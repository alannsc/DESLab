# DESLab

Biblioteca Python para sistemas a eventos discretos modelados por autômatos, com operações de linguagens, controle supervisório, diagnóstico e opacidade.

## Instalação

Use Python 3.8 ou superior. Na pasta do repositório, execute:

```sh
python -m pip install .
```

Se recebeu um arquivo `.whl`, instale o arquivo recebido:

```sh
python -m pip install caminho/arquivo.whl
```

Execute a instalação com o mesmo Python usado pelos seus scripts ou notebooks. As dependências Python são instaladas automaticamente.

Para gerar PDFs, instale também Graphviz e LaTeX conforme seu sistema.

### macOS

Com o [Homebrew](https://brew.sh/) instalado:

```sh
brew install graphviz
brew install --cask basictex
```

Feche e reabra o terminal. Depois, instale os pacotes LaTeX necessários:

```sh
sudo tlmgr update --self
sudo tlmgr install beamer pgf lm
```

### Linux — Ubuntu e Debian

```sh
sudo apt update
sudo apt install graphviz texlive-latex-extra texlive-fonts-recommended lmodern
```

### Windows

Instale [Graphviz](https://graphviz.org/download/) e [MiKTeX](https://miktex.org/download), habilitando os comandos no PATH. No MiKTeX Console, instale `beamer`, `pgf` e `lm`, ou habilite a instalação de pacotes ausentes. Abra um novo terminal após a instalação.

Em qualquer sistema, confira se os comandos estão disponíveis:

```sh
dot -V
pdflatex --version
```

## Uso

```python
from deslab import fsa, draw

G = fsa(
    ['q0', 'q1'], ['a'], [('q0', 'a', 'q1')],
    ['q0'], ['q1'], name='Exemplo',
)

draw(G, 'figure', output='resultado.pdf', show=False)
```

`output` define onde salvar o PDF. Use `show=False` para salvar sem abrir um visualizador; o padrão é abrir o arquivo gerado.

Os estilos disponíveis são `figure`, `figurecolor` e `beamer`. Use `save_file=True` para salvar também o arquivo `Figure.tex`.
