from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Cycle, Group
from datetime import datetime

bp = Blueprint('cycles', __name__, url_prefix='/cycles')

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    phase = request.args.get('phase')
    search = request.args.get('search')
    
    query = Cycle.query
    
    if status:
        query = query.filter_by(status=status)
    if phase:
        query = query.filter_by(phase=phase)
    if search:
        query = query.filter(Cycle.name.ilike(f'%{search}%'))
    
    cycles = query.order_by(Cycle.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('cycles/index.html', cycles=cycles)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        target_amount = request.form.get('target_amount')
        interest_rate = request.form.get('interest_rate')
        meeting_frequency = request.form.get('meeting_frequency')
        meeting_day = request.form.get('meeting_day')
        
        if not all([name, start_date]):
            flash('Nom et date de début sont obligatoires', 'error')
            return render_template('cycles/create.html')
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            target_amount = float(target_amount) if target_amount else 0
            interest_rate = float(interest_rate) if interest_rate else 0
        except ValueError:
            flash('Format de date ou de nombre invalide', 'error')
            return render_template('cycles/create.html')
        
        cycle = Cycle(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            target_amount=target_amount,
            interest_rate=interest_rate,
            meeting_frequency=meeting_frequency or 'weekly',
            meeting_day=meeting_day,
            created_by=current_user.id
        )
        
        db.session.add(cycle)
        db.session.commit()
        
        flash('Cycle créé avec succès!', 'success')
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
    
    if current_user.role not in ['admin', 'supervisor'] and cycle.created_by != current_user.id:
        flash('Permissions insuffisantes', 'error')
        return redirect(url_for('cycles.show', id=id))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        target_amount = request.form.get('target_amount')
        interest_rate = request.form.get('interest_rate')
        status = request.form.get('status')
        phase = request.form.get('phase')
        meeting_frequency = request.form.get('meeting_frequency')
        meeting_day = request.form.get('meeting_day')
        
        if not all([name, start_date]):
            flash('Nom et date de début sont obligatoires', 'error')
            return render_template('cycles/edit.html', cycle=cycle)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            target_amount = float(target_amount) if target_amount else 0
            interest_rate = float(interest_rate) if interest_rate else 0
        except ValueError:
            flash('Format de date ou de nombre invalide', 'error')
            return render_template('cycles/edit.html', cycle=cycle)
        
        cycle.name = name
        cycle.description = description
        cycle.start_date = start_date
        cycle.end_date = end_date
        cycle.target_amount = target_amount
        cycle.interest_rate = interest_rate
        cycle.status = status
        cycle.phase = phase
        cycle.meeting_frequency = meeting_frequency
        cycle.meeting_day = meeting_day
        
        db.session.commit()
        
        flash('Cycle mis à jour avec succès!', 'success')
        return redirect(url_for('cycles.show', id=id))
    
    return render_template('cycles/edit.html', cycle=cycle)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    cycle = Cycle.query.get_or_404(id)
    
    if current_user.role not in ['admin', 'supervisor'] and cycle.created_by != current_user.id:
        flash('Permissions insuffisantes', 'error')
        return redirect(url_for('cycles.show', id=id))
    
    # Vérifier s'il y a des groupes actifs
    active_groups = cycle.groups.filter_by(status='active').count()
    if active_groups > 0:
        flash('Impossible de supprimer un cycle avec des groupes actifs', 'error')
        return redirect(url_for('cycles.show', id=id))
    
    db.session.delete(cycle)
    db.session.commit()
    
    flash('Cycle supprimé avec succès!', 'success')
    return redirect(url_for('cycles.index'))

@bp.route('/<int:id>/next-phase', methods=['POST'])
@login_required
def next_phase(id):
    cycle = Cycle.query.get_or_404(id)
    
    if current_user.role not in ['admin', 'supervisor', 'animator'] and cycle.created_by != current_user.id:
        flash('Permissions insuffisantes', 'error')
        return redirect(url_for('cycles.show', id=id))
    
    if cycle.phase == 'completed':
        flash('Le cycle est déjà terminé', 'error')
        return redirect(url_for('cycles.show', id=id))
    
    phases = ['preparation', 'formation', 'supervision', 'completed']
    current_index = phases.index(cycle.phase)
    
    if current_index < len(phases) - 1:
        cycle.phase = phases[current_index + 1]
        db.session.commit()
        flash('Cycle passé à la phase suivante!', 'success')
    else:
        flash('Le cycle est déjà à sa dernière phase', 'error')
    
    return redirect(url_for('cycles.show', id=id)) 