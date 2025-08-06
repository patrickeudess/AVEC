from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, User, Cycle, Group, Transaction
from datetime import datetime, timedelta
import json

bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@bp.route('/')
@login_required
def index():
    """Afficher toutes les notifications de l'utilisateur"""
    notifications = get_user_notifications(current_user.id)
    return render_template('notifications/index.html', notifications=notifications)

@bp.route('/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_read(notification_id):
    """Marquer une notification comme lue"""
    # Ici vous pourriez implémenter un système de notifications en base
    return jsonify({'success': True})

@bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Marquer toutes les notifications comme lues"""
    return jsonify({'success': True})

@bp.route('/api/unread-count')
@login_required
def unread_count():
    """API pour obtenir le nombre de notifications non lues"""
    count = get_unread_count(current_user.id)
    return jsonify({'count': count})

def get_user_notifications(user_id):
    """Récupérer les notifications de l'utilisateur"""
    notifications = []
    
    # Notifications de cycles
    cycles = Cycle.query.filter_by(created_by=user_id).all()
    for cycle in cycles:
        if cycle.status == 'active' and cycle.end_date:
            days_remaining = (cycle.end_date - datetime.utcnow()).days
            if days_remaining <= 7 and days_remaining > 0:
                notifications.append({
                    'id': f'cycle_{cycle.id}',
                    'type': 'warning',
                    'title': f'Cycle "{cycle.name}" se termine bientôt',
                    'message': f'Il reste {days_remaining} jour(s) avant la fin du cycle.',
                    'date': cycle.end_date,
                    'url': url_for('cycles.show', id=cycle.id)
                })
    
    # Notifications de groupes
    user = User.query.get(user_id)
    for group in user.groups:
        if group.status == 'active':
            # Vérifier les transactions en retard
            overdue_transactions = Transaction.query.filter_by(
                group_id=group.id,
                user_id=user_id,
                status='pending'
            ).filter(Transaction.due_date < datetime.utcnow()).count()
            
            if overdue_transactions > 0:
                notifications.append({
                    'id': f'group_{group.id}_overdue',
                    'type': 'danger',
                    'title': f'Transactions en retard dans "{group.name}"',
                    'message': f'Vous avez {overdue_transactions} transaction(s) en retard.',
                    'date': datetime.utcnow(),
                    'url': url_for('transactions.index', group_id=group.id)
                })
    
    # Notifications de transactions
    pending_transactions = Transaction.query.filter_by(
        user_id=user_id,
        status='pending'
    ).all()
    
    for transaction in pending_transactions:
        if transaction.due_date and transaction.due_date < datetime.utcnow():
                            notifications.append({
                    'id': f'transaction_{transaction.id}_overdue',
                    'type': 'danger',
                    'title': 'Transaction en retard',
                    'message': f'Transaction de {transaction.amount} FCFA en retard depuis {(datetime.utcnow() - transaction.due_date).days} jour(s).',
                    'date': transaction.due_date,
                    'url': url_for('transactions.show', id=transaction.id)
                })
    
    # Trier par date (plus récentes en premier)
    notifications.sort(key=lambda x: x['date'], reverse=True)
    return notifications

def get_unread_count(user_id):
    """Obtenir le nombre de notifications non lues"""
    notifications = get_user_notifications(user_id)
    return len(notifications)

def create_notification(user_id, notification_type, title, message, url=None):
    """Créer une nouvelle notification"""
    # Ici vous pourriez sauvegarder en base de données
    notification = {
        'id': f'notif_{datetime.utcnow().timestamp()}',
        'type': notification_type,
        'title': title,
        'message': message,
        'date': datetime.utcnow(),
        'url': url
    }
    return notification 