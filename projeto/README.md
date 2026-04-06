# The Typist - Projeto da Fase WebMAC

Neste diretório temos o projeto da primeira fase da disciplina, o site de digitação **The Typist**, onde o usuário tenta digitar palavras aleatórias o mais rápido possível.

## Estrutura do Repositório

### Backend

Aqui, temos nosso servidor em fastapi e a interação com o banco de dados em SQLite. As componentes são:
- `main.py` - script do **servidor** com os endpoints
- `db/` - diretório com os **modelos** do BD (`models.py`) e 4 outros scripts, um para cada operação CRUD, com funções de **interação com o BD**
- `utils/` - diretório com **funções utilitárias** usadas nas consultas com o BD e pelas funções dos endpoints em si

#### Banco de dados
O BD é o arquivo `projeto.db` gerado ao rodar o servidor pela primeira vez

Vale notar que o banco de dados possui 2 tabelas, um para usuários registrados, e outro para tentativas realizadas

### Frontend

Utilizamos HTML, CSS, JS e HTMX na construção das páginas. Tais páginas são servidas como templates do `Jinja2` pelo servidor. Os diretórios são:
- `templates/` - arquivos **HTML**, organizados pelo seu nível de atomicidade
- `static/` - contém o **CSS** e o **JS** do site, incluindo uma versão local mínima do HTMX

## Setup

Para instalar as dependências, basta instalar os requerimentos especificados em `requirements.txt`. Para isso, estando na raiz do projeto, faça:

```bash
pip install -r requirements.txt
```

A partir disso, é possível iniciar o servidor:

```bash
fastapi dev
```

De modo que o site passe a ser acessível no seu localhost (`127.0.0.1:8000` por padrão)

## Disclaimer sobre IA

No frontend, utilizei IA generativa para encontrar uma paleta de cores a ser utilizada nos estilos que seguisse o que eu queria, e também para auxiliar em tornar algumas telas responsivas, que acabou não envolvendo tanto trabalho assim, pelos layouts do site serem razoavelmente simples

No backend, não houve uso direto além de um direcionamento geral de estudos sobre temas com os quais não estava habituado, tais como bibliotecas de python para hashing/criptografia de senhas