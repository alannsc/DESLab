# DESLab Portable

A Python library for discrete event systems modeled as automata, with language operations, supervisory control, diagnosis, and opacity analysis.

Evaluation build of the DESLab update. The temporary `deslab_portable` import lets you test it alongside `deslab` in the same Python installation.

## Installation

Use Python 3.11 or later. Run the installation command from the repository directory.

On Windows, you can use the [Python 3.12 installer](programas/python-3.12.0-amd64.exe) in `programas`. Select **Add Python to PATH** during installation and open a new terminal. If the `python` command is not recognized, see [how to configure PATH](#configure-path-on-windows). Then run this command from the repository directory:

```bat
python -m pip install .
```

On macOS or Linux:

```sh
python3 -m pip install .
```

If you received a `.whl` file, replace `.` with its path in the commands above. Use the same Python installation as your scripts or notebooks. The dependencies needed for calculations and PDF generation are installed automatically.

For Python 3.8, 3.9, or 3.10, follow [Compatibility with older Python versions and the previous setup](#compatibility-with-older-python-versions-and-the-previous-setup) before running the examples.

## Examples

### Create and draw an automaton

This example defines three states, three events, one initial state, and two marked states. The table maps states and events to the labels displayed in the drawing.

```python
from deslab_portable import *

syms('q1 q2 q3 a1 b1 e')

table = [
    (a1, r'\alpha_1'), (b1, r'\beta_1'),
    (q1, 'q_1'), (q2, 'q_2'), (q3, 'q_3'),
]
X = [q1, q2, q3]
Sigma = [a1, b1, e]
X0 = [q1]
Xm = [q1, q3]
T = [
    (q1, b1, q2),
    (q2, b1, q3),
    (q2, e, q3),
    (q3, a1, q1),
    (q2, a1, q2),
]

G1 = fsa(X, Sigma, T, X0, Xm, table, name='$G_1$ -- example 1')
draw(G1)
```

### Save the PDF

Using the same automaton, save a color version without opening the PDF viewer:

```python
draw(G1, 'figurecolor', output='G1.pdf', show=False)
```

`output` sets the PDF destination. By default, `draw()` opens the generated file. Available styles are `figure`, `figurecolor`, and `beamer`. Use `save_file=True` to also save the `Figure.tex` file.

### Compare the two versions

The packages use separate names, so you can import both:

```python
import deslab
import deslab_portable
```

Build each version's models with its own `fsa()` constructor. To test an existing `.des` model, use `deslab_portable.load()`; it loads the model into the portable version.

## Compatibility with older Python versions and the previous setup

Use this section only if you are running Python 3.8, 3.9, or 3.10, or if you want to use native rendering engines as in earlier DESLab versions.

With Python 3.11 or later, the default rendering mode of `draw()` already includes the required dependencies. Follow the installation instructions and examples above.

To use native rendering, install Graphviz and TeX Live for your operating system:

### Windows

Use the installers in the `programas` directory:

1. Install [Graphviz 2.28](programas/graphviz-2.28.0.msi).
2. Install [TeX Live](programas/TEXLIVE-install-tl-windows.exe), keeping the installer's full package selection.
3. Follow the [PATH configuration instructions](#configure-path-on-windows) to add the Graphviz and TeX Live directories.

### macOS

With [Homebrew](https://brew.sh/) installed:

```sh
brew install graphviz
brew install --cask basictex
```

Close and reopen the terminal. Then install the required LaTeX packages:

```sh
sudo tlmgr update --self
sudo tlmgr install beamer pgf lm
```

### Linux — Ubuntu and Debian

```sh
sudo apt update
sudo apt install graphviz texlive-latex-extra texlive-fonts-recommended lmodern
```

### Verify the installation

On any operating system, check that both commands are available:

```sh
dot -V
pdflatex --version
```

### Select the rendering mode for draw()

Before drawing, enable native rendering. This call checks that `dot` and `pdflatex` are available on PATH:

```python
from deslab_portable import use_native_draw

use_native_draw()
draw(G1, 'figure', output='G1.pdf', show=False)
```

To return to default rendering on Python 3.11 or later:

```python
from deslab_portable import use_default_draw

use_default_draw()
```

The selected mode applies to subsequent `draw()` calls in the same Python session.

## Configure PATH on Windows

PATH lets you run programs by name in the terminal without entering their full paths.

1. Open **Control Panel → System → Advanced system settings**.
2. In the **Advanced** tab, click **Environment Variables**.
3. Under **User variables**, select **Path** and click **Edit**.
4. Click **New** and add the directory for each required program, one per entry, keeping the existing entries:

| Program | Directory to add |
| --- | --- |
| Python | The directory containing `python.exe`, for example, `C:\Users\YourUser\AppData\Local\Programs\Python\Python312\`. |
| Graphviz | The `bin` directory containing `dot.exe`, for example, `C:\Program Files (x86)\Graphviz2.28\bin\`. |
| TeX Live | The directory containing `pdflatex.exe` under `C:\texlive\<year>\bin\`. Depending on the installed version, the subdirectory may be named `windows` or `win32`. |

Paths depend on your installation. Add the **directory**, without the executable name: `C:\...\Python312\`, rather than `C:\...\Python312\python.exe`.

For the default installation, only Python needs to be on PATH. Graphviz and TeX Live are needed on PATH only if you choose native rendering.

Click **OK** to confirm the changes, then close and reopen the terminal or application where you run your scripts. Check the selected Python installation:

```bat
python --version
where python
```

If PATH contains more than one Python version, place the directory of the version you want to use before the other Python entries.
