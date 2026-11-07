"""Compile DESLab's TeX drawings to PDF with the included offline engine.

``compile_pdf`` describes the export steps. The helpers below it handle the
packaged resources, the isolated working directory, and the engine's memory API.
"""

from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import zipfile

from deslab_portable.src.exceptions import deslabError

# Older Python versions and native rendering do not require this dependency.
# Importing it here does not compile the engine or extract the TeX resources.
try:
    import wasmtime
except ImportError:
    wasmtime = None


_ASSET_ROOT = Path(__file__).with_name('_tex_assets')
_LOG_FILES = ('stdout.log', 'stderr.log')
# Bound each compilation's memory and work without changing drawing quality.
_MAX_MEMORY_BYTES = 1024 * 1024 * 1024  # 1 GiB
_MAX_INSTRUCTIONS = 500_000_000_000


def compile_pdf(source, destination):
    """Compile a local TeX file and save its PDF, without network or commands."""
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_file():
        raise deslabError('The TeX source does not exist: ' + str(source))
    if source == destination:
        raise deslabError('PDF destination must differ from the TeX source')

    engine, module, resources = _compiler()
    with tempfile.TemporaryDirectory(prefix='deslab-tex-') as temporary:
        workspace = Path(temporary)
        try:
            # Each document has its own engine state, output, cache, and logs.
            store, exports = _create_session(engine, module, resources, source, workspace)
            _run_compiler(store, exports, source.name)

            # Reject missing symbols or invalid output before replacing any PDF.
            _check_missing_characters(workspace)
            generated = workspace / 'output' / (source.stem + '.pdf')
            data = generated.read_bytes()
            if not data.startswith(b'%PDF-'):
                raise ValueError('The compiler did not produce a PDF')
        except (wasmtime.WasmtimeError, wasmtime.Trap, OSError, ValueError,
                KeyError, MemoryError) as error:
            raise deslabError(
                'Portable TeX compilation failed. ' + str(error) + '\n'
                + _read_compiler_logs(workspace) + '\n'
                'The offline bundle supports DESLab drawing styles and core '
                'mathematical fonts. For additional TeX packages, configure '
                'native rendering with use_native_draw().'
            ) from error

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    return str(destination)


# Compiling the engine and extracting TeX files is expensive. Reuse this one
# prepared compiler across drawings; keep the temporary resources alive with it.
# Document state is NOT cached: _create_session creates it anew for every PDF.
@lru_cache(maxsize=1)
def _compiler():
    """Verify and prepare the included engine and TeX files once per process."""
    if sys.version_info < (3, 11):
        raise deslabError('Portable PDF export requires Python 3.11+. '
                          'Use Python 3.11+ or configure native rendering.')
    if wasmtime is None:
        raise deslabError('Portable PDF export requires the Wasmtime dependency '
                          'installed with DESlab. Reinstall DESlab.')

    try:
        manifest = json.loads((_ASSET_ROOT / 'manifest.json').read_text(encoding='utf-8'))
        for name, metadata in manifest['files'].items():
            path = _ASSET_ROOT / name
            if hashlib.sha256(path.read_bytes()).hexdigest() != metadata['sha256']:
                raise ValueError('Asset checksum differs: ' + name)

        resources = tempfile.TemporaryDirectory(prefix='deslab-tex-resources-')
        with zipfile.ZipFile(_ASSET_ROOT / 'resources.zip') as archive:
            # All bundled files belong directly in the resource directory.
            if any(Path(name).name != name or '\\' in name for name in archive.namelist()):
                raise ValueError('Invalid bundled resource filename')
            archive.extractall(resources.name)

        config = wasmtime.Config()
        config.consume_fuel = True  # Enable the per-document instruction limit.
        engine = wasmtime.Engine(config)
        module = wasmtime.Module.from_file(engine, str(_ASSET_ROOT / 'tectonic.wasm'))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, wasmtime.WasmtimeError) as error:
        raise deslabError('The bundled portable TeX resources are missing or invalid. '
                          'Reinstall DESlab. ' + str(error)) from error
    return engine, module, resources


