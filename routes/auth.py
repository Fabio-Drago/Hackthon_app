# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Admin
from werkzeug.security import check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

auth_bp = Blueprint('auth', __name__)

# Formulário de Login com Flask-WTF
class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se o admin já estiver logado, redireciona para o dashboard
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin) # Realiza o login
            flash('Login bem-sucedido!', 'success')
            # Redireciona para a página que o usuário tentou acessar ou para o dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    return render_template('admin/login.html', title='Login Admin', form=form)

@auth_bp.route('/logout')
@login_required # Só pode deslogar quem está logado
def logout():
    logout_user() # Realiza o logout
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))