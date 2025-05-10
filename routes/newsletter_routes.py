# newsletter_routes.py
# Importar bibliotecas necessárias
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
# REMOVA ESTA LINHA: from flask_mail import Mail, Message # Não usaremos mais Flask-Mail
# Importar para lidar com data/hora
from datetime import datetime, timedelta
# Importar para gerar e validar tokens seguros
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

# Importar a instância do banco de dados e o modelo Subscriber
# Ajuste a importação conforme a estrutura do seu projeto.
# Esta importação assume que 'db' e 'models' estão no nível acima da pasta 'routes'.
# Se a sua estrutura de pastas for diferente (ex: 'app' é um pacote), ajuste a importação.
try:
    from .. import db
    from ..models import Subscriber
except ImportError:
    # Fallback para estrutura de projeto simples onde app.py e models.py estão no mesmo nível que a pasta 'routes'
    # ou se 'app' for o pacote principal.
    import sys
    import os
    # Adiciona o diretório pai ao sys.path se necessário
    # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    try:
        # Tenta importar de 'app' e 'models' (se estiverem no sys.path ou no pacote principal)
        from app import db # Assume que 'db' é definido globalmente em app.py ou __init__.py
        from models import Subscriber # Assume que 'models' está no mesmo nível que app.py ou é importado no __init__.py
    except ImportError as e_inner:
        # Se mesmo assim não encontrar, levanta o erro original
        print(f"Erro de importação em newsletter_routes.py: {e_inner}")
        print("Por favor, verifique a estrutura do seu projeto e ajuste as importações de 'db' e 'Subscriber'.")
        raise # Levanta o erro para parar a execução e mostrar o problema

# Importar para threading (para envio assíncrono de email)
import threading
# Importar para logs
import logging

# ### Importar a biblioteca Mailjet (NOVO) ###
from mailjet_rest import Client # Importa o cliente da API Mailjet


# Configurar logging básico se não estiver configurado em outro lugar
logging.basicConfig(level=logging.INFO)


# Criar o blueprint para newsletter
newsletter_bp = Blueprint('newsletter', __name__)


# Função para obter o serializador de token (usando SECRET_KEY do app)
def get_token_serializer():
    """Obtém um serializador de token seguro usando a SECRET_KEY da aplicação."""
    # A SECRET_KEY é necessária para assinar os tokens
    # current_app é acessível porque esta função será chamada dentro de um contexto de aplicação
    if 'SECRET_KEY' not in current_app.config or not current_app.config['SECRET_KEY']:
         # Lança erro se a chave secreta não estiver configurada
         raise RuntimeError("SECRET_KEY não está definida ou é vazia nas configurações da aplicação. Necessária para tokens seguros.")
    # Cria e retorna um serializador URL-safe com tempo limite
    # O salt ('email-confirm-salt') DEVE ser o mesmo usado na geração e validação.
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


