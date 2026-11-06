"""Offline TeX export using the bundled Tectonic WASI artifact (host ABI 2)."""

from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import zipfile

from deslab.src.exceptions import deslabError


_ASSET_ROOT = Path(__file__).with_name('_tex_assets')


@lru_cache(maxsize=1)
def _compiler():
    if sys.version_info < (3, 11):
        raise deslabError('Portable PDF export requires Python 3.11+. '
                          'Use Python 3.11+ or configure native rendering.')
    try:
        import wasmtime
    except ImportError as error:
        raise deslabError('Portable PDF export requires the Wasmtime dependency '
                          'installed with DESlab. Reinstall DESlab.') from error
    try:
        manifest = json.loads((_ASSET_ROOT / 'manifest.json').read_text(encoding='utf-8'))
        for name, metadata in manifest['files'].items():
            path = _ASSET_ROOT / name
            if hashlib.sha256(path.read_bytes()).hexdigest() != metadata['sha256']:
                raise ValueError('Asset checksum differs: ' + name)
        resources = tempfile.TemporaryDirectory(prefix='deslab-tex-resources-')
        with zipfile.ZipFile(_ASSET_ROOT / 'resources.zip') as archive:
            if any(Path(name).name != name or '\\' in name for name in archive.namelist()):
                raise ValueError('Invalid bundled resource filename')
            archive.extractall(resources.name)
        config = wasmtime.Config()
        config.consume_fuel = True
        engine = wasmtime.Engine(config)
        module = wasmtime.Module.from_file(engine, str(_ASSET_ROOT / 'tectonic.wasm'))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, wasmtime.WasmtimeError) as error:
        raise deslabError('The bundled portable TeX resources are missing or invalid. '
                          'Reinstall DESlab. ' + str(error)) from error
    # Keep the extracted resources alive until this cached compiler is released.
    return wasmtime, engine, module, resources


def _diagnostics(workspace):
    parts = []
    for name in ('stdout.log', 'stderr.log'):
        path = workspace / name
        if path.exists():
            # Keep actionable compiler output without reading an unbounded log.
            with path.open('rb') as stream:
                stream.seek(0, 2)
                stream.seek(max(0, stream.tell() - 8000))
                parts.append(stream.read().decode('utf-8', errors='replace'))
    return '\n'.join(parts)


def _check_glyphs(workspace):
    for name in ('stdout.log', 'stderr.log'):
        path = workspace / name
        if not path.exists():
            continue
        with path.open(encoding='utf-8', errors='replace') as stream:
            for line in stream:
                if 'Missing character:' in line:
                    # The legacy TikZ converter emits an extra semicolon in
                    # nullfont; it also occurs with the reference pdfLaTeX.
                    if 'There is no ; (' in line and 'font nullfont!' in line:
                        continue
                    raise ValueError(line.strip())


def compile_pdf(source, destination):
    """Compile with local packaged resources; no native compiler or network use."""
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_file():
        raise deslabError('The TeX source does not exist: ' + str(source))
    if source == destination:
        raise deslabError('PDF destination must differ from the TeX source')
    runtime, engine, module, resources = _compiler()
    with tempfile.TemporaryDirectory(prefix='deslab-tex-') as temporary:
        workspace = Path(temporary)
        store = runtime.Store(engine)
        store.set_fuel(500_000_000_000)
        store.set_limits(memory_size=1024 * 1024 * 1024)
        wasi = runtime.WasiConfig()
        for name in ('output', 'cache', 'fonts'):
            (workspace / name).mkdir()
            wasi.preopen_dir(str(workspace / name), '/' + name, fs_mutable=name != 'fonts')
        wasi.preopen_dir(resources.name, '/bundle', fs_mutable=False)
        wasi.preopen_dir(str(source.parent), '/input', fs_mutable=False)
        # A fixed source date is optional; normal drawings use the current date.
        epoch = os.environ.get('SOURCE_DATE_EPOCH', str(int(time.time())))
        try:
            epoch = str(max(0, int(epoch)))
        except ValueError as error:
            raise deslabError('SOURCE_DATE_EPOCH must be an integer timestamp') from error
        wasi.env = [('TECTONIC_FONT_DIR', '/fonts'), ('TECTONIC_CACHE_DIR', '/cache'),
                    ('SOURCE_DATE_EPOCH', epoch)]
        wasi.stdout_file = str(workspace / 'stdout.log')
        wasi.stderr_file = str(workspace / 'stderr.log')
        store.set_wasi(wasi)
        linker = runtime.Linker(engine)
        linker.define_wasi()
        try:
            instance = linker.instantiate(store, module)
            exports = instance.exports(store)
            if exports['tectonic_abi_version'](store) != 2:
                raise ValueError('Unsupported bundled Tectonic host ABI')
            arguments, pointers = [], []
            try:
                for text in ('/input/' + source.name, '/output', '/bundle'):
                    data = text.encode('utf-8')
                    pointer = exports['malloc'](store, len(data))
                    if not pointer:
                        raise MemoryError('Could not allocate WASI input')
                    pointers.append(pointer)
                    exports['memory'].write(store, data, pointer)
                    arguments.extend((pointer, len(data)))
                status = exports['tectonic_compile'](store, *arguments)
                if status:
                    raise ValueError('Tectonic returned status ' + str(status))
            finally:
                for pointer in pointers:
                    exports['free'](store, pointer)
            _check_glyphs(workspace)
            generated = workspace / 'output' / (source.stem + '.pdf')
            data = generated.read_bytes()
            if not data.startswith(b'%PDF-'):
                raise ValueError('The compiler did not produce a PDF')
        except (runtime.WasmtimeError, runtime.Trap, OSError, ValueError, KeyError,
                MemoryError) as error:
            raise deslabError('Portable TeX compilation failed. ' + str(error) + '\n'
                              + _diagnostics(workspace) + '\n'
                              'The offline bundle supports DESLab drawing styles and core '
                              'mathematical fonts. For additional TeX packages, configure '
                              'native rendering with use_native_draw().') from error
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    return str(destination)
