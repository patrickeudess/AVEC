from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Group, Cycle, User
from datetime import datetime

bp = Blueprint('groups', __name__, url_prefix='/groups')

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    cycle_filter = request.args.get('cycle_id', '', type=int)
    
    query = Group.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if cycle_filter:
        query = query.filter_by(cycle_id=cycle_filter)
    
    groups = query.order_by(Group.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    cycles = Cycle.query.all()
    
    return render_template('groups/index.html', 
                         groups=groups, 
                         status_filter=status_filter,
                         cycle_filter=cycle_filter,
                         cycles=cycles)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    cycles = Cycle.query.filter_by(status='active').all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        cycle_id = request.form.get('cycle_id', type=int)
        max_members = request.form.get('max_members', 25, type=int)
        contribution_amount = request.form.get('contribution_amount', 0, type=float)
        meeting_location = request.form.get('meeting_location')
        meeting_time_str = request.form.get('meeting_time')
        
        if meeting_time_str:
            meeting_time = datetime.strptime(meeting_time_str, '%H:%M').time()
        else:
            meeting_time = None
        
        group = Group(
            name=name,
            description=description,
            cycle_id=cycle_id,
            creator_id=current_user.id,
            max_members=max_members,
            contribution_amount=contribution_amount,
            meeting_location=meeting_location,
            meeting_time=meeting_time
        )
        
        db.session.add(group)
        db.session.commit()
        
        flash('Groupe créé avec succès !', 'success')
        return redirect(url_for('groups.index'))
    
    return render_template('groups/create.html', cycles=cycles)

@bp.route('/<int:id>')
@login_required
def show(id):
    group = Group.query.get_or_404(id)
    members = group.members.all()
    recent_transactions = group.transactions.order_by(
        db.desc('created_at')).limit(10).all()
    return render_template('groups/show.html', 
                         group=group, 
                         members=members,
                         recent_transactions=recent_transactions)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    group = Group.query.get_or_404(id)
    cycles = Cycle.query.all()
    
    if request.method == 'POST':
        group.name = request.form.get('name')
        group.description = request.form.get('description')
        group.cycle_id = request.form.get('cycle_id', type=int)
        group.max_members = request.form.get('max_members', 25, type=int)
        group.contribution_amount = request.form.get('contribution_amount', 0, type=float)
        group.meeting_location = request.form.get('meeting_location')
        
        meeting_time_str = request.form.get('meeting_time')
        if meeting_time_str:
            group.meeting_time = datetime.strptime(meeting_time_str, '%H:%M').time()
        
        db.session.commit()
        flash('Groupe modifié avec succès !', 'success')
        return redirect(url_for('groups.show', id=group.id))
    
    return render_template('groups/edit.html', group=group, cycles=cycles)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    group = Group.query.get_or_404(id)
    db.session.delete(group)
    db.session.commit()
    flash('Groupe supprimé avec succès !', 'success')
    return redirect(url_for('groups.index'))

@bp.route('/<int:id>/add-member', methods=['GET', 'POST'])
@login_required
def add_member(id):
    group = Group.query.get_or_404(id)
    
    if request.method == 'POST':
        user_id = request.form.get('user_id', type=int)
        user = User.query.get(user_id)
        
        if user and group.add_member(user):
            db.session.commit()
            flash(f'{user.get_full_name()} ajouté au groupe !', 'success')
        else:
            flash('Impossible d\'ajouter ce membre.', 'error')
        
        return redirect(url_for('groups.show', id=group.id))
    
    # Utilisateurs disponibles (pas encore dans le groupe)
    group_member_ids = [member.id for member in group.members.all()]
    available_users = User.query.filter(
        ~User.id.in_(group_member_ids) if group_member_ids else True
    ).all()
    
    return render_template('groups/add_member.html', 
                         group=group, 
                         available_users=available_users)

@bp.route('/<int:id>/remove-member/<int:user_id>', methods=['POST'])
@login_required
def remove_member(id, user_id):
    group = Group.query.get_or_404(id)
    user = User.query.get_or_404(user_id)
    
    if group.remove_member(user):
        db.session.commit()
        flash(f'{user.get_full_name()} retiré du groupe !', 'success')
    else:
        flash('Impossible de retirer ce membre.', 'error')
    
    return redirect(url_for('groups.show', id=group.id)) 