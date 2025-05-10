# routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
# Importe todos os modelos necessários
# Certifique-se de que Participant, Answer, Question, Room, Admin, ParticipantAccount estão importados
from models import db, Room, Question, Participant, Answer, Admin, ParticipantAccount
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Regexp
import random
import string
from datetime import datetime # Importe datetime

admin_bp = Blueprint('admin', __name__)

# --- Formulários WTForms ---
class RoomForm(FlaskForm):
    name = StringField('Nome da Sala', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Criar Sala')

class QuestionForm(FlaskForm):
    text = TextAreaField('Texto da Pergunta', validators=[DataRequired()])
    room_id = HiddenField() # Para associar a pergunta à sala correta
    submit = SubmitField('Adicionar Pergunta')

# --- Rotas da Área Administrativa ---

@admin_bp.route('/dashboard')
@login_required # Restringe o acesso a usuários logados (Admins)
def dashboard():
    # Busca todas as salas criadas pelo admin logado, ordenadas pela data de criação (mais recente primeiro)
    admin_rooms = Room.query.filter_by(admin_id=current_user.id).order_by(Room.created_at.desc()).all()

    # --- Lógica para calcular o total de participantes e respostas para o dashboard ---
    # Esta lógica conta participantes e respostas APENAS nas salas do admin logado.

    # 1. Obter os IDs das salas do admin logado
    admin_room_ids = [room.id for room in admin_rooms]

    # 2. Calcular o total de participantes
    # Conta todas as entradas de Participant cujas room_id estão na lista de IDs das salas do admin
    # Assumindo que 'Participant' representa uma entrada única por pessoa por sala.
    total_participants = Participant.query.filter(
        Participant.room_id.in_(admin_room_ids)
    ).count()

    # 3. Calcular o total de respostas
    # Conta todas as respostas ('Answer') associadas a perguntas ('Question')
    # que, por sua vez, estão associadas a salas ('Room') do admin logado.
    # Usa joins implícitos ou relacionamentos definidos nos modelos.
    total_responses = Answer.query.join(Question).join(Room).filter(
        Room.admin_id == current_user.id
    ).count()

    # --- Fim da lógica de cálculo para o dashboard ---


    # Renderiza o template do dashboard, passando os dados, incluindo os totais calculados
    return render_template(
        'admin/dashboard.html',
        title='Painel Administrativo',
        rooms=admin_rooms, # Passa as salas do admin
        total_participants=total_participants, # Passa o total de participantes
        total_responses=total_responses # Passa o total de respostas
    )

# Função auxiliar para gerar código de sala único
def generate_unique_room_code():
    # Generate a 6-character code using uppercase letters and digits
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        # Check if a room with this code already exists
        existing_room = Room.query.filter_by(code=code).first()
        if not existing_room:
            return code

# Rota para Criar Sala
@admin_bp.route('/create_room', methods=['GET', 'POST'])
@login_required # Garante que um admin está logado
def create_room():
    form = RoomForm()
    if form.validate_on_submit():
        room_name = form.name.data
        # Gerar um código de sala único
        room_code = generate_unique_room_code()

        # Cria o novo objeto Sala
        new_room = Room(name=room_name, code=room_code)

        # Associa a sala ao admin logado
        new_room.admin_id = current_user.id

        db.session.add(new_room)

        # Bloco try...except para o commit
        try:
            db.session.commit() # Tenta salvar as mudanças no DB
            flash('Sala criada com sucesso!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback() # Desfaz a transação em caso de erro
            flash(f'Erro ao criar sala: {e}', 'danger')
            # Opcional: Logar o erro completo do traceback para depuração mais detalhada
            # app.logger.error(f'Erro ao criar sala: {e}', exc_info=True)

    return render_template('admin/create_room.html', title='Criar Nova Sala', form=form)

@admin_bp.route('/room/<int:room_id>/manage', methods=['GET', 'POST'])
@login_required # Restringe o acesso a usuários logados (Admins)
def room_management(room_id):
    # Busca a sala pelo ID ou retorna 404 se não encontrar
    room = Room.query.get_or_404(room_id)

    # Opcional: Verificar se o admin logado é o criador da sala
    # if room.admin_id != current_user.id:
    #     flash('Você não tem permissão para gerenciar esta sala.', 'danger')
    #     return redirect(url_for('admin.dashboard'))

    # Cria uma instância do formulário de pergunta, passando o ID da sala para o campo oculto
    question_form = QuestionForm(room_id=room_id)

    # Processa o formulário de pergunta se for POST e válido
    if request.method == 'POST' and question_form.validate_on_submit():
        new_question = Question(text=question_form.text.data, room_id=room.id) # Cria um novo objeto Question
        db.session.add(new_question) # Adiciona a nova pergunta à sessão do DB
        db.session.commit() # Salva as mudanças no DB
        flash('Pergunta adicionada com sucesso!', 'success') # Mensagem de sucesso
        # Redireciona para a mesma página de gerenciamento para evitar reenvio do formulário
        return redirect(url_for('admin.room_management', room_id=room_id))

    # Carrega as perguntas associadas a esta sala, ordenadas por ID
    questions = Question.query.filter_by(room_id=room.id).order_by(Question.id).all()

    # Renderiza o template de gerenciamento de sala, passando os dados
    return render_template('admin/room_management.html',
                           title=f'Gerenciar Sala: {room.name}',
                           room=room,
                           questions=questions,
                           question_form=question_form) # Passa o formulário para o template

@admin_bp.route('/room/<int:room_id>/toggle_active', methods=['POST'])
@login_required # Restringe o acesso a usuários logados (Admins)
def toggle_room_active(room_id):
    room = Room.query.get_or_404(room_id)
    # Opcional: Verificar se o admin logado é o criador da sala
    # if room.admin_id != current_user.id:
    #     flash('Você não tem permissão para alterar o status desta sala.', 'danger')
    #     return redirect(url_for('admin.dashboard'))

    room.is_active = not room.is_active # Inverte o status de ativo
    db.session.commit() # Salva a mudança no DB
    status = "ativada" if room.is_active else "desativada"
    flash(f'Sala "{room.name}" foi {status}.', 'info') # Mensagem informativa
    # Tenta redirecionar de volta para onde o admin estava (dashboard ou manage)
    referer = request.headers.get("Referer")
    if referer: # Verifica se há um Referer e se contém 'manage' ou 'dashboard'
        if 'manage' in referer:
            return redirect(url_for('admin.room_management', room_id=room_id))
        elif 'dashboard' in referer:
            return redirect(url_for('admin.dashboard'))
    # Redireciona para o dashboard como fallback
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/room/<int:room_id>/delete', methods=['POST'])
@login_required # Restringe o acesso a usuários logados (Admins)
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    # Opcional: Verificar se o admin logado é o criador da sala
    # if room.admin_id != current_user.id:
    #     flash('Você não tem permissão para deletar esta sala.', 'danger')
    #     return redirect(url_for('admin.dashboard'))

    try:
        db.session.delete(room) # Deleta a sala da sessão do DB
        db.session.commit() # Salva as mudanças no DB
        flash(f'Sala "{room.name}" e seus dados associados foram deletados.', 'success') # Mensagem de sucesso
    except Exception as e:
        db.session.rollback() # Reverte a operação em caso de erro
        flash(f'Erro ao deletar sala: {e}', 'danger') # Mensagem de erro
    return redirect(url_for('admin.dashboard')) # Redireciona para o dashboard

@admin_bp.route('/question/<int:question_id>/delete', methods=['POST'])
@login_required # Restringe o acesso a usuários logados (Admins)
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    # Opcional: Verificar se o admin logado é o criador da sala da pergunta
    # if question.room.admin_id != current_user.id:
    #     flash('Você não tem permissão para deletar esta pergunta.', 'danger')
    #     return redirect(url_for('admin.dashboard'))

    room_id = question.room_id # Guarda o ID da sala para redirecionar de volta
    try:
        db.session.delete(question) # Deleta a pergunta da sessão do DB
        db.session.commit() # Salva as mudanças no DB
        flash('Pergunta deletada com sucesso.', 'success') # Mensagem de sucesso
    except Exception as e:
        db.session.rollback() # Reverte a operação em caso de erro
        flash(f'Erro ao deletar pergunta: {e}', 'danger') # Mensagem de erro
    # Redireciona de volta para a página de gerenciamento da sala de onde veio
    return redirect(url_for('admin.room_management', room_id=room_id))


# Rota para Exibir Resultados - COM FILTROS E ESTATÍSTICAS
@admin_bp.route('/room/<int:room_id>/results')
@login_required
def view_results(room_id):
    room = Room.query.get_or_404(room_id)

    # Verifica se o admin logado é o criador da sala (opcional, se reativado)
    # if room.admin_id != current_user.id:
    #     flash('Você não tem permissão para ver os resultados desta sala.', 'danger')
    #     return redirect(url_for('admin.dashboard'))

    # --- Lógica para obter parâmetros de filtro da URL ---
    filter_email = request.args.get('email')
    filter_participant_id = request.args.get('participant_entry_id')
    # --- Fim da Lógica de Filtro ---


    # --- Lógica para construir a query com filtros ---
    participants_in_room_query = Participant.query.filter_by(room_id=room.id)

    if filter_email:
        accounts_with_email = ParticipantAccount.query.filter_by(email=filter_email).all()
        account_ids = [account.id for account in accounts_with_email]
        participants_in_room_query = participants_in_room_query.filter(Participant.account_id.in_(account_ids))

    if filter_participant_id:
        try:
            participant_entry_id_int = int(filter_participant_id)
            participants_in_room_query = participants_in_room_query.filter_by(id=participant_entry_id_int)
        except ValueError:
            flash('ID de participante inválido.', 'warning')

    # Executa a query filtrada para obter as entradas de participante
    participants_in_room = participants_in_room_query.all()
    # --- Fim da Lógica de Query com Filtros ---


    # --- Lógica para calcular as estatísticas dos resultados ---

    # Total de participantes nesta sala (sem filtros aplicados)
    # Para a estatística, queremos o total de participantes na sala,
    # não apenas os que correspondem aos filtros atuais.
    total_participants_in_room = Participant.query.filter_by(room_id=room.id).count()

    # Total de respostas nesta sala (sem filtros aplicados)
    # Conta todas as respostas associadas a perguntas nesta sala
    total_answers_in_room = Answer.query.join(Question).filter(
        Question.room_id == room.id
    ).count()

    # Total de perguntas nesta sala
    total_questions_in_room = Question.query.filter_by(room_id=room.id).count()

    # Taxa de Resposta
    # Se houver participantes e perguntas, calcula a taxa. Evita divisão por zero.
    response_rate = 'N/A'
    if total_participants_in_room > 0 and total_questions_in_room > 0:
        # Taxa de resposta pode ser calculada como (Total Respostas) / (Total Participantes * Total Perguntas) * 100
        # Ou, se cada participante deve responder a cada pergunta: (Total Respostas) / (Total Participantes * Total Perguntas) * 100
        # Ou, se você quer a média de respostas por participante: (Total Respostas) / (Total Participantes)
        # Vou calcular a porcentagem de respostas submetidas em relação ao total possível (participantes * perguntas)
        total_possible_answers = total_participants_in_room * total_questions_in_room
        if total_possible_answers > 0:
             response_rate_percentage = (total_answers_in_room / total_possible_answers) * 100
             response_rate = f'{response_rate_percentage:.2f}%' # Formata para 2 casas decimais
        else:
             response_rate = '0%' # Se não há perguntas ou participantes, a taxa é 0%

    # Última Resposta Submetida
    # Busca a resposta mais recente para esta sala
    last_response_obj = Answer.query.join(Question).filter(
        Question.room_id == room.id
    ).order_by(Answer.submitted_at.desc()).first()

    last_response_time = 'N/A'
    if last_response_obj:
        # Formata a data/hora. Ajuste o formato conforme necessário.
        last_response_time = last_response_obj.submitted_at.strftime('%d/%m/%Y %H:%M')


    # --- Fim da lógica de estatísticas ---


    # Lista para armazenar os resultados formatados para o template (para a tabela/cards de resultados)
    results_list = []

    # Itera sobre cada entrada de participante que passou pelos filtros
    for participant_entry in participants_in_room:
        # Busca o ParticipantAccount associado a esta entrada
        participant_account = ParticipantAccount.query.get(participant_entry.account_id)

        # Busca todas as respostas submetidas por ESTA ENTRADA de participante (participant_entry.id)
        # Ordena por ID da pergunta para exibir na ordem correta
        answers_for_entry = Answer.query.filter_by(participant_id=participant_entry.id).join(Question).order_by(Question.id).all()

        # Adiciona os dados desta entrada (incluindo o email da conta e suas respostas) à lista de resultados
        results_list.append({
            'participant_entry_id': participant_entry.id,
            'participant_email': participant_account.email if participant_account else 'Conta Desconhecida',
            'answers': answers_for_entry
        })

    # Passa a lista de resultados, os valores de filtro atuais e as estatísticas para o template
    return render_template('admin/view_results.html',
                           title=f'Resultados da Sala: {room.name}',
                           room=room,
                           results=results_list,
                           filter_email=filter_email,
                           filter_participant_id=filter_participant_id,
                           # Passa as variáveis de estatística para o template
                           total_participants=total_participants_in_room,
                           total_answers=total_answers_in_room,
                           response_rate=response_rate,
                           last_response=last_response_time
                           )
