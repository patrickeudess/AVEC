from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Transaction, Group, User
from datetime import datetime

bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    group_filter = request.args.get('group_id', '', type=int)
    
    query = Transaction.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if type_filter:
        query = query.filter_by(type=type_filter)
    
    if group_filter:
        query = query.filter_by(group_id=group_filter)
    
    transactions = query.order_by(Transaction.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    groups = Group.query.all()
    
    return render_template('transactions/index.html', 
                         transactions=transactions,
                         status_filter=status_filter,
                         type_filter=type_filter,
                         group_filter=group_filter,
                         groups=groups)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    groups = Group.query.filter_by(status='active').all()
    
    if request.method == 'POST':
        group_id = request.form.get('group_id', type=int)
        type_transaction = request.form.get('type')
        amount = request.form.get('amount', 0, type=float)
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        interest_rate = request.form.get('interest_rate', 0, type=float)
        loan_term = request.form.get('loan_term', type=int)
        
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        else:
            due_date = None
        
        transaction = Transaction(
            group_id=group_id,
            user_id=current_user.id,
            type=type_transaction,
            amount=amount,
            description=description,
            due_date=due_date,
            interest_rate=interest_rate,
            loan_term=loan_term
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Transaction créée avec succès !', 'success')
        return redirect(url_for('transactions.index'))
    
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
    
    if transaction.status == 'pending':
        transaction.approve(current_user)
        db.session.commit()
        flash('Transaction approuvée avec succès !', 'success')
    else:
        flash('Cette transaction ne peut pas être approuvée.', 'error')
    
    return redirect(url_for('transactions.show', id=transaction.id))

@bp.route('/<int:id>/reject', methods=['POST'])
@login_required
def reject(id):
    transaction = Transaction.query.get_or_404(id)
    
    if transaction.status == 'pending':
        transaction.reject()
        db.session.commit()
        flash('Transaction rejetée !', 'success')
    else:
        flash('Cette transaction ne peut pas être rejetée.', 'error')
    
    return redirect(url_for('transactions.show', id=transaction.id))

@bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def complete(id):
    transaction = Transaction.query.get_or_404(id)
    
    if transaction.status == 'approved':
        transaction.complete()
        db.session.commit()
        flash('Transaction terminée avec succès !', 'success')
    else:
        flash('Cette transaction ne peut pas être terminée.', 'error')
    
    return redirect(url_for('transactions.show', id=transaction.id))

@bp.route('/stats')
@login_required
def stats():
    # Statistiques des transactions
    total_transactions = Transaction.query.count()
    pending_transactions = Transaction.query.filter_by(status='pending').count()
    approved_transactions = Transaction.query.filter_by(status='approved').count()
    completed_transactions = Transaction.query.filter_by(status='completed').count()
    
    # Montants par type
    total_savings = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        type='savings', status='approved').scalar() or 0
    total_loans = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        type='loan', status='approved').scalar() or 0
    total_repayments = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        type='repayment', status='completed').scalar() or 0
    
    # Transactions récentes
    recent_transactions = Transaction.query.order_by(
        Transaction.created_at.desc()).limit(10).all()
    
    return render_template('transactions/stats.html',
                         total_transactions=total_transactions,
                         pending_transactions=pending_transactions,
                         approved_transactions=approved_transactions,
                         completed_transactions=completed_transactions,
                         total_savings=total_savings,
                         total_loans=total_loans,
                         total_repayments=total_repayments,
                         recent_transactions=recent_transactions) 