# routes/participant.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
# Importe todos os modelos necessários
# Importe ParticipantAccount para acessar os dados da conta logada
from models import db, Room, Question, Participant, Answer, ParticipantAccount
from flask_wtf import FlaskForm
# Removidos imports de validação que não são mais usados neste arquivo (Email, EqualTo, ValidationError)
from wtforms import StringField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp


participant_bp = Blueprint('participant', __name__)

# --- Formulários WTForms ---

# JoinRoomForm agora precisa apenas do código da sala
class JoinRoomForm(FlaskForm):
    # Removido o campo 'name' - o nome/identificação virá da ParticipantAccount logada
    # name = StringField('Seu Nome', validators=[DataRequired(), Length(min=2, max=100)])
    room_code = StringField('Código da Sala (6 dígitos)', validators=[
        DataRequired(),
        Length(min=6, max=6, message='O código deve ter exatamente 6 caracteres.'),
        Regexp(r'^[A-Z0-9]{6}$', message='Código inválido. Use apenas letras maiúsculas e números.')
    ])
    submit = SubmitField('Entrar na Sala')

# AnswerForm permanece o mesmo
class AnswerForm(FlaskForm):
    # Campos de resposta serão gerados dinamicamente no template HTML
    submit = SubmitField('Enviar Respostas')


# --- Rotas da Área do Participante ---

@participant_bp.route('/join', methods=['GET', 'POST'])
def join_room_route():
    # ### Nova Lógica: Verificar se a conta do participante está logada ###
    # Se o ID da conta do participante NÃO estiver na sessão, redireciona para o login de participante
    if 'participant_account_id' not in session:
        flash('Por favor, faça login ou crie uma conta para entrar em uma sala.', 'warning')
        return redirect(url_for('participant_auth.login'))

    # Se o participante JÁ ESTÁ em uma sala (Participant entry na sessão), redireciona para as perguntas
    # Isso lida com o caso de já ter entrado na sala e voltar para /join
    if 'participant_id' in session and 'room_id' in session:
        # Opcional: Verificar se a sala ainda existe/está ativa antes de redirecionar
        room = Room.query.get(session['room_id'])
        if room and room.is_active:
             # Redireciona para a página de perguntas se já está em uma sala ativa
             flash('Você já está nesta sala. Redirecionando para suas perguntas.', 'info')
             return redirect(url_for('participant.answer_questions_route'))
        else:
             # Sala não ativa ou não encontrada, limpar APENAS a sessão de entrada na sala atual
             session.pop('participant_id', None)
             session.pop('participant_name', None) # O nome que foi guardado da entrada anterior
             session.pop('room_code', None)
             session.pop('room_id', None)
             flash('A sala anterior não está mais acessível. Entre em uma nova sala.', 'warning')
             # Permite que ele continue o fluxo de entrada na sala atual (GET ou POST abaixo)


    # Se a conta do participante está logada mas ele não está em uma sala, exibe o formulário de entrada na sala

    # Recupera a conta do participante logada via sessão para exibir o email/nome
    account_id = session['participant_account_id']
    participant_account = ParticipantAccount.query.get(account_id)

    # Se a conta não for encontrada (situação inesperada, ex: DB mudou), faz logout da conta e redireciona
    if not participant_account:
         session.pop('participant_account_id', None)
         # Limpa outras chaves de participante/sala por segurança
         session.pop('participant_id', None)
         session.pop('participant_name', None)
         session.pop('room_code', None)
         session.pop('room_id', None)
         flash('Sua conta não foi encontrada. Por favor, faça login novamente.', 'danger')
         return redirect(url_for('participant_auth.login'))


    form = JoinRoomForm() # Cria uma instância do formulário de entrada na sala (agora só pede o código)

    if form.validate_on_submit(): # Processa o formulário se for POST e válido
        room_code = form.room_code.data.upper() # Pega o código

        # Busca a sala pelo código
        room = Room.query.filter_by(code=room_code).first()

        # Verifica se a sala existe e está ativa
        if room and room.is_active:
            # ### Nova Lógica: Cria ou reutiliza uma entrada Participant vinculada à ParticipantAccount logada e à Sala ###
            # Buscar se já existe uma entrada Participant para esta conta nesta sala
            existing_participation = Participant.query.filter_by(
                account_id=participant_account.id,
                room_id=room.id
            ).first()

            if existing_participation:
                 # Se já existe uma entrada, reutiliza ela
                 participant = existing_participation
                 flash(f'Você já está registrado(a) nesta sala. Bem-vindo(a) de volta!', 'info')
            else:
                # Se não existe, cria uma nova entrada Participant
                # Podemos usar ParticipantAccount.email como o "nome" de exibição nesta entrada
                participant = Participant(account_id=participant_account.id, room_id=room.id)
                db.session.add(participant)
                db.session.commit() # Salva no DB para obter o ID da nova entrada Participant
                flash(f'Bem-vindo(a), {participant_account.email}! Você entrou na sala "{room.name}".', 'success')


            # Guarda informações da PARTICIPAÇÃO na sessão do Flask (não da conta de login)
            session['participant_id'] = participant.id # ID da entrada específica desta sala
            session['room_code'] = room.code
            session['room_id'] = room.id # Guarda o ID da sala
            # Guarda o email da conta logada como o "nome" de exibição para esta sessão de sala
            session['participant_name'] = participant_account.email # Usa o email da conta como nome de exibição

            # Redireciona para a página de perguntas
            return redirect(url_for('participant.answer_questions_route'))

        elif room and not room.is_active:
             flash('Esta sala não está ativa no momento.', 'warning') # Mensagem se a sala está inativa
        else:
            flash('Código da sala inválido.', 'danger') # Mensagem se o código não existe

    # Renderiza o template de entrada na sala, passando o formulário
    # Passa o email da conta logada para exibir na página, se necessário
    return render_template('participant/join_room.html',
                           title='Entrar na Sala',
                           form=form,
                           participant_account_email=participant_account.email) # Passa o email da conta logada


