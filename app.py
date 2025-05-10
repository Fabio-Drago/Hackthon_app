# app.py

import datetime
import os
from flask import Flask, render_template, redirect, url_for, flash, request, session
from config import Config # Importa sua classe de configuração

# ### INICIALIZAÇÃO DAS EXTENSÕES (Nível Superior) ###
# Cria as instâncias das extensões sem associá-las a uma app específica ainda.
# Elas serão inicializadas com a app dentro da fábrica.
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, logout_user, current_user
# REMOVA ESTA LINHA: from flask_mail import Mail, Message # Não usaremos mais Flask-Mail
# REMOVA ESTA LINHA: mail = Mail() # Não usaremos mais Flask-Mail

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# Não há instância 'mail' para inicializar aqui

# Configurações do Flask-Login (feitas aqui ou dentro da fábrica)
login_manager.login_view = 'participant_auth.login' # Rota para onde redirecionar usuários não logados
login_manager.login_message_category = 'info' # Categoria da mensagem flash para login_required


# ### Importação dos Blueprints ###
# Importa o Blueprint que contém as rotas relacionadas à newsletter
from routes.newsletter_routes import newsletter_bp
# Importa os outros blueprints (ajuste conforme a estrutura das suas pastas em 'routes/')
from routes.auth import auth_bp as auth_blueprint
from routes.admin import admin_bp as admin_blueprint
from routes.participant import participant_bp as participant_blueprint
from routes.participant_auth import participant_auth_bp as participant_auth_blueprint
# from routes.main import main as main_blueprint # Descomente quando criar o blueprint main


