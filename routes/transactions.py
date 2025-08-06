from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Transaction, Group, User
from datetime import datetime

bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    type_filter = request.args.get('type')
    status = request.args.get('status')
    group_id = request.args.get('group_id')
    
    query = Transaction.query
    
    if type_filter:
        query = query.filter_by(type=type_filter)
    if status:
        query = query.filter_by(status=status)
    if group_id:
        query = query.filter_by(group_id=group_id)
    
    transactions = query.order_by(Transaction.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    groups = Group.query.all()
    
    return render_template('transactions/index.html', transactions=transactions, groups=groups)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        type_transaction = request.form.get('type')
        amount = request.form.get('amount')
        description = request.form.get('description')
        group_id = request.form.get('group_id')
        due_date = request.form.get('due_date')
        interest_rate = request.form.get('interest_rate')
        loan_term = request.form.get('loan_term')
        
        if not all([type_transaction, amount, group_id]):
            flash('Type, montant et groupe sont obligatoires', 'error')
            return render_template('transactions/create.html')
        
        group = Group.query.get(group_id)
        if not group:
            flash('Groupe invalide', 'error')
            return render_template('transactions/create.html')
        
        # Vérifier que l'utilisateur est membre du groupe
        if current_user not in group.members and current_user.role not in ['admin', 'supervisor', 'animator']:
            flash('Vous devez être membre du groupe pour effectuer une transaction', 'error')
            return render_template('transactions/create.html')
        
        try:
            amount = float(amount)
            interest_rate = float(interest_rate) if interest_rate else 0
            loan_term = int(loan_term) if loan_term else None
            due_date = datetime.strptime(due_date, '%Y-%m-%d') if due_date else None
        except ValueError:
            flash('Format de nombre ou date invalide', 'error')
            return render_template('transactions/create.html')
        
        transaction = Transaction(
            type=type_transaction,
            amount=amount,
            description=description,
            group_id=group_id,
            user_id=current_user.id,
            due_date=due_date,
            interest_rate=interest_rate,
            loan_term=loan_term,
            status='pending'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Transaction créée avec succès!', 'success')
        return redirect(url_for('transactions.index'))
    
    groups = Group.query.filter_by(status='active').all()
    return render_template('transactions/create.html', groups=groups)

@bp.route('/<int:id>')
@login_required
def show(id):
    transaction = Transaction.query.get_or_404(id)
    
    return render_template('transactions/show.html', transaction=transaction)

@bp.route('/<int:id>/approve', methods=['POST'])
@login_required
def approve(id):
    transaction = Transaction.query.get_or_404(id)
    
    # Vérifier les permissions
    if current_user.role not in ['admin', 'supervisor', 'animator'] and transaction.group.created_by != current_user.id:
        flash('Permissions insuffisantes', 'error')
        return redirect(url_for('transactions.show', id=id))
    
    if transaction.status != 'pending':
        flash('Seules les transactions en attente peuvent être approuvées', 'error')
        return redirect(url_for('transactions.show', id=id))
    
    transaction.status = 'approved'
    transaction.approved_by = current_user.id
    transaction.approved_at = datetime.utcnow()
    
    # Mettre à jour les statistiques du groupe
    if transaction.type == 'savings':
        transaction.group.total_savings += transaction.amount
    elif transaction.type == 'loan':
        transaction.group.total_loans += transaction.amount
    
    db.session.commit()
    
    flash('Transaction approuvée avec succès!', 'success')
    return redirect(url_for('transactions.show', id=id))

@bp.route('/<int:id>/reject', methods=['POST'])
@login_required
def reject(id):
    transaction = Transaction.query.get_or_404(id)
    
    # Vérifier les permissions
    if current_user.role not in ['admin', 'supervisor', 'animator'] and transaction.group.created_by != current_user.id:
        flash('Permissions insuffisantes', 'error')
        return redirect(url_for('transactions.show', id=id))
    
    if transaction.status != 'pending':
        flash('Seules les transactions en attente peuvent être rejetées', 'error')
        return redirect(url_for('transactions.show', id=id))
    
    reason = request.form.get('reason', '')
    transaction.status = 'rejected'
    if reason:
        transaction.description = f"{transaction.description or ''}\n\nRaison du rejet: {reason}"
    
    db.session.commit()
    
    flash('Transaction rejetée avec succès!', 'success')
    return redirect(url_for('transactions.show', id=id))

@bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def complete(id):
    transaction = Transaction.query.get_or_404(id)
    
    if transaction.status != 'approved':
        flash('Seules les transactions approuvées peuvent être complétées', 'error')
        return redirect(url_for('transactions.show', id=id))
    
    transaction.status = 'completed'
    db.session.commit()
    
    flash('Transaction complétée avec succès!', 'success')
    return redirect(url_for('transactions.show', id=id))

@bp.route('/stats')
@login_required
def stats():
    period = request.args.get('period', 'month')
    group_id = request.args.get('group_id')
    
    query = Transaction.query.filter_by(status='completed')
    
    if group_id:
        query = query.filter_by(group_id=group_id)
    
    # Filtrer par période
    now = datetime.utcnow()
    if period == 'week':
        start_date = datetime(now.year, now.month, now.day - 7)
    elif period == 'month':
        start_date = datetime(now.year, now.month, 1)
    elif period == 'year':
        start_date = datetime(now.year, 1, 1)
    else:
        start_date = datetime(now.year, now.month, now.day - 30)
    
    query = query.filter(Transaction.created_at >= start_date)
    transactions = query.all()
    
    # Calculer les statistiques
    stats = {
        'total_transactions': len(transactions),
        'total_savings': sum(t.amount for t in transactions if t.type == 'savings'),
        'total_loans': sum(t.amount for t in transactions if t.type == 'loan'),
        'total_repayments': sum(t.amount for t in transactions if t.type == 'repayment'),
        'total_interest': sum(t.amount for t in transactions if t.type == 'interest'),
        'average_amount': sum(t.amount for t in transactions) / len(transactions) if transactions else 0
    }
    
    groups = Group.query.all()
    
    return render_template('transactions/stats.html', stats=stats, groups=groups, period=period) 