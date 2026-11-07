"""Choose the renderer once per Python process; default engines are included."""

import shutil
import threading

from deslab_portable.src.exceptions import deslabError


_render_lock = threading.RLock()
_mode = 'default'


def get_draw_mode():
    """Return the selected draw mode: ``default`` or ``native``."""
    return _mode


def use_native_draw():
    """Use installed Graphviz and pdfLaTeX, after checking both on PATH."""
    global _mode
    with _render_lock:
        missing = [name for name in ('dot', 'pdflatex') if shutil.which(name) is None]
        if missing:
            raise deslabError('Native rendering requires executable commands on PATH: '
                              + ', '.join(missing) + '. See the native installation '
                              'instructions in README.md.')
        _mode = 'native'


def use_default_draw():
    """Use the Graphviz and TeX engines installed with DESlab (the default)."""
    global _mode
    with _render_lock:
        _mode = 'default'