def _create_session(engine, module, resources, source, workspace):
    """Give one document access to its input, bundled files, and temporary output."""
    store = wasmtime.Store(engine)
    store.set_fuel(_MAX_INSTRUCTIONS)
    store.set_limits(memory_size=_MAX_MEMORY_BYTES)
    wasi = wasmtime.WasiConfig()

    # Paths on the right exist only inside the engine. Inputs are read-only;
    # generated files stay in this document's temporary working directory.
    for name in ('output', 'cache', 'fonts'):
        directory = workspace / name
        directory.mkdir()
        wasi.preopen_dir(str(directory), '/' + name, fs_mutable=name != 'fonts')
    wasi.preopen_dir(resources.name, '/bundle', fs_mutable=False)
    wasi.preopen_dir(str(source.parent), '/input', fs_mutable=False)

    # Drawings normally use today's date. A fixed timestamp allows repeatable
    # exports for comparisons (SOURCE_DATE_EPOCH is an optional convention).
    epoch = os.environ.get('SOURCE_DATE_EPOCH', str(int(time.time())))
    try:
        epoch = str(max(0, int(epoch)))
    except ValueError as error:
        raise ValueError('SOURCE_DATE_EPOCH must be an integer timestamp') from error
    wasi.env = [('TECTONIC_FONT_DIR', '/fonts'), ('TECTONIC_CACHE_DIR', '/cache'),
                ('SOURCE_DATE_EPOCH', epoch)]
    wasi.stdout_file = str(workspace / 'stdout.log')
    wasi.stderr_file = str(workspace / 'stderr.log')
    store.set_wasi(wasi)

    linker = wasmtime.Linker(engine)
    linker.define_wasi()
    instance = linker.instantiate(store, module)
    return store, instance.exports(store)


def _run_compiler(store, exports, source_name):
    """Pass input/output paths to the engine using its version 2 memory API."""
    if exports['tectonic_abi_version'](store) != 2:
        raise ValueError('Unsupported bundled Tectonic host ABI')

    # The engine cannot read Python strings directly. Copy each UTF-8 path into
    # its memory, then pass the memory address and byte count to tectonic_compile.
    paths = ('/input/' + source_name, '/output', '/bundle')
    arguments, allocated_pointers = [], []
    try:
        for path in paths:
            data = path.encode('utf-8')
            pointer = exports['malloc'](store, len(data))
            if not pointer:
                raise MemoryError('Could not allocate WASI input')
            allocated_pointers.append(pointer)
            exports['memory'].write(store, data, pointer)
            arguments.extend((pointer, len(data)))

        status = exports['tectonic_compile'](store, *arguments)
        if status:
            raise ValueError('Tectonic returned status ' + str(status))
    finally:
        # Release every copied path, even when compilation fails.
        for pointer in allocated_pointers:
            exports['free'](store, pointer)


def _check_missing_characters(workspace):
    """Fail if a font cannot display a character, rather than lose PDF content."""
    for name in _LOG_FILES:
        path = workspace / name
        if not path.exists():
            continue
        with path.open(encoding='utf-8', errors='replace') as stream:
            for line in stream:
                if 'Missing character:' in line:
                    # The TikZ converter emits an extra semicolon in nullfont;
                    # this harmless warning also occurs with native pdfLaTeX.
                    if 'There is no ; (' in line and 'font nullfont!' in line:
                        continue
                    raise ValueError(line.strip())


def _read_compiler_logs(workspace):
    """Read the end of each log to include useful details in compilation errors."""
    parts = []
    for name in _LOG_FILES:
        path = workspace / name
        if path.exists():
            # Read at most 8 KB per log, even when a failed compilation is noisy.
            with path.open('rb') as stream:
                stream.seek(0, 2)
                stream.seek(max(0, stream.tell() - 8000))
                parts.append(stream.read().decode('utf-8', errors='replace'))
    return '\n'.join(parts)
