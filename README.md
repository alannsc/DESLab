# DESLab

Biblioteca Python para sistemas a eventos discretos modelados por autômatos: operações de linguagens, controle supervisório, diagnóstico, opacidade e intervalos temporais.

## Requisitos

- Python 3.8 ou superior.
- Para gerar PDFs: Graphviz e uma distribuição LaTeX com pdfLaTeX, Beamer, PGF/TikZ e Latin Modern.

Os cálculos não precisam dos programas de desenho. As dependências Python são instaladas automaticamente pelo pip. Não é necessário Docker.

## macOS

Instale o [Python](https://www.python.org/downloads/macos/) e o [Homebrew](https://brew.sh/) caso ainda não estejam disponíveis. Depois:

```sh
brew install graphviz
brew install --cask basictex
```

Feche e reabra o terminal para disponibilizar os comandos do BasicTeX. Instale os pacotes usados nos desenhos:

```sh
sudo tlmgr update --self
sudo tlmgr install beamer pgf lm
```

Confira os programas:

```sh
python3 --version
dot -V
pdflatex --version
```

## Linux (Ubuntu e Debian)

```sh
sudo apt update
sudo apt install python3 python3-pip python3-venv graphviz texlive-latex-extra texlive-fonts-recommended lmodern
```

Confira os programas:

```sh
python3 --version
dot -V
pdflatex --version
```

Em outras distribuições, instale os pacotes equivalentes usando o gerenciador do sistema.

## Windows

Instale o [Python](https://www.python.org/downloads/windows/), o [Graphviz](https://graphviz.org/download/) e o [MiKTeX](https://miktex.org/download). Nas opções dos instaladores, habilite a disponibilização dos comandos no PATH. No MiKTeX Console, instale `beamer`, `pgf` e `lm`, ou habilite a instalação dos pacotes ausentes.

Abra um novo terminal e confira:

```bat
python --version
dot -V
pdflatex --version
```

## Instalar a biblioteca

Na pasta deste repositório, crie um ambiente virtual. No macOS ou Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

No Windows, usando o Prompt de Comando:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install .
```

Se já usa um ambiente Python ou notebook, instale o DESLab nesse ambiente. O ambiente virtual apenas isola dependências; a biblioteca continua sendo usada por `import`.

Com o ambiente ativo, `sh Install.sh` (macOS/Linux) ou `Install.bat` (Windows) são alternativas para instalar o pacote. Esses scripts instalam as dependências Python; os programas de desenho seguem as instruções acima.

Se receber um wheel pronto, instale-o no lugar do checkout:

```sh
python -m pip install /caminho/para/deslab-0.0.5.dev0-py3-none-any.whl
```

Não é necessário clonar o repositório para usar um wheel. Esta versão de desenvolvimento ainda não foi publicada por esta alteração.

## Usar

```python
from deslab import fsa, draw

G = fsa(
    ['q0', 'q1'], ['a'], [('q0', 'a', 'q1')],
    ['q0'], ['q1'], name='Exemplo',
)

pdf = draw(G, 'figure', output='resultados/exemplo.pdf', show=False)
print(pdf)
```

`show=False` salva o PDF sem abrir um aplicativo. O padrão `show=True` usa o visualizador do sistema. O resultado permanece no destino escolhido; os arquivos intermediários usam uma pasta temporária. Caminhos com espaços são aceitos.

Continuam disponíveis `from deslab import *`, os estilos `figure`, `figurecolor` e `beamer`, e a opção `save_file=True` para salvar também `Figure.tex` na pasta atual. O desenho usa Graphviz, o conversor TikZ existente e pdfLaTeX, preservando a saída vetorial.

## Problemas comuns

- **`dot` ou `pdflatex` não encontrado:** confirme a instalação e abra um novo terminal. O comando correspondente precisa funcionar nesse terminal antes de iniciar o Python ou notebook.
- **Pacote LaTeX ausente:** instale os pacotes indicados acima; a mensagem de erro inclui o trecho final do log do compilador.
- **Sem interface gráfica:** use `draw(..., show=False)`.

Esta alteração cuida de instalação, caminhos e integração entre sistemas. Ela não representa uma revisão matemática dos algoritmos científicos.
