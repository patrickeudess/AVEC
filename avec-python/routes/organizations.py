from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Organization, User, Cycle, Group, Transaction
from datetime import datetime

bp = Blueprint('organizations', __name__, url_prefix='/organizations')

@bp.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        organizations = Organization.query.all()
    else:
        organizations = [current_user.organization] if current_user.organization else []
    
    return render_template('organizations/index.html', organizations=organizations)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role != 'admin':
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('organizations.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        address = request.form.get('address')
        phone = request.form.get('phone')
        email = request.form.get('email')
        website = request.form.get('website')
        
        organization = Organization(
            name=name,
            description=description,
            address=address,
            phone=phone,
            email=email,
            website=website
        )
        
        db.session.add(organization)
        db.session.commit()
        
        flash('Organisation créée avec succès !', 'success')
        return redirect(url_for('organizations.index'))
    
    return render_template('organizations/create.html')

@bp.route('/<int:id>')
@login_required
def show(id):
    organization = Organization.query.get_or_404(id)
    
    # Vérifier les permissions
    if current_user.role != 'admin' and current_user.organization_id != id:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('organizations.index'))
    
    # Statistiques de l'organisation
    total_cycles = organization.cycles.count()
    total_groups = organization.get_total_groups()
    total_members = organization.get_total_members()
    total_savings = organization.get_total_savings()
    total_loans = organization.get_total_loans()
    
    # Cycles récents
    recent_cycles = organization.cycles.order_by(Cycle.created_at.desc()).limit(5).all()
    
    # Groupes récents
    recent_groups = []
    for cycle in organization.cycles.all():
        recent_groups.extend(cycle.groups.order_by(Group.created_at.desc()).limit(3).all())
    recent_groups = sorted(recent_groups, key=lambda x: x.created_at, reverse=True)[:5]
    
    return render_template('organizations/show.html',
                         organization=organization,
                         total_cycles=total_cycles,
                         total_groups=total_groups,
                         total_members=total_members,
                         total_savings=total_savings,
                         total_loans=total_loans,
                         recent_cycles=recent_cycles,
                         recent_groups=recent_groups)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    organization = Organization.query.get_or_404(id)
    
    # Vérifier les permissions
    if current_user.role != 'admin' and current_user.organization_id != id:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('organizations.index'))
    
    if request.method == 'POST':
        organization.name = request.form.get('name')
        organization.description = request.form.get('description')
        organization.address = request.form.get('address')
        organization.phone = request.form.get('phone')
        organization.email = request.form.get('email')
        organization.website = request.form.get('website')
        
        db.session.commit()
        flash('Organisation modifiée avec succès !', 'success')
        return redirect(url_for('organizations.show', id=organization.id))
    
    return render_template('organizations/edit.html', organization=organization)

@bp.route('/<int:id>/users')
@login_required
def users(id):
    organization = Organization.query.get_or_404(id)
    
    # Vérifier les permissions
    if current_user.role != 'admin' and current_user.organization_id != id:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('organizations.index'))
    
    users = organization.users.all()
    return render_template('organizations/users.html', organization=organization, users=users)

@bp.route('/<int:id>/reports')
@login_required
def reports(id):
    organization = Organization.query.get_or_404(id)
    
    # Vérifier les permissions
    if current_user.role != 'admin' and current_user.organization_id != id:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('organizations.index'))
    
    # Générer les rapports
    cycles_data = []
    for cycle in organization.cycles.all():
        cycle_data = {
            'cycle': cycle,
            'groups_count': cycle.groups.count(),
            'total_members': sum(group.current_members for group in cycle.groups.all()),
            'total_savings': sum(group.total_savings for group in cycle.groups.all()),
            'total_loans': sum(group.total_loans for group in cycle.groups.all())
        }
        cycles_data.append(cycle_data)
    
    return render_template('organizations/reports.html', 
                         organization=organization,
                         cycles_data=cycles_data) 