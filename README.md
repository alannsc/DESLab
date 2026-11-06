# DESLab

Biblioteca Python para sistemas a eventos discretos modelados por autômatos, com operações de linguagens, controle supervisório, diagnóstico e opacidade.

## Instalação

Use Python 3.8 ou superior. Instale a partir da pasta do repositório.

No macOS ou Linux:

```sh
python3 -m pip install .
```

No Windows, você pode usar o [instalador do Python 3.12](programas/python-3.12.0-amd64.exe) disponível em `programas`. Marque **Add Python to PATH** durante a instalação e abra um novo terminal. Depois, execute na pasta do repositório:

```bat
python -m pip install .
```

Se recebeu um arquivo `.whl`, substitua `.` pelo caminho do arquivo nos comandos acima. Use o mesmo Python dos seus scripts ou notebooks. As dependências Python são instaladas automaticamente.

Para gerar PDFs, instale também Graphviz e TeX Live conforme as instruções abaixo.

## Exemplos

### Criar e desenhar um autômato

Este exemplo define três estados, três eventos, um estado inicial e dois estados marcados. A tabela associa os estados e eventos aos rótulos exibidos no desenho.

```python
from deslab import *

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

### Salvar o PDF

Usando o mesmo autômato, salve uma versão colorida sem abrir o visualizador:

```python
draw(G1, 'figurecolor', output='G1.pdf', show=False)
```

`output` define onde salvar o PDF. Por padrão, `draw()` abre o arquivo gerado. Os estilos disponíveis são `figure`, `figurecolor` e `beamer`. Use `save_file=True` para salvar também o arquivo `Figure.tex`.

## Dependências para gerar PDFs

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

Use os instaladores que já estão na pasta `programas`:

1. Instale o [Graphviz 2.28](programas/graphviz-2.28.0.msi).
2. Instale o [TeX Live](programas/TEXLIVE-install-tl-windows.exe), mantendo a seleção completa de pacotes do instalador.
3. Em **Configurações avançadas do sistema → Variáveis de Ambiente**, edite o **Path** do seu usuário. Adicione a pasta `bin` do Graphviz, que contém `dot.exe`, e a pasta do TeX Live que contém `pdflatex.exe`. Adicione as pastas, sem o nome dos executáveis.
4. Feche e reabra o terminal.

### Verificar a instalação

Em qualquer sistema, confira se os dois comandos estão disponíveis:

```sh
dot -V
pdflatex --version
```
