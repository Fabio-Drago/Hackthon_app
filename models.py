# models.py
# REMOVA: from flask_sqlalchemy import SQLAlchemy # Não precisamos mais inicializar aqui
from werkzeug.security import generate_password_hash, check_password_hash
# Manter UserMixin para Admin. ParticipanteAccount terá login customizado ou UserMixin se aplicável.
from flask_login import UserMixin
import datetime

# ### IMPORTA A INSTÂNCIA 'db' DO SEU ARQUIVO app.py ###
# Esta é a instância SQLAlchemy que foi inicializada no topo do app.py
# Esta importação está correta para o padrão de fábrica, desde que models
# seja importado DENTRO da fábrica em app.py, depois que db.init_app(app)
# foi chamado.
from app import db
# ### FIM DA IMPORTAÇÃO ###


# Modelo para Administradores (usando Flask-Login)
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Flask-Login user loader usa este método para obter o ID do usuário
    def get_id(self):
        return str(self.id)

    # Permite verificar se o objeto representa um admin autenticado pelo Flask-Login
    @property
    def is_authenticated(self):
        return True # Para Admin, sempre True se o objeto existir após load_user

    @property
    def is_active(self):
        return True # Admins estão sempre ativos no contexto deste app

    @property
    def is_anonymous(self):
        return False # Admins não são anônimos quando logados


    def __repr__(self):
        return f'<Admin {self.username}>'

# === NOVO MODELO PARA CONTAS DE PARTICIPANTE ===
# Não usaremos UserMixin do Flask-Login para ParticipantAccount,
# pois o Flask-Login é mais simples com um único tipo de usuário ativo por vez.
# Faremos o controle de sessão para ParticipantAccount manualmente.
class ParticipantAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relação reversa para ver todas as entradas (participações em salas) desta conta
    # 'participations' é o nome da lista de objetos Participant associados a esta conta
    participations = db.relationship('Participant', backref='account', lazy='dynamic', cascade="all, delete-orphan")


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<ParticipantAccount {self.email}>'


# Modelo para Salas
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(6), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    admin = db.relationship('Admin', backref=db.backref('rooms', lazy=True))

    # Relação com Perguntas (cascade garante que perguntas sejam deletadas com a sala)
    questions = db.relationship('Question', backref='room', lazy='dynamic', cascade="all, delete-orphan")
    # Relação com Participantes (cascade garante que PARTICIPAÇÕES sejam deletadas com a sala)
    # AQUI, 'participants' agora se refere às entradas Participant nesta sala
    participants = db.relationship('Participant', backref='room', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Room {self.name} ({self.code})>'

# Modelo para Participantes (Representa a ENTRADA de uma ParticipantAccount em uma sala)
class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Removido 'name' daqui, pois o nome virá da ParticipantAccount ou será re-introduzido se necessário
    # name = db.Column(db.String(100), nullable=False) # << REMOVIDO >>

    # === NOVA CHAVE ESTRANGEIRA VINCULANDO À ParticipantAccount ===
    account_id = db.Column(db.Integer, db.ForeignKey('participant_account.id'), nullable=False)
    # === FIM NOVA CHAVE ESTRANGEIRA ===

    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relação com Respostas (sem cascade aqui, pois respostas são deletadas com o participante pela relação no modelo Participant)
    answers = db.relationship('Answer', backref='participant', lazy='dynamic')

    def __repr__(self):
        # Representação agora usa o email da conta associada
        return f'<Participant {self.account.email} in Room {self.room_id}>'


# Modelo para Perguntas
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    # Relação com Respostas (cascade garante que respostas sejam deletadas com a pergunta)
    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Question {self.id} for Room {self.room_id}>'

# Modelo para Respostas
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

    def __repr__(self):
        return f'<Answer by Participant {self.participant_id} for Question {self.question_id}>'

# === NOVO MODELO PARA SUBSCRIBERS DA NEWSLETTER (Adicionado) ===
# Em models.py (trecho do modelo Subscriber)
# ... outras importações e modelos ...

# === MODELO PARA SUBSCRIBERS DA NEWSLETTER ===
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=True) # Adicione este campo se quiser armazenar o nome
    subscribed_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False) # <<< CAMPO NECESSÁRIO >>>
    confirmed_at = db.Column(db.DateTime, nullable=True) # <<< CAMPO NECESSÁRIO >>>


    def __repr__(self):
        return f'<Subscriber {self.email}>'
# === FIM NOVO MODELO ===
