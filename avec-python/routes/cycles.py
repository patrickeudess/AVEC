from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Cycle, Group
from datetime import datetime

bp = Blueprint('cycles', __name__, url_prefix='/cycles')

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Cycle.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    cycles = query.order_by(Cycle.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('cycles/index.html', cycles=cycles, status_filter=status_filter)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        target_amount = request.form.get('target_amount', 0, type=float)
        interest_rate = request.form.get('interest_rate', 0, type=float)
        meeting_frequency = request.form.get('meeting_frequency', 'weekly')
        meeting_day = request.form.get('meeting_day')
        start_date_str = request.form.get('start_date')
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = None
        
        cycle = Cycle(
            name=name,
            description=description,
            target_amount=target_amount,
            interest_rate=interest_rate,
            meeting_frequency=meeting_frequency,
            meeting_day=meeting_day,
            start_date=start_date
        )
        
        db.session.add(cycle)
        db.session.commit()
        
        flash('Cycle créé avec succès !', 'success')
        return redirect(url_for('cycles.index'))
    
    return render_template('cycles/create.html')

@bp.route('/<int:id>')
@login_required
def show(id):
    cycle = Cycle.query.get_or_404(id)
    groups = cycle.groups.all()
    return render_template('cycles/show.html', cycle=cycle, groups=groups)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    cycle = Cycle.query.get_or_404(id)
    
    if request.method == 'POST':
        cycle.name = request.form.get('name')
        cycle.description = request.form.get('description')
        cycle.target_amount = request.form.get('target_amount', 0, type=float)
        cycle.interest_rate = request.form.get('interest_rate', 0, type=float)
        cycle.meeting_frequency = request.form.get('meeting_frequency', 'weekly')
        cycle.meeting_day = request.form.get('meeting_day')
        
        start_date_str = request.form.get('start_date')
        if start_date_str:
            cycle.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        db.session.commit()
        flash('Cycle modifié avec succès !', 'success')
        return redirect(url_for('cycles.show', id=cycle.id))
    
    return render_template('cycles/edit.html', cycle=cycle)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    cycle = Cycle.query.get_or_404(id)
    db.session.delete(cycle)
    db.session.commit()
    flash('Cycle supprimé avec succès !', 'success')
    return redirect(url_for('cycles.index'))

@bp.route('/<int:id>/next-phase', methods=['POST'])
@login_required
def next_phase(id):
    cycle = Cycle.query.get_or_404(id)
    if cycle.next_phase():
        db.session.commit()
        flash('Phase du cycle avancée avec succès !', 'success')
    else:
        flash('Le cycle est déjà à sa phase finale.', 'info')
    return redirect(url_for('cycles.show', id=cycle.id)) 