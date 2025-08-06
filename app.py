from flask import Flask, render_template, redirect, url_for, flash, request # type: ignore
from flask_login import LoginManager, current_user, login_user, logout_user, login_required # type: ignore
from flask_migrate import Migrate # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
import os
from datetime import datetime
from dotenv import load_dotenv # type: ignore
import logging
from logging.handlers import RotatingFileHandler

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
if not os.path.exists('logs'):
    os.mkdir('logs')

# Initialisation de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///avec.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration de sécurité
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Import des modèles et db
from models import db, User, Cycle, Group, Transaction

# Initialisation des extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

# Import des routes
from routes import auth, cycles, groups, transactions
from routes import notifications

# Enregistrement des blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(cycles.bp)
app.register_blueprint(groups.bp)
app.register_blueprint(transactions.bp)
app.register_blueprint(notifications.bp)

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
    try:
        # Statistiques pour le tableau de bord
        total_cycles = Cycle.query.count()
        total_groups = Group.query.count()
        total_transactions = Transaction.query.count()
        active_cycles = Cycle.query.filter_by(status='active').count()
        
        # Cycles récents
        recent_cycles = Cycle.query.order_by(Cycle.created_at.desc()).limit(5).all()
        
        return render_template('dashboard.html',
                             total_cycles=total_cycles,
                             total_groups=total_groups,
                             total_transactions=total_transactions,
                             active_cycles=active_cycles,
                             recent_cycles=recent_cycles)
    except Exception as e:
        app.logger.error(f"Erreur dashboard: {str(e)}")
        flash('Erreur lors du chargement du tableau de bord', 'error')
        return render_template('dashboard.html',
                             total_cycles=0,
                             total_groups=0,
                             total_transactions=0,
                             active_cycles=0,
                             recent_cycles=[])

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f"Erreur 500: {str(error)}")
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

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