# ### FÁBRICA DE APLICAÇÃO ###
def create_app(config_class=Config):
    """Cria e configura a aplicação Flask."""

    app = Flask(__name__)
    # Carrega a configuração da classe Config (que lê do .env via config.py)
    app.config.from_object(config_class)

    # Garante que a pasta de instância existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # A pasta já existe

    # ### ASSOCIAÇÃO DAS EXTENSÕES COM A APP (DENTRO da fábrica) ###
    # Inicializa as extensões associando-as à instância 'app' criada.
    # NÃO INICIALIZAMOS MAIS O FLASK-MAIL AQUI.
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    # REMOVA ESTA LINHA: mail.init_app(app) # Não usaremos mais Flask-Mail


    # Configurações do Jinja2 (adicionado para funcionalidades como 'hasattr')
    app.jinja_env.globals['hasattr'] = hasattr


    # ### IMPORTAR MODELOS (DENTRO da fábrica) ###
    # Importe os modelos AQUI, DEPOIS que db.init_app(app) foi chamado.
    # Isso ajuda a evitar importações circulares.
    # Importa os modelos necessários (Admin para user_loader, Subscriber para uso potencial)
    # AJUSTE A IMPORTAÇÃO CONFORME A ESTRUTURA DO SEU PROJETO
    try:
        from models import Admin, Subscriber
    except ImportError:
        # Fallback ou ajuste para sua estrutura real
        print("Erro ao importar modelos. Verifique a estrutura do seu projeto.")
        # Pode precisar de sys.path.append aqui dependendo da estrutura
        from .models import Admin, Subscriber # Exemplo para estrutura de pacote


    # ### FUNÇÃO USER_LOADER (DENTRO da fábrica) ###
    # Define e registra a função user_loader AQUI, DEPOIS que login_manager.init_app(app) foi chamado.
    @login_manager.user_loader
    def load_user(user_id):
        """Carrega um usuário Admin pelo ID para o Flask-Login."""
        if user_id is not None:
            # O modelo Admin é importado acima, dentro desta fábrica.
            return db.session.get(Admin, int(user_id))
        return None


    # ### REGISTRO DE BLUEPRINTS ###
    # Registra os Blueprints na aplicação
    app.register_blueprint(auth_blueprint, url_prefix='/auth') # Rotas de autenticação de admin
    app.register_blueprint(admin_blueprint, url_prefix='/admin') # Rotas da área administrativa
    app.register_blueprint(participant_blueprint, url_prefix='/') # Rotas principais do participante (ex: /join)
    app.register_blueprint(participant_auth_blueprint, url_prefix='/participant') # Rotas de autenticação de participante

    # REGISTRE O BLUEPRINT DA NEWSLETTER AQUI
    app.register_blueprint(newsletter_bp)

    # app.register_blueprint(main_blueprint) # Descomente quando criar o blueprint main para rotas gerais (ex: /)


    # ### CONTEXT PROCESSORS (Opcional) ###
    # Funções que injetam variáveis em todos os contextos de template.
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.utcnow}

    # ### ROTAS DIRETAS (Se não estiverem em blueprints, ou se forem rotas globais como a raiz) ###
    # A rota '/' é definida aqui. Se você tiver um blueprint 'main', mova-a para lá.
    @app.route('/')
    def index():
        # Verifica se há uma sessão de participante ativa
        if 'participant_account_id' in session:
            flash('Você já está logado. Insira o código da sala para continuar.', 'info')
            # Redireciona para a rota de entrar na sala do blueprint 'participant'
            # Certifique-se de que 'participant.join_room_route' é o nome correto do endpoint
            return redirect(url_for('participant.join_room_route'))
        # Se não houver sessão de participante, renderiza a página inicial genérica
        # O template index.html exibirá flash messages se houver.
        return render_template('index.html')


    # ### A ROTA /subscribe FOI COMPLETAMENTE MOVIDA PARA routes/newsletter_routes.py ###
    # Não deve haver nenhuma definição @app.route('/subscribe') aqui.


    @app.route('/terms')
    def terms_and_conditions():
        return render_template('terms.html', title='Termos e Condições')

    # Rota de Logout Unificada (para Admin e Participante)
    @app.route('/logout')
    def logout():
        # Verifica se um admin está logado via Flask-Login
        if current_user.is_authenticated:
            logout_user() # Desconecta o admin
            flash('Você (Admin) foi desconectado.', 'info')
            # Redireciona para a página de login do admin (ou outra página apropriada)
            return redirect(url_for('auth.login')) # Ajuste 'auth.login' se o endpoint for diferente

        # Verifica se há uma sessão de participante ativa
        elif 'participant_account_id' in session:
            # Limpa as informações da sessão do participante
            session.pop('participant_account_id', None)
            session.pop('participant_id', None)
            session.pop('participant_name', None)
            session.pop('room_code', None)
            session.pop('room_id', None)

            flash('Sua conta de participante foi desconectada.', 'info')
            # Redireciona para a página inicial ou página de entrada de participante
            return redirect(url_for('index')) # Ajuste 'index' ou 'participant.join_room_route' conforme necessário

        # Se não houver sessão de admin ou participante, informa que já está desconectado
        flash('Você já está desconectado.', 'info')
        return redirect(url_for('index'))


    # ### LÓGICA DE INICIALIZAÇÃO NO CONTEXTO DA APP (EXECUTA NA CRIAÇÃO DA APP) ###
    # Este bloco garante que certas operações que precisam do contexto da aplicação
    # sejam executadas durante a criação da app.
    with app.app_context():
        # Exemplo: Criar tabelas se não existirem (geralmente feito com Flask-Migrate)
        # db.create_all() # Descomente APENAS para testes iniciais sem migrações (não use com migrações)

        # Remova qualquer lógica que consulte o DB aqui se ela estiver causando o erro inicial
        pass

    # ### COMANDO CLI CUSTOMIZADO PARA CRIAR ADMIN (DENTRO da fábrica) ###
    # Este bloco DEVE FICAR AQUI, DENTRO da função create_app(),
    # para que o comando seja registrado na instância 'app' correta APÓS a importação do modelo Admin.
    from werkzeug.security import generate_password_hash # Importa a função para criar hash de senha

    @app.cli.command("create-initial-admin")
    def create_initial_admin_command():
        """Cria um administrador inicial se nenhum existir."""
        # O contexto da aplicação é necessário para operações de DB
        with app.app_context():
            # O modelo Admin é importado acima, dentro desta fábrica.
            if Admin.query.first() is None:
                print("Nenhum administrador encontrado.")

                # Define credenciais padrão a partir de variáveis de ambiente ou valores fixos
                default_admin_username = os.environ.get('DEFAULT_ADMIN_USERNAME', 'Admin') #<<< mude isso
                default_admin_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'Admin123') #<<< mude isso

                print(f"Criando administrador padrão: {default_admin_username}")

                # Cria o novo objeto Admin
                initial_admin = Admin(username=default_admin_username)
                # Define a senha usando a função set_password do modelo Admin
                initial_admin.set_password(default_admin_password)

                # Adiciona e salva no banco de dados
                db.session.add(initial_admin)
                db.session.commit()
                print("Administrador padrão criado com sucesso!")
                print("!!! Por favor, mude a senha IMEDIATAMENTE após o primeiro login. !!!")
            else:
                print("Administrador já existe.")
    # ### FIM COMANDO CLI CUSTOMIZADO ###


    # A função factory retorna a instância 'app' configurada
    return app

# ### CRIAÇÃO DA INSTÂNCIA GLOBAL DA APP ###
# Esta linha CRIA a instância 'app' chamando a função factory create_app().
# É esta instância que será usada pelo servidor web (como Gunicorn no PythonAnywhere).
app = create_app()

# ### BLOCO PARA RODAR DIRETAMENTE (Opcional com 'python app.py') ###
# Este bloco só é executado se você rodar o arquivo diretamente (python app.py).
# Geralmente não é usado em produção com servidores WSGI como Gunicorn.
if __name__ == '__main__':
    # Remova debug=True em produção!
    # Host '0.0.0.0' torna o servidor acessível externamente, útil em alguns ambientes.
    # Porta 5000 é a padrão, ajuste se necessário.
    app.run(debug=True, host='0.0.0.0', port=5000)