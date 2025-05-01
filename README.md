# Hackathon App

Este é um aplicativo web simples construído com Flask, projetado para facilitar a organização e participação em hackathons ou sessões de perguntas e respostas interativas. Ele permite que administradores criem salas, adicionem perguntas e visualizem as respostas dos participantes, enquanto os participantes podem ingressar em salas com um código e submeter suas respostas.

## Funcionalidades Principais

**Para Administradores:**

* **Login Seguro:** Área de login protegida por senha para administradores.
* **Dashboard:** Visão geral das salas criadas.
* **Criação de Salas:** Crie novas salas com um nome e um código único gerado automaticamente.
* **Gerenciamento de Salas:** Adicione e remova perguntas para salas específicas.
* **Ativar/Desativar Salas:** Controle a participação ativando ou desativando salas.
* **Visualização de Resultados:** Veja todos os participantes de uma sala e suas respostas submetidas. (Nota: Um sistema de pontuação pode ser adicionado no futuro).

**Para Participantes:**

* **Página de Entrada Intuitiva:** Uma landing page com design futurista.
* **Entrar em Salas:** Junte-se a uma sala usando um código fornecido pelo administrador.
* **Responder Perguntas:** Visualize as perguntas em uma sala ativa e submeta suas respostas.

## Tecnologias Utilizadas

* **Backend:** Flask (Python)
* **Banco de Dados:** SQLAlchemy ORM (com suporte para MySQL ou SQLite, configurável via `DATABASE_URL`)
* **Gerenciamento de Formulários:** Flask-WTF
* **Autenticação:** Flask-Login
* **Interface:** HTML, CSS
* **(Potencial Futuro):** Flask-SocketIO para funcionalidades em tempo real, Flask-Migrate para gerenciar o esquema do banco de dados.

## Instalação e Configuração

(Aqui você adicionaria instruções sobre como clonar o repositório, configurar o ambiente virtual, instalar dependências (`pip install -r requirements.txt`), configurar o banco de dados (`.env` com `DATABASE_URL`) e rodar a aplicação).

## Como Usar

(Explique como o administrador cria uma sala, obtém o código, e como o participante usa o código para entrar na sala e responder.)

## Licença

(Espaço para a informação da licença - veja a recomendação abaixo)
