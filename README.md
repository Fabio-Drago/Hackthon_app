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

## Instalação e Execução Local

Siga estes passos para configurar e executar o projeto localmente.

### Pré-requisitos

* Python 3.6+
* Git
* (Opcional, se for usar MySQL) Um servidor MySQL rodando e as credenciais de acesso.

### Configuração

1.  **Clone o Repositório:**

    Abra seu terminal e clone o repositório do GitHub:

    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    ```

    Substitua `<URL_DO_SEU_REPOSITORIO>` pelo endereço real do seu repositório no GitHub.

2.  **Navegue até o Diretório do Projeto:**

    Entre na pasta clonada:

    ```bash
    cd hackathon_app
    ```

3.  **Crie e Ative o Ambiente Virtual:**

    É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.

    * **No Windows:**

        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

    * **No macOS e Linux:**

        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

    Você verá o nome do ambiente virtual (`venv`) no início da linha do seu terminal, indicando que ele está ativo.

4.  **Instale as Dependências:**

    Com o ambiente virtual ativo, instale as bibliotecas necessárias listadas no `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

5.  **Configuração do Banco de Dados:**

    A aplicação usa o SQLAlchemy para interagir com o banco de dados e lê a string de conexão da variável de ambiente `DATABASE_URL`, configurada no arquivo `.env`.

    * Crie um arquivo na raiz do projeto chamado `.env`.
    * Edite o arquivo `.env` e adicione a sua string de conexão do banco de dados no formato `DATABASE_URL="..."`.

    **Exemplo para MySQL:**

    ```dotenv
    SECRET_KEY='sua_chave_secreta_aqui'
    DATABASE_URL="mysql+pymysql://seu_usuario:sua_senha@seu_host:sua_porta/hackton"
    ```
    Substitua `seu_usuario`, `sua_senha`, `seu_host`, `sua_porta` (geralmente 3306) com as suas credenciais do MySQL.
    **Importante:** Certifique-se de que o banco de dados chamado `hackton` já existe no seu servidor MySQL e que o `seu_usuario` tem permissões para criar tabelas nele. (Consulte as instruções anteriores sobre como criar o banco de dados MySQL manualmente se ainda não o fez).

    **Exemplo para SQLite (para teste rápido, não recomendado para produção):**

    ```dotenv
    SECRET_KEY='sua_chave_secreta_aqui'
    DATABASE_URL="sqlite:///app.db"
    ```
    Neste caso, um arquivo `app.db` será criado na raiz do projeto.

    **Não se esqueça de definir uma `SECRET_KEY` forte e única!**

6.  **Inicialize o Banco de Dados (Crie as Tabelas):**

    Na primeira vez que você rodar a aplicação, as tabelas do banco de dados precisam ser criadas.

    * Abra o arquivo `app.py`.
    * Localize o bloco `with app.app_context():`.
    * **Descomente** a linha `db.create_all()` dentro deste bloco.

        ```python
        with app.app_context():
            # Comentar após a primeira execução ou usar Flask-Migrate
            db.create_all() # <--- Descomente esta linha na primeira vez
            print("Verifique se as tabelas foram criadas no banco de dados 'Hackton'.")
            # ... (código para criar admin inicial)
        ```

    * Rode a aplicação uma vez para que as tabelas sejam criadas (veja o próximo passo).
    * **Após a primeira execução bem-sucedida (verifique se as tabelas foram criadas no seu banco de dados), COMENTE NOVAMENTE** a linha `db.create_all()` para evitar tentar recriar as tabelas em execuções futuras.

    * **(Opcional - Criar Usuário Admin Inicial):** Se você quiser um usuário administrador padrão, descomente o bloco de código abaixo de `db.create_all()` no `app.py` na **primeira execução** e lembre-se de **trocar a senha padrão**!

7.  **Execute a Aplicação Flask:**

    Com o ambiente virtual ativo e o banco de dados configurado/inicializado, você pode rodar a aplicação:

    ```bash
    flask run
    ```
    ou
    ```bash
    python app.py
    ```

    A aplicação deverá iniciar e indicar o endereço local onde está rodando (geralmente `http://127.0.0.1:5000/`).

8.  **Acesse a Aplicação:**

    Abra seu navegador e visite:

    * Página inicial: `http://127.0.0.1:5000/`
    * Login do Administrador: `http://127.0.0.1:5000/auth/login`

Agora você tem as instruções detalhadas para a seção de instalação do seu README! Lembre-se de adaptar a URL do repositório e as configurações do banco de dados conforme o seu ambiente.

## Como Usar

## Guia de Uso

Este guia explica os passos básicos para administradores e participantes utilizarem a aplicação.

### Para Administradores

1.  **Acesse a Área Administrativa:** Navegue até a página de login do administrador, geralmente em `/auth/login`. Use suas credenciais de administrador para entrar.

2.  **Dashboard do Admin:** Após o login, você será redirecionado para o Dashboard do Admin (`/admin/dashboard`), onde verá uma lista das salas existentes (se houver).

3.  **Crie uma Nova Sala:**
    * No Dashboard, clique no botão "Criar Nova Sala".
    * Na página de criação, insira um nome para a sala (ex: "Hackathon de Inovação", "Quiz de Tecnologia").
    * Clique em "Criar Sala".

4.  **Obtenha o Código da Sala:** Após criar a sala, você será redirecionado de volta para o Dashboard ou para a página de gerenciamento da sala. O código único de 6 dígitos gerado para a sala será exibido (por exemplo, no Dashboard, ao lado do nome da sala). Este código é o que os participantes usarão para entrar.

5.  **Adicione Perguntas (Gerenciar Sala):**
    * No Dashboard, encontre a sala que você acabou de criar e clique no link "Gerenciar".
    * Na página de gerenciamento da sala, você verá a opção para adicionar novas perguntas.
    * Digite o texto da pergunta no campo e clique em "Adicionar Pergunta". Repita para adicionar todas as perguntas desejadas.
    * Você também pode ativar/desativar a sala ou excluí-la nesta página.

### Para Participantes

1.  **Acesse a Página Inicial:** Abra a aplicação no seu navegador, geralmente em `http://127.0.0.1:5000/`.

2.  **Entre em uma Sala:**
    * Na página inicial, clique no botão "Participar Agora" (ou navegue diretamente para `/join`).
    * Você será levado para a página "Entrar em uma Sala".
    * Digite o seu nome.
    * Insira o Código da Sala fornecido pelo administrador.
    * Clique em "Entrar na Sala".

3.  **Responda às Perguntas:**
    * Se o código da sala for válido e a sala estiver ativa, você será redirecionado para a página de Perguntas (`/questions`).
    * Leia cada pergunta e digite sua resposta no campo de texto correspondente.
    * Depois de responder a todas as perguntas (ou as que desejar), clique no botão "Enviar Respostas" ao final da página.

Suas respostas serão salvas, e o administrador poderá visualizá-las na área de gerenciamento da sala, clicando em "Ver Resultados".

## Licença

MIT
