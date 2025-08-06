from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialisation de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///avec.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import des modèles et db
from models import db, User, Cycle, Group, Transaction, Organization

# Initialisation des extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

# Import des routes
from routes import auth, cycles, groups, transactions, organizations

# Enregistrement des blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(cycles.bp)
app.register_blueprint(groups.bp)
app.register_blueprint(transactions.bp)
app.register_blueprint(organizations.bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Statistiques pour le tableau de bord
    if current_user.role == 'admin':
        # Admin global - voir toutes les organisations
        total_organizations = Organization.query.count()
        total_cycles = Cycle.query.count()
        total_groups = Group.query.count()
        total_transactions = Transaction.query.count()
        active_cycles = Cycle.query.filter_by(status='active').count()
        recent_cycles = Cycle.query.order_by(Cycle.created_at.desc()).limit(5).all()
    else:
        # Utilisateur d'organisation - voir seulement ses données
        total_organizations = 1 if current_user.organization else 0
        total_cycles = Cycle.query.filter_by(organization_id=current_user.organization_id).count() if current_user.organization_id else 0
        total_groups = Group.query.join(Cycle).filter(Cycle.organization_id == current_user.organization_id).count() if current_user.organization_id else 0
        total_transactions = Transaction.query.join(Group).join(Cycle).filter(Cycle.organization_id == current_user.organization_id).count() if current_user.organization_id else 0
        active_cycles = Cycle.query.filter_by(status='active', organization_id=current_user.organization_id).count() if current_user.organization_id else 0
        recent_cycles = Cycle.query.filter_by(organization_id=current_user.organization_id).order_by(Cycle.created_at.desc()).limit(5).all() if current_user.organization_id else []
    
    return render_template('dashboard.html',
                        total_organizations=total_organizations,
                        total_cycles=total_cycles,
                        total_groups=total_groups,
                        total_transactions=total_transactions,
                        active_cycles=active_cycles,
                        recent_cycles=recent_cycles)

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Créer un utilisateur admin par défaut s'il n'existe pas
        admin = User.query.filter_by(email='admin@avec.com').first()
        if not admin:
            admin = User(
                first_name='Admin',
                last_name='AVEC',
                email='admin@avec.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                status='active'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Utilisateur admin créé : admin@avec.com / admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 