# Rota para processar subscrição (Usa DB e gera Tokens)
@newsletter_bp.route('/subscribe', methods=['POST'])
def subscribe():
    """Processa a submissão do formulário de inscrição na newsletter."""
    # Obter dados do formulário.
    # Assumimos que o formulário está sendo enviado via POST tradicional (não JSON via JS fetch).
    data = request.form

    # Extrair campos do formulário (usamos .get para evitar KeyError se o campo faltar)
    email = data.get('email', '').strip().lower() # Normaliza para minúsculas e remove espaços
    name = data.get('name', '').strip()
    # getlist é usado para checkboxes com o mesmo atributo 'name'
    interests_data = data.getlist('interests') # Se você armazena interesses, trate aqui

    # Validar email básico (formato)
    if not email or '@' not in email or '.' not in email:
        flash('Por favor, insira um endereço de email válido.', 'danger')
        # Redireciona de volta para a página inicial
        return redirect(url_for('index'))

    # Verificar se o email já existe no banco de dados
    # Query eficiente para buscar pelo email
    existing_subscriber = Subscriber.query.filter_by(email=email).first()
    if existing_subscriber:
        if existing_subscriber.confirmed:
            flash('Este email já está subscrito e confirmado.', 'warning')
        else:
            flash('Este email já está subscrito, mas ainda não confirmado. Por favor, verifique sua caixa de entrada.', 'info')
        # Redireciona de volta para a página inicial
        return redirect(url_for('index'))

    # Inicia um bloco try/except para lidar com possíveis erros de banco de dados ou preparação do envio
    try:
        # Criar um novo assinante no banco de dados
        # Assumindo que o modelo Subscriber tem campos 'email', 'name' (opcional), 'confirmed' (False por padrão)
        new_subscriber = Subscriber(email=email, name=name, confirmed=False)

        # Adiciona o novo assinante à sessão do banco de dados
        db.session.add(new_subscriber)
        # Comita para salvar no banco de dados. Isso é importante para que o new_subscriber tenha um ID
        # e para que a transação seja confirmada antes de tentar enviar o email.
        db.session.commit()

        # Gerar token de confirmação usando itsdangerous
        serializer = get_token_serializer()
        # O token codifica o email do assinante. Usamos um 'salt' ('email-confirm-salt')
        # para diferenciar tokens de confirmação de outros tipos de tokens (ex: redefinição de senha).
        token = serializer.dumps(email, salt='email-confirm-salt')

        # Enviar email de confirmação em uma thread separada para não bloquear a requisição web
        # É crucial passar a instância da aplicação (current_app._get_current_object())
        # para que a thread possa empurrar o contexto da aplicação e usar recursos como url_for.
        # A função de envio (send_confirmation_email) foi atualizada para usar a API do Mailjet.
        threading.Thread(target=send_confirmation_email_task, args=(email, name, token, current_app._get_current_object())).start()

        # Mensagem flash de sucesso para o usuário
        flash('Inscrição realizada com sucesso! Verifique seu e-mail para confirmar.', 'success')

    except Exception as e:
        # Em caso de qualquer erro durante o processamento ou envio (ex: problema de DB)
        # Desfaz as mudanças pendentes na sessão do banco de dados
        db.session.rollback()
        # Loga o erro no servidor (importante para depuração)
        current_app.logger.error(f"Erro ao processar subscrição para {email}: {e}", exc_info=True) # exc_info=True para incluir traceback
        flash('Ocorreu um erro ao processar sua subscrição. Por favor, tente novamente.', 'danger')

    # Redireciona de volta para a página inicial após tentar processar a subscrição
    # O feedback virá das flash messages na página de destino.
    return redirect(url_for('index'))


# Tarefa de envio de email para ser executada em uma thread
# Esta função é um wrapper para garantir que send_confirmation_email rode com o contexto da aplicação
def send_confirmation_email_task(email, name, token, app):
    """Função wrapper para enviar email de confirmação em uma thread com contexto de aplicação."""
    # Empurra o contexto da aplicação para que Flask-Mail e url_for funcionem na thread
    with app.app_context():
        # Chama a função real de envio de email (AGORA USA MAILJET)
        send_confirmation_email(email, name, token)


