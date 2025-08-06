from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Group, Cycle, User, Transaction
from datetime import datetime

bp = Blueprint('groups', __name__, url_prefix='/groups')

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    cycle_id = request.args.get('cycle_id')
    search = request.args.get('search')
    
    query = Group.query
    
    if status:
        query = query.filter_by(status=status)
    if cycle_id:
        query = query.filter_by(cycle_id=cycle_id)
    if search:
        query = query.filter(Group.name.ilike(f'%{search}%'))
    
    groups = query.order_by(Group.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    cycles = Cycle.query.all()
    
    return render_template('groups/index.html', groups=groups, cycles=cycles)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    # Seuls les admin et animateur peuvent créer des groupes
    if current_user.role not in ['admin', 'animateur']:
        flash('Seuls les administrateurs et animateurs peuvent créer des groupes', 'error')
        return redirect(url_for('groups.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        village = request.form.get('village')
        cycle_id = request.form.get('cycle_id')
        max_members = request.form.get('max_members')
        meeting_location = request.form.get('meeting_location')
        meeting_time = request.form.get('meeting_time')
        contribution_amount = request.form.get('contribution_amount')
        share_value = request.form.get('share_value')
        loan_interest_rate = request.form.get('loan_interest_rate')
        
        if not all([name, cycle_id, village]):
            flash('Nom, cycle et village sont obligatoires', 'error')
            return render_template('groups/create.html')
        
        cycle = Cycle.query.get(cycle_id)
        if not cycle:
            flash('Cycle invalide', 'error')
            return render_template('groups/create.html')
        
        try:
            max_members = int(max_members) if max_members else 25
            contribution_amount = float(contribution_amount) if contribution_amount else 0
            share_value = float(share_value) if share_value else 1000
            loan_interest_rate = float(loan_interest_rate) if loan_interest_rate else 10
        except ValueError:
            flash('Format de nombre invalide', 'error')
            return render_template('groups/create.html')
        
        group = Group(
            name=name,
            description=description,
            village=village,
            cycle_id=cycle_id,
            max_members=max_members,
            meeting_location=meeting_location,
            meeting_time=meeting_time,
            contribution_amount=contribution_amount,
            share_value=share_value,
            loan_interest_rate=loan_interest_rate,
            created_by=current_user.id
        )
        
        db.session.add(group)
        db.session.commit()
        
        flash('Groupe créé avec succès!', 'success')
        return redirect(url_for('groups.index'))
    
    cycles = Cycle.query.filter_by(status='active').all()
    return render_template('groups/create.html', cycles=cycles)

@bp.route('/<int:id>')
@login_required
def show(id):
    group = Group.query.get_or_404(id)
    transactions = group.transactions.order_by(Transaction.created_at.desc()).limit(10).all()
    
    return render_template('groups/show.html', group=group, transactions=transactions)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    group = Group.query.get_or_404(id)
    
    # Seuls les admin, animateur et le créateur du groupe peuvent modifier
    if current_user.role not in ['admin', 'animateur'] and group.created_by != current_user.id:
        flash('Seuls les administrateurs et animateurs peuvent modifier les groupes', 'error')
        return redirect(url_for('groups.show', id=id))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        max_members = request.form.get('max_members')
        meeting_location = request.form.get('meeting_location')
        meeting_time = request.form.get('meeting_time')
        contribution_amount = request.form.get('contribution_amount')
        status = request.form.get('status')
        
        if not name:
            flash('Nom est obligatoire', 'error')
            return render_template('groups/edit.html', group=group)
        
        try:
            max_members = int(max_members) if max_members else 25
            contribution_amount = float(contribution_amount) if contribution_amount else 0
        except ValueError:
            flash('Format de nombre invalide', 'error')
            return render_template('groups/edit.html', group=group)
        
        group.name = name
        group.description = description
        group.max_members = max_members
        group.meeting_location = meeting_location
        group.meeting_time = meeting_time
        group.contribution_amount = contribution_amount
        group.status = status
        
        db.session.commit()
        
        flash('Groupe mis à jour avec succès!', 'success')
        return redirect(url_for('groups.show', id=id))
    
    return render_template('groups/edit.html', group=group)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    group = Group.query.get_or_404(id)
    
    # Seuls les admin peuvent supprimer des groupes
    if current_user.role not in ['admin']:
        flash('Seuls les administrateurs peuvent supprimer des groupes', 'error')
        return redirect(url_for('groups.show', id=id))
    
    if group.current_members > 0:
        flash('Impossible de supprimer un groupe avec des membres', 'error')
        return redirect(url_for('groups.show', id=id))
    
    db.session.delete(group)
    db.session.commit()
    
    flash('Groupe supprimé avec succès!', 'success')
    return redirect(url_for('groups.index'))

@bp.route('/<int:id>/add-member', methods=['GET', 'POST'])
@login_required
def add_member(id):
    group = Group.query.get_or_404(id)
    
    if current_user.role not in ['admin', 'supervisor', 'animator'] and group.created_by != current_user.id:
        flash('Permissions insuffisantes', 'error')
        return redirect(url_for('groups.show', id=id))
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        
        if not user_id:
            flash('Utilisateur requis', 'error')
            return redirect(url_for('groups.add_member', id=id))
        
        user = User.query.get(user_id)
        if not user:
            flash('Utilisateur non trouvé', 'error')
            return redirect(url_for('groups.add_member', id=id))
        
        if user in group.members:
            flash('L\'utilisateur est déjà membre de ce groupe', 'error')
            return redirect(url_for('groups.add_member', id=id))
        
        if not group.can_accept_members():
            flash('Le groupe ne peut plus accepter de nouveaux membres', 'error')
            return redirect(url_for('groups.add_member', id=id))
        
        group.members.append(user)
        group.current_members += 1
        
        if group.current_members >= group.max_members:
            group.status = 'full'
        
        db.session.commit()
        
        flash('Membre ajouté avec succès!', 'success')
        return redirect(url_for('groups.show', id=id))
    
    # Utilisateurs disponibles (non membres du groupe)
    available_users = User.query.filter(
        ~User.id.in_([member.id for member in group.members])
    ).all()
    
    return render_template('groups/add_member.html', group=group, available_users=available_users)

@bp.route('/<int:id>/remove-member/<int:user_id>', methods=['POST'])
@login_required
def remove_member(id, user_id):
    group = Group.query.get_or_404(id)
    
    if current_user.role not in ['admin', 'supervisor', 'animator'] and group.created_by != current_user.id:
        flash('Permissions insuffisantes', 'error')
        return redirect(url_for('groups.show', id=id))
    
    user = User.query.get_or_404(user_id)
    
    if user not in group.members:
        flash('L\'utilisateur n\'est pas membre de ce groupe', 'error')
        return redirect(url_for('groups.show', id=id))
    
    group.members.remove(user)
    group.current_members -= 1
    
    if group.status == 'full' and group.current_members < group.max_members:
        group.status = 'active'
    
    db.session.commit()
    
    flash('Membre retiré avec succès!', 'success')
    return redirect(url_for('groups.show', id=id)) 