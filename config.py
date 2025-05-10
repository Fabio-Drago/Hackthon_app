# config.py
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
basedir = os.path.abspath(os.path.dirname(__file__))
# Tenta carregar o .env na raiz do projeto
dotenv_path = os.path.join(basedir, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # Fallback: se o .env não estiver na raiz, pode estar no diretório atual
    load_dotenv()

class Config:
    # Chave Secreta da Aplicação - ESSENCIAL PARA SEGURANÇA!
    # Use 'os.urandom(24)' em um console Python para gerar uma chave forte.
    # NUNCA use o fallback padrão em produção. Defina SECRET_KEY no seu .env.
    SECRET_KEY = os.environ.get('SECRET_KEY') # Tenta ler de SECRET_KEY no ambiente/env

    # Fallback inseguro para SECRET_KEY caso não esteja definida (apenas para evitar falha total em desenvolvimento)
    if not SECRET_KEY:
        print("!!! WARNING: SECRET_KEY não definida no ambiente/dotenv. Usando fallback inseguro. !!!")
        SECRET_KEY = 'uma-chave-fallback-MUITO-insegura-em-desenvolvimento-TROQUE-IMEDIATAMENTE'


    # Configuração do Banco de Dados
    # Lê do DATABASE_URL no .env (comum em ambientes de deploy como Heroku)
    # ou usa SQLite local como fallback para desenvolvimento
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db') # Fallback para SQLite

    SQLALCHEMY_TRACK_MODIFICATIONS = False # Desativa o rastreamento de modificações do SQLAlchemy (recomendado)

    # ### Configurações do Mailjet (NOVO) ###
    # Lidas de variáveis de ambiente no .env ou ambiente de deploy.
    MAILJET_API_KEY = os.environ.get('MAILJET_API_KEY') # Sua chave API pública do Mailjet
    MAILJET_API_SECRET = os.environ.get('MAILJET_API_SECRET') # Sua chave API secreta do Mailjet

    # O remetente padrão (DEVE ser um email verificado no Mailjet)
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@seuservidor.com'

    # Outras configurações podem ser adicionadas aqui
    # ...