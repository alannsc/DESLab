# DESLab

Biblioteca Python para sistemas a eventos discretos modelados por autômatos, com operações de linguagens, controle supervisório, diagnóstico e opacidade.

## Instalação

Use Python 3.11 ou superior. Instale a partir da pasta do repositório.

No Windows, você pode usar o [instalador do Python 3.12](programas/python-3.12.0-amd64.exe) disponível em `programas`. Marque **Add Python to PATH** durante a instalação e abra um novo terminal. Se o comando `python` não for reconhecido, veja [como configurar o PATH](#configurar-o-path-no-windows). Depois, execute na pasta do repositório:

```bat
python -m pip install .
```

No macOS ou Linux:

```sh
python3 -m pip install .
```

Se recebeu um arquivo `.whl`, substitua `.` pelo caminho do arquivo nos comandos acima. Use o mesmo Python dos seus scripts ou notebooks. As dependências necessárias para os cálculos e a geração de PDFs são instaladas automaticamente.

Para Python 3.8, 3.9 ou 3.10, siga a seção [Compatibilidade com Python antigo e estrutura anterior](#compatibilidade-com-python-antigo-e-estrutura-anterior) antes de executar os exemplos.

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

## Compatibilidade com Python antigo e estrutura anterior

Use esta seção somente se estiver usando Python 3.8, 3.9 ou 3.10, ou se quiser usar as engines nativas de renderização, como nas versões anteriores do DESLab.

Com Python 3.11 ou superior, a renderização padrão de `draw()` já inclui as dependências necessárias. Basta seguir a instalação e os exemplos acima.

Para usar a renderização nativa, instale Graphviz e TeX Live conforme seu sistema:

### Windows

Use os instaladores que já estão na pasta `programas`:

1. Instale o [Graphviz 2.28](programas/graphviz-2.28.0.msi).
2. Instale o [TeX Live](programas/TEXLIVE-install-tl-windows.exe), mantendo a seleção completa de pacotes do instalador.
3. Siga as instruções de [configuração do PATH](#configurar-o-path-no-windows) para adicionar as pastas do Graphviz e do TeX Live.

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

### Verificar a instalação

Em qualquer sistema, confira se os dois comandos estão disponíveis:

```sh
dot -V
pdflatex --version
```

### Selecionar a renderização de draw()

Antes de desenhar, ative a renderização nativa. A chamada verifica se `dot` e `pdflatex` estão disponíveis no PATH:

```python
from deslab import use_native_draw

use_native_draw()
draw(G1, 'figure', output='G1.pdf', show=False)
```

Para voltar à renderização padrão, com Python 3.11 ou superior:

```python
from deslab import use_default_draw

use_default_draw()
```

A escolha vale para as próximas chamadas de `draw()` na mesma execução.

## Configurar o PATH no Windows

O PATH permite executar os programas pelo nome no terminal, sem informar o caminho completo.

1. Abra o **Painel de Controle → Sistema → Configurações avançadas do sistema**.
2. Na aba **Avançado**, clique em **Variáveis de Ambiente**.
3. Em **Variáveis de usuário**, selecione **Path** e clique em **Editar**.
4. Clique em **Novo** e adicione a pasta de cada programa necessário, uma por entrada, preservando as entradas existentes:

| Programa | Pasta a adicionar |
| --- | --- |
| Python | A pasta que contém `python.exe`, por exemplo, `C:\Users\SeuUsuario\AppData\Local\Programs\Python\Python312\`. |
| Graphviz | A pasta `bin` que contém `dot.exe`, por exemplo, `C:\Program Files (x86)\Graphviz2.28\bin\`. |
| TeX Live | A pasta que contém `pdflatex.exe`, dentro de `C:\texlive\<ano>\bin\`. Dependendo da versão instalada, a subpasta pode se chamar `windows` ou `win32`. |

Os caminhos variam conforme a instalação. Adicione a **pasta**, sem o nome do executável: `C:\...\Python312\`, e não `C:\...\Python312\python.exe`.

Na instalação padrão, basta configurar o Python. Graphviz e TeX Live só precisam estar no PATH se você escolher a renderização nativa.

Confirme as janelas com **OK** e feche e reabra o terminal ou o programa em que executa seus scripts. Confira o Python selecionado:

```bat
python --version
where python
```

Se houver mais de uma versão do Python no PATH, coloque a pasta da versão que deseja usar antes das outras entradas de Python.