# Rota para Responder Perguntas - Reimplementada e Corrigida
@participant_bp.route('/questions', methods=['GET', 'POST'])
def answer_questions_route():
    # ### Nova Lógica: Verificar se a conta do participante está logada E se ele entrou em uma sala ###
    # Precisa ter a conta logada E a entrada na sala registrada na sessão (vindo de /join)
    if 'participant_account_id' not in session or 'participant_id' not in session or 'room_id' not in session:
        flash('Por favor, faça login e entre em uma sala para responder às perguntas.', 'warning')
        # Redireciona para a rota de login de participante
        return redirect(url_for('participant_auth.login'))

    # Recupera informações da sessão
    room_id = session['room_id']
    participant_id = session['participant_id']
    account_id = session['participant_account_id'] # Obtém o ID da conta logada

    # Busca a sala, o participante (entrada específica desta sala) e a conta (para pegar o email/nome)
    room = Room.query.get_or_404(room_id)
    participant = Participant.query.get_or_404(participant_id)
    participant_account = ParticipantAccount.query.get_or_404(account_id) # Busca a conta

    # ### Verificação de Segurança Extra ###
    # Verifica se a entrada Participant na sessão está realmente associada à conta ParticipantAccount logada
    if participant.account_id != participant_account.id:
         flash('Sessão inválida. Discrepância de conta. Por favor, faça login novamente.', 'danger')
         # Limpa TODAS as informações de sessão (conta e sala) em caso de inconsistência grave
         session.pop('participant_account_id', None)
         session.pop('participant_id', None)
         session.pop('room_id', None)
         session.pop('participant_name', None) # O nome que foi guardado da entrada anterior
         session.pop('room_code', None)
         return redirect(url_for('participant_auth.login')) # Redireciona para o login de participante
    # ### Fim da Verificação de Segurança ###


    # Verifica se a sala ainda está ativa
    if not room.is_active:
        flash('Esta sala foi desativada pelo administrador. Sua sessão de sala foi encerrada.', 'danger')
        # Limpa APENAS as informações da sessão RELACIONADAS À ENTRADA NA SALA
        session.pop('participant_id', None)
        session.pop('participant_name', None)
        session.pop('room_code', None)
        session.pop('room_id', None)
        # Não limpa participant_account_id, a conta continua logada.
        # Ele será redirecionado para /join automaticamente pelo check no início da rota
        return redirect(url_for('participant.join_room_route')) # Redireciona para a entrada de sala (com a conta logada)


    # Busca todas as perguntas associadas a esta sala, ordenadas
    questions = Question.query.filter_by(room_id=room.id).order_by(Question.id).all()

    # Busca as respostas existentes DESTA ENTRADA PARTICIPANT (participant_id) para pré-preencher o formulário
    existing_answers = {ans.question_id: ans.text for ans in Answer.query.filter_by(participant_id=participant_id).all()}

    form = AnswerForm() # Instância do formulário (para o CSRF token)

    if request.method == 'POST':
        # Processa as respostas enviadas (lógica permanece a mesma, salva para o participant_id atual)
        for question in questions:
            answer_text = request.form.get(f'question_{question.id}')
            if answer_text is not None:
                clean_answer_text = answer_text.strip()

                # Busca se já existe uma resposta para esta pergunta por este participante (entrada na sala)
                existing_answer = Answer.query.filter_by(participant_id=participant_id, question_id=question.id).first()

                if existing_answer:
                    existing_answer.text = clean_answer_text
                    existing_answer.submitted_at = db.func.now()
                elif clean_answer_text: # Só cria uma nova resposta se não for vazia após remover espaços
                    new_answer = Answer(text=clean_answer_text,
                                        participant_id=participant_id,
                                        question_id=question.id,
                                        submitted_at=db.func.now())
                    db.session.add(new_answer)

        try:
            db.session.commit()
            flash('Suas respostas foram salvas com sucesso!', 'success')
            # Recarrega as respostas após salvar para exibir o estado atual (se ficar na mesma página)
            existing_answers = {ans.question_id: ans.text for ans in Answer.query.filter_by(participant_id=participant_id).all()}

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar respostas: {e}', 'danger')

    # Renderiza o template de perguntas
    return render_template('participant/answer_questions.html',
                           title=f'Perguntas - Sala {room.name}', # Título da página
                           room=room, # Objeto Room
                           questions=questions, # Lista de objetos Question
                           participant=participant, # Objeto Participant (a entrada específica desta sala)
                           # Passa o email da conta logada para exibição no template
                           participant_account_email=participant_account.email,
                           existing_answers=existing_answers, # Dicionário de respostas existentes
                           form=form) # Passa a instância do formulário (para o CSRF token)


# ROTA PARA REGRAS
@participant_bp.route('/rules')
def participant_rules():
    # Renderiza o template de regras para participantes
    return render_template('participant/rules.html', title='Regras do Hackathon')

# Opcional: Rota de "Obrigado" após submeter
# @participant_bp.route('/thank_you')
# def thank_you_route():
#    # Renderiza o template de agradecimento
#    return render_template('participant/thank_you.html', title="Obrigado por Participar!")

# NOTA: A rota /logout para participantes individuais foi REMOVIDA deste arquivo
# A lógica de logout agora está na rota /logout genérica em app.py