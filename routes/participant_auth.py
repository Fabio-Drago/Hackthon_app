# routes/participant_auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
# Importe o novo modelo ParticipantAccount
from models import db, ParticipantAccount
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash # Já importado em models, mas útil aqui também

participant_auth_bp = Blueprint('participant_auth', __name__)

# ### Lista de domínios de email permitidos ###
ALLOWED_EMAIL_DOMAINS = ['gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com'] # Adicione outros conforme necessário
# ### Fim da lista de domínios permitidos ###

# ### Validador Customizado para domínios de email ###
def validate_allowed_email_domain(form, field):
    email = field.data
    if email: # Garante que só valida se o campo não estiver vazio
        domain = email.split('@')[-1].lower() # Pega a parte após o '@' e converte para minúsculas
        if domain not in ALLOWED_EMAIL_DOMAINS:
            raise ValidationError(f'Endereço de e-mail com domínio não permitido. Domínios válidos são: {", ".join(ALLOWED_EMAIL_DOMAINS)}')
# ### Fim do Validador Customizado ###

# Formulário de login
class ParticipantRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Por favor, insira seu email.'),
        Email(message='Formato de email inválido.'),
        # ### Adicionar o validador customizado aqui ###
        validate_allowed_email_domain # Adiciona a função validadora à lista
        # ### Fim da adição do validador customizado ###
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='Por favor, insira uma senha.'),
        Length(min=6, message='A senha deve ter pelo menos 6 caracteres.'),
        EqualTo('confirm_password', message='As senhas devem ser iguais')
    ])
    confirm_password = PasswordField('Confirme a Senha', validators=[
        DataRequired(message='Por favor, confirme sua senha.')
    ])
    submit = SubmitField('Registrar')


# Formulário de registro
class ParticipantLoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Por favor, insira seu email.'),
        Email(message='Formato de email inválido.'),
         # ### Adicionar o validador customizado aqui também, se quiser ###
        validate_allowed_email_domain # Adiciona a função validadora à lista
         # ### Fim da adição do validador customizado ###
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='Por favor, insira sua senha.')
    ])
    submit = SubmitField('Entrar')

# --- Rotas de Autenticação do Participante ---

@participant_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Se um participante já estiver logado (conta na sessão), redireciona para a entrada da sala
    if 'participant_account_id' in session:
        flash('Você já possui uma conta logada.', 'info')
        return redirect(url_for('participant.join_room_route')) # Redireciona para a entrada da sala

    form = ParticipantRegistrationForm() # Cria uma instância do formulário de registro

    if form.validate_on_submit(): # Processa o formulário se for POST e válido
        # Cria uma nova conta de participante com os dados do formulário
        new_account = ParticipantAccount(email=form.email.data)
        new_account.set_password(form.password.data) # Salva a senha hasheada

        try:
            db.session.add(new_account) # Adiciona a nova conta à sessão do DB
            db.session.commit() # Salva as mudanças no DB
            flash('Sua conta foi criada com sucesso! Agora faça login.', 'success') # Mensagem de sucesso
            # Redireciona para a página de login de participante
            return redirect(url_for('participant_auth.login'))
        except Exception as e:
             db.session.rollback()
             flash(f'Erro ao registrar conta: {e}', 'danger') # Mensagem de erro

    # Renderiza o template de registro, passando o formulário
    return render_template('participant_auth/register.html', title='Criar Conta Participante', form=form)


@participant_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se um participante já estiver logado (conta na sessão), redireciona para a entrada da sala
    if 'participant_account_id' in session:
        flash('Você já possui uma conta logada.', 'info')
        return redirect(url_for('participant.join_room_route')) # Redireciona para a entrada da sala

    form = ParticipantLoginForm() # Cria uma instância do formulário de login

    if form.validate_on_submit(): # Processa o formulário se for POST e válido
        # Busca a conta de participante pelo email
        account = ParticipantAccount.query.filter_by(email=form.email.data).first()

        # Verifica se a conta existe e se a senha está correta
        if account and account.check_password(form.password.data):
            # Autenticação bem-sucedida! Armazena o ID da conta na sessão
            session['participant_account_id'] = account.id
            # Opcional: Armazenar o email na sessão também, mas cuidado com dados sensíveis
            # session['participant_account_email'] = account.email
            flash('Login de participante bem-sucedido!', 'success') # Mensagem de sucesso
            # Redireciona para a página de entrada da sala (onde o código será inserido)
            return redirect(url_for('participant.join_room_route'))
        else:
            # Login falhou
            flash('Email ou senha inválidos.', 'danger')

    # Renderiza o template de login, passando o formulário
    return render_template('participant_auth/login.html', title='Login Participante', form=form)