# ### Função para enviar email de confirmação USANDO MAILJET (NOVO) ###
# Esta função PRECISA rodar DENTRO de um contexto de aplicação (via send_confirmation_email_task).
def send_confirmation_email(email, name, token):
    """Envia o email de confirmação usando a API do Mailjet."""
    try:
        # --- OBTENHA AS CONFIGURAÇÕES DO MAILJET DO app.config ---
        api_key = current_app.config.get('MAILJET_API_KEY')
        api_secret = current_app.config.get('MAILJET_API_SECRET')
        sender_email = current_app.config.get('MAIL_DEFAULT_SENDER') # Seu email/nome remetente verificado no Mailjet

        # Verifique se as configurações do Mailjet estão presentes
        if not api_key or not api_secret or not sender_email:
             current_app.logger.error("Configurações do Mailjet incompletas ou ausentes.")
             # Não é comum dar flash message de erro aqui, pois é em thread.
             # O erro será logado.
             return # Sai da função se não puder enviar

        # --- INICIALIZAR O CLIENTE MAILJET ---
        mailjet = Client(auth=(api_key, api_secret), version='v3.1') # Usamos a API v3.1

        # --- GERAR LINKS DE CONFIRMAÇÃO E CANCELAMENTO (Lógica ITSDANGEROUS permanece) ---
        serializer = get_token_serializer()
        # url_for precisa do contexto da aplicação e _external=True
        confirm_url = url_for('newsletter.confirm_subscription', token=token, _external=True)
        # Gerar token para cancelamento (com salt diferente)
        unsubscribe_token = serializer.dumps(email, salt='email-unsubscribe-salt')
        unsubscribe_url = url_for('newsletter.unsubscribe', token=unsubscribe_token, _external=True)

        # --- CONSTRUIR CORPOS DO EMAIL (HTML e Texto) ---
        # Use f-strings ou templates Jinja2 para o corpo do email, inserindo as URLs e o nome.
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirmação de Inscrição</title>
    <style>
        /* Seus estilos CSS para o email */
         body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; background-color: #f9f9f9; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%); color: white; text-align: center; padding: 30px 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: white; padding: 30px; border-radius: 0 0 8px 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .button {{ display: inline-block; background: linear-gradient(45deg, #00c6ff, #0072ff); color: white; text-decoration: none; padding: 12px 25px; border-radius: 50px; margin: 20px auto; font-weight: bold; display: block; text-align: center; max-width: 200px; }} /* Botão centralizado */
        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        .footer a {{ color: #666; text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Hackathon App</h1>
        </div>
        <div class="content">
            <h2>Olá{f' {name}' if name else ''}!</h2> <p>Obrigado por se inscrever em nossa newsletter. Estamos muito felizes em tê-lo(a) em nossa comunidade!</p>
            <p>Para confirmar sua inscrição e começar a receber nossas atualizações, por favor, clique no botão abaixo:</p>

            <a href="{confirm_url}" class="button">Confirmar Inscrição</a>

            <p>Se você não solicitou esta inscrição, por favor, ignore este e-mail.</p>
        </div>
        <div class="footer">
            <p>© {datetime.now().year} Hackathon App. Todos os direitos reservados.</p>
            <p>Para cancelar sua inscrição, <a href="{unsubscribe_url}">clique aqui</a>.</p>
        </div>
    </div>
</body>
</html>
"""
        text_body = f"""
Olá{f' {name}' if name else ''}!

Obrigado por se inscrever em nossa newsletter do Hackathon App.

A partir de agora, você receberá atualizações sobre nossos próximos eventos, workshops e oportunidades exclusivas.

Para confirmar sua inscrição, acesse o link abaixo:
{confirm_url}

Se você não se inscreveu em nossa newsletter, apenas ignore este email.

© {datetime.now().year} Hackathon App. Todos os direitos reservados.

Para cancelar sua inscrição, acesse:
{unsubscribe_url}
"""

        # --- PREPARAR O PAYLOAD PARA A API DO MAILJET ---
        # A estrutura exata é definida pela API do Mailjet (v3.1)
        # Consulte a documentação oficial do Mailjet para detalhes!
        data = {
          'Messages': [
            {
              "From": {
                "Email": sender_email.split('<')[-1].strip('> ') if '<' in sender_email else sender_email, # Apenas o endereço de email
                "Name": sender_email.split('<')[0].strip() if '<' in sender_email else None # Apenas o nome (opcional)
              },
              "To": [
                {
                  "Email": email, # O endereço de email do destinatário
                  "Name": name # O nome do destinatário (opcional)
                }
              ],
              "Subject": "Confirmação de Inscrição - Hackathon App", # Assunto do email
              "TextPart": text_body, # Conteúdo em texto simples
              "HTMLPart": html_body # Conteúdo em HTML
              # Você pode adicionar outras opções aqui, como 'CustomID' para tracking
            }
          ]
        }

        # --- ENVIAR O EMAIL USANDO O CLIENTE MAILJET ---
        # Chamar a API /send
        result = mailjet.send.create(data=data)

        # --- VERIFICAR O RESULTADO DA API ---
        # O código de status 200 geralmente indica sucesso para API v3.1
        if result.status_code == 200:
            current_app.logger.info(f"Email de confirmação enviado via Mailjet API para: {email}")
            # Você pode logar a resposta da API para mais detalhes se necessário:
            # current_app.logger.info(f"Resposta da API Mailjet: {result.json()}")
        else:
            # Se a API retornou um erro, logue o status e a resposta completa para depuração
            current_app.logger.error(f"Erro ao enviar email via Mailjet API para {email}: Status {result.status_code}, Resposta: {result.json()}")
            # Loga o payload enviado (sem as chaves da API que estão na autenticação)
            current_app.logger.error(f"Payload enviado: {data}")


    except Exception as e:
        # Captura quaisquer outros erros inesperados (problemas de rede, erro na biblioteca, etc.)
        current_app.logger.error(f"Erro inesperado na função send_confirmation_email (Mailjet) para {email}: {e}", exc_info=True)


# Suas rotas de confirmação e cancelamento (confirm_subscription, unsubscribe) permanecem as mesmas
# Elas dependem apenas do itsdangerous e do DB, não do método de envio inicial.

# Sua rota admin_subscribers e export_subscribers permanecem as mesmas