from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email et mot de passe requis', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.status != 'active':
                flash('Compte utilisateur inactif', 'error')
                return render_template('auth/login.html')
            
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard')
            
            flash('Connexion réussie!', 'success')
            return redirect(next_page)
        else:
            flash('Email ou mot de passe incorrect', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        if not all([first_name, last_name, email, password]):
            flash('Tous les champs obligatoires doivent être remplis', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Un utilisateur avec cet email existe déjà', 'error')
            return render_template('auth/register.html')
        
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            village=request.form.get('village'),
            role=request.form.get('role', 'member')
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))

@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('Tous les champs sont requis', 'error')
            return render_template('auth/change_password.html')
        
        if not current_user.check_password(current_password):
            flash('Mot de passe actuel incorrect', 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('Les nouveaux mots de passe ne correspondent pas', 'error')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 6:
            flash('Le nouveau mot de passe doit contenir au moins 6 caractères', 'error')
            return render_template('auth/change_password.html')
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Mot de passe modifié avec succès!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html')

@bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    
    if not first_name or not last_name:
        flash('Prénom et nom sont requis', 'error')
        return redirect(url_for('auth.profile'))
    
    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.phone = phone
    
    db.session.commit()
    
    flash('Profil mis à jour avec succès!', 'success')
    return redirect(url_for('auth.profile')) 