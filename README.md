# Hackathon app

![Captura de tela 2025-05-09 132413](https://github.com/user-attachments/assets/c938ca3b-f854-4ede-b613-917fd182ad6a)

Nota: esta web application não terá atualizações durante algum tempo provalvemente.

## Requisitos

Para configurar e rodar esta aplicação, você precisará ter instalado em seu sistema:

* **Python 3.7+**
* **MySQL Server**
* **Git**
* **Ou podes usar um serviço de Platform as a Service - PaaS, no meu caso eu uso "pythonanywhere"**

## Configuração do Ambiente

Siga estes passos para preparar seu ambiente de desenvolvimento:

1.  **Clone o Repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO_AQUI]
    cd [nome_da_pasta_do_seu_projeto]
    ```

2.  **Crie um Ambiente Virtual:**
    É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.
    ```bash
    python -m venv venv
    ```

3.  **Ative o Ambiente Virtual:**

    * **No Windows (Prompt de Comando):**
        ```cmd
        venv\Scripts\activate
        ```
    * **No Windows (PowerShell):**
        ```powershell
        .\venv\Scripts\activate
        ```
    * **No macOS e Linux (Bash/Zsh):**
        ```bash
        source venv/bin/activate
        ```
    Você verá `(venv)` no início da linha do seu terminal, indicando que o ambiente virtual está ativo.

4.  **Instale as Dependências:**
    Com o ambiente virtual ativo, instale as bibliotecas Python necessárias. Certifique-se de que você tem um arquivo `requirements.txt` na raiz do seu projeto listando as dependências. Se não tiver, crie um rodando `pip freeze > requirements.txt` após instalar as bibliotecas que você usa (Flask, Flask-SQLAlchemy, Flask-Migrate, PyMySQL, python-dotenv, Flask-Login, cryptography, Werkzeug).

    Um `requirements.txt` típico para este projeto conteria:
    ```
    Flask==3.0.0
    Flask-SQLAlchemy==3.1.1
    Flask-Login==0.6.3
    Flask-WTF==1.2.1
    Flask-Migrate==4.0.5 
    Flask-SocketIO==5.3.6 
    PyMySQL==1.1.0 
    python-dotenv==1.0.0 
    Werkzeug==3.0.1  
    email-validator==2.0.0 
    Flask-Login>=0.6.0,<1.0.0
    Flask-WTF>=1.2.0,<2.0.0
    WTForms>=3.0.0,<4.0.0
    ```
    Instale-as com:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Se não tiver, crie o Arquivo de Configuração de Ambiente (`.env`):**
    Na raiz do seu projeto, crie um arquivo chamado `.env`. Este arquivo armazenará configurações sensíveis e específicas do ambiente.

    ```dotenv
    # .env

    SECRET_KEY='sua_chave_secreta_aqui' # Gere uma chave aleatória forte e única
    DATABASE_URL='mysql+pymysql://usuario_mysql:senha_mysql@host_mysql:porta_mysql/nome_do_banco_de_dados'

    # Exemplo para MySQL Local:
    # DATABASE_URL='mysql+pymysql://root:sua_senha_do_root@localhost:3306/hackton'

    # Opcional: Credenciais Admin Padrão (se você adicionar lógica para criá-lo via CLI)
    # DEFAULT_ADMIN_USERNAME='admin'
    # DEFAULT_ADMIN_PASSWORD='senha_inicial'
    ```
    * Substitua `sua_chave_secreta_aqui` por uma string aleatória e segura.
    * Substitua os valores em `DATABASE_URL` pelas credenciais e detalhes de conexão do seu servidor MySQL local. Certifique-se de que o `usuario_mysql` tem permissão para criar tabelas no `nome_do_banco_de_dados`.

6.  **Configure a Variável de Ambiente `FLASK_APP`:**
    Esta variável diz ao comando `flask` onde encontrar sua aplicação. Execute o comando apropriado para o seu shell (com o ambiente virtual ativo):

    * **No Windows (Prompt de Comando):**
        ```cmd
        set FLASK_APP=app
        ```
    * **No Windows (PowerShell):**
        ```powershell
        $env:FLASK_APP="app"
        ```
    * **No macOS e Linux (Bash/Zsh):**
        ```bash
        export FLASK_APP=app
        ```
    Você precisará executar este comando em cada nova sessão do terminal.

## Configuração do Banco de Dados

A aplicação usa o MySQL e gerencia a estrutura do banco de dados com o Flask-Migrate.

1.  **Crie o Banco de Dados MySQL:**
    No seu servidor MySQL, crie um banco de dados com o mesmo nome especificado na sua `DATABASE_URL` no arquivo `.env` (por exemplo, `hackton`). Você pode fazer isso usando um cliente MySQL (MySQL Workbench, DBeaver, linha de comando `mysql`, etc.).

    Exemplo usando a linha de comando MySQL:
    ```sql
    CREATE DATABASE hackton CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    ```

2.  **Execute as Migrações do Banco de Dados:**
    Na pasta raiz do projeto, com o ambiente virtual ativo e `FLASK_APP` configurado, execute os comandos do Flask-Migrate na seguinte ordem:

    * **Inicialize o repositório de migrações (rode apenas na primeira vez):**
        ```bash
        flask db init
        ```
        Isso criará a pasta `migrations/`.

    * **Gere o script da migração inicial (rode sempre que alterar seus modelos em `models.py`):**
        ```bash
        flask db migrate -m "create initial tables"
        ```
        Isso criará um novo arquivo Python na pasta `migrations/versions/`.

    * **Aplique as migrações ao banco de dados (rode para criar/atualizar as tabelas):**
        ```bash
        flask db upgrade
        ```
        Este comando se conectará ao seu banco de dados (usando a `DATABASE_URL` do `.env`) e executará o script gerado para criar todas as suas tabelas ou atualizar e criar novas. Se tiver novas e quiser ver na base de dados, apenas vá atualizando com o flash db migrate "nome_da_sua_escolha" caso precise:

      Exemplo: flask db migrate -m "create new system" e depois faça o `flask db upgrade`

    Se `flask db upgrade` rodar sem erros, suas tabelas estarão prontas no banco de dados.

3.  **Execute a web application:**

    * **Começe a rodar o programa:**
        ```bash
        flask run
        ```

    * **Digite no navegador:**
        ```bash
        127.0.0.1:5000
        ```

    **Outras informações:**

    Não tem um admin? Use o comando customizado: `flask create-initial-admin`.

    Quer fazer login como admin? Isso é feito em: `http://127.0.0.1:5000/auth/login`

    Aviso: no `app.py` e ficheiro `.env` tem campos que devem ser mudados, favor ler bem toda documentação em caso de problemas.
