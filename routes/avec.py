from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, User, Cycle, Group, Transaction, FormationModule, CommunityEvaluation, Meeting
from datetime import datetime, timedelta

bp = Blueprint('avec', __name__, url_prefix='/avec')

@bp.route('/community-evaluation', methods=['GET', 'POST'])
@login_required
def community_evaluation():
    """Évaluation et sélection de la communauté - Phase préparatoire"""
    if current_user.role not in ['admin', 'animateur']:
        flash('Accès réservé aux animateurs', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        village_name = request.form.get('village_name')
        population = request.form.get('population')
        main_activities = request.form.get('main_activities')
        existing_groups = request.form.get('existing_groups')
        needs_assessment = request.form.get('needs_assessment')
        community_interest = request.form.get('community_interest') == 'on'
        
        evaluation = CommunityEvaluation(
            village_name=village_name,
            population=population,
            main_activities=main_activities,
            existing_groups=existing_groups,
            needs_assessment=needs_assessment,
            community_interest=community_interest,
            evaluated_by=current_user.id
        )
        
        db.session.add(evaluation)
        db.session.commit()
        
        flash('Évaluation de communauté enregistrée avec succès!', 'success')
        return redirect(url_for('avec.community_evaluations'))
    
    return render_template('avec/community_evaluation.html')

@bp.route('/community-evaluations')
@login_required
def community_evaluations():
    """Liste des évaluations de communautés"""
    if current_user.role not in ['admin', 'animateur']:
        flash('Accès réservé aux animateurs', 'error')
        return redirect(url_for('dashboard'))
    
    evaluations = CommunityEvaluation.query.order_by(CommunityEvaluation.evaluation_date.desc()).all()
    return render_template('avec/community_evaluations.html', evaluations=evaluations)

@bp.route('/group/<int:group_id>/shares')
@login_required
def group_shares(group_id):
    """Gestion des parts du groupe AVEC"""
    group = Group.query.get_or_404(group_id)
    
    if current_user not in group.members and current_user.role not in ['admin', 'animateur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('dashboard'))
    
    # Calculer les parts de chaque membre
    members_shares = {}
    for member in group.members:
        shares = group.get_member_shares(member.id)
        members_shares[member.id] = shares
    
    total_shares = group.get_total_shares()
    
    return render_template('avec/group_shares.html', 
                         group=group, 
                         members_shares=members_shares,
                         total_shares=total_shares)

@bp.route('/group/<int:group_id>/shares/purchase', methods=['POST'])
@login_required
def purchase_shares(group_id):
    """Acheter des parts - Réunion d'épargne"""
    group = Group.query.get_or_404(group_id)
    
    if current_user not in group.members:
        flash('Seuls les membres peuvent acheter des parts', 'error')
        return redirect(url_for('avec.group_shares', group_id=group_id))
    
    amount = request.form.get('amount')
    meeting_date = request.form.get('meeting_date')
    witnesses = request.form.get('witnesses')
    
    if not amount or not meeting_date:
        flash('Montant et date de réunion requis', 'error')
        return redirect(url_for('avec.group_shares', group_id=group_id))
    
    try:
        amount = float(amount)
        meeting_date = datetime.strptime(meeting_date, '%Y-%m-%d')
    except ValueError:
        flash('Format de montant ou date invalide', 'error')
        return redirect(url_for('avec.group_shares', group_id=group_id))
    
    # Vérifier que le montant est un multiple de la valeur de part
    if amount % group.share_value != 0:
        flash(f'Le montant doit être un multiple de {group.share_value} FCFA (valeur d\'une part)', 'error')
        return redirect(url_for('avec.group_shares', group_id=group_id))
    
    transaction = Transaction(
        type='shares_purchase',
        amount=amount,
        description=f'Achat de {amount / group.share_value} part(s)',
        group_id=group_id,
        user_id=current_user.id,
        status='completed',
        witnesses=witnesses,
        meeting_date=meeting_date
    )
    
    group.total_savings += amount
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'Achat de {amount / group.share_value} part(s) enregistré!', 'success')
    return redirect(url_for('avec.group_shares', group_id=group_id))

@bp.route('/group/<int:group_id>/meetings')
@login_required
def group_meetings(group_id):
    """Gestion des réunions du groupe"""
    group = Group.query.get_or_404(group_id)
    
    if current_user not in group.members and current_user.role not in ['admin', 'animateur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('dashboard'))
    
    meetings = Meeting.query.filter_by(group_id=group_id).order_by(Meeting.meeting_date.desc()).all()
    return render_template('avec/group_meetings.html', group=group, meetings=meetings)

@bp.route('/group/<int:group_id>/meetings/create', methods=['GET', 'POST'])
@login_required
def create_meeting(group_id):
    """Créer une nouvelle réunion"""
    group = Group.query.get_or_404(group_id)
    
    if current_user.role not in ['admin', 'animateur'] and current_user not in [group.get_president(), group.get_secretary()]:
        flash('Seuls les membres du comité peuvent créer des réunions', 'error')
        return redirect(url_for('avec.group_meetings', group_id=group_id))
    
    if request.method == 'POST':
        meeting_date = request.form.get('meeting_date')
        meeting_type = request.form.get('meeting_type')
        agenda = request.form.get('agenda')
        attendees_count = request.form.get('attendees_count')
        
        if not meeting_date:
            flash('Date de réunion requise', 'error')
            return render_template('avec/create_meeting.html', group=group)
        
        try:
            meeting_date = datetime.strptime(meeting_date, '%Y-%m-%d %H:%M')
            attendees_count = int(attendees_count) if attendees_count else 0
        except ValueError:
            flash('Format de date ou nombre invalide', 'error')
            return render_template('avec/create_meeting.html', group=group)
        
        meeting = Meeting(
            group_id=group_id,
            meeting_date=meeting_date,
            meeting_type=meeting_type,
            agenda=agenda,
            attendees_count=attendees_count,
            created_by=current_user.id
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        flash('Réunion créée avec succès!', 'success')
        return redirect(url_for('avec.group_meetings', group_id=group_id))
    
    return render_template('avec/create_meeting.html', group=group)

@bp.route('/group/<int:group_id>/cycle-sharing')
@login_required
def cycle_sharing(group_id):
    """Partage des bénéfices à la fin du cycle"""
    group = Group.query.get_or_404(group_id)
    cycle = group.cycle
    
    if current_user.role not in ['admin', 'animateur'] and current_user not in [group.get_president(), group.get_treasurer()]:
        flash('Accès réservé au comité de gestion', 'error')
        return redirect(url_for('dashboard'))
    
    if not cycle.is_cycle_ready_for_sharing():
        flash('Le cycle n\'est pas encore terminé', 'warning')
        return redirect(url_for('groups.show', id=group_id))
    
    # Calculer le partage des bénéfices
    total_capital = group.total_savings + group.total_loans  # Épargne + intérêts
    total_shares = group.get_total_shares()
    
    # Calculer la part de chaque membre
    members_shares = {}
    members_profit = {}
    
    for member in group.members:
        shares = group.get_member_shares(member.id)
        members_shares[member.id] = shares
        if total_shares > 0:
            profit_share = (shares / total_shares) * total_capital
            members_profit[member.id] = profit_share
        else:
            members_profit[member.id] = 0
    
    return render_template('avec/cycle_sharing.html',
                         group=group,
                         cycle=cycle,
                         total_capital=total_capital,
                         total_shares=total_shares,
                         members_shares=members_shares,
                         members_profit=members_profit)

@bp.route('/group/<int:group_id>/cycle-sharing/execute', methods=['POST'])
@login_required
def execute_cycle_sharing(group_id):
    """Exécuter le partage des bénéfices"""
    group = Group.query.get_or_404(group_id)
    cycle = group.cycle
    
    if current_user.role not in ['admin', 'animateur'] and current_user not in [group.get_president(), group.get_treasurer()]:
        flash('Accès réservé au comité de gestion', 'error')
        return redirect(url_for('dashboard'))
    
    # Marquer le cycle comme terminé
    cycle.is_cycle_completed = True
    cycle.profit_sharing_date = datetime.utcnow()
    
    # Créer des transactions de partage pour chaque membre
    total_shares = group.get_total_shares()
    total_capital = group.total_savings + group.total_loans
    
    for member in group.members:
        shares = group.get_member_shares(member.id)
        if total_shares > 0:
            profit_share = (shares / total_shares) * total_capital
            
            transaction = Transaction(
                type='profit_sharing',
                amount=profit_share,
                description=f'Partage des bénéfices - {shares} parts',
                group_id=group_id,
                user_id=member.id,
                status='completed',
                created_at=datetime.utcnow()
            )
            db.session.add(transaction)
    
    db.session.commit()
    flash('Partage des bénéfices exécuté avec succès!', 'success')
    return redirect(url_for('groups.show', id=group_id))

@bp.route('/formation/<int:group_id>')
@login_required
def formation_modules(group_id):
    """Modules de formation pour un groupe"""
    group = Group.query.get_or_404(group_id)
    
    # Vérifier que l'utilisateur est membre du groupe ou animateur
    if current_user not in group.members and current_user.role not in ['admin', 'animateur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('dashboard'))
    
    modules = FormationModule.query.filter_by(group_id=group_id).order_by(FormationModule.order).all()
    return render_template('avec/formation_modules.html', group=group, modules=modules)

@bp.route('/formation/<int:group_id>/module/<int:module_id>', methods=['GET', 'POST'])
@login_required
def formation_module_detail(group_id, module_id):
    """Détail d'un module de formation"""
    group = Group.query.get_or_404(group_id)
    module = FormationModule.query.get_or_404(module_id)
    
    if request.method == 'POST':
        module.is_completed = True
        module.completed_at = datetime.utcnow()
        module.completed_by = current_user.id
        db.session.commit()
        
        flash('Module marqué comme terminé!', 'success')
        return redirect(url_for('avec.formation_modules', group_id=group_id))
    
    return render_template('avec/formation_module_detail.html', group=group, module=module)

@bp.route('/group/<int:group_id>/committee')
@login_required
def group_committee(group_id):
    """Gestion du comité de groupe"""
    group = Group.query.get_or_404(group_id)
    
    if current_user.role not in ['admin', 'animateur'] and current_user not in group.members:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('avec/group_committee.html', group=group)

@bp.route('/group/<int:group_id>/committee/update', methods=['POST'])
@login_required
def update_committee(group_id):
    """Mettre à jour le comité de groupe"""
    group = Group.query.get_or_404(group_id)
    
    if current_user.role not in ['admin', 'animateur']:
        flash('Accès réservé aux animateurs', 'error')
        return redirect(url_for('dashboard'))
    
    president_id = request.form.get('president_id')
    secretary_id = request.form.get('secretary_id')
    treasurer_id = request.form.get('treasurer_id')
    
    group.president_id = president_id
    group.secretary_id = secretary_id
    group.treasurer_id = treasurer_id
    
    db.session.commit()
    flash('Comité de groupe mis à jour!', 'success')
    return redirect(url_for('avec.group_committee', group_id=group_id))

@bp.route('/group/<int:group_id>/solidarity-fund')
@login_required
def solidarity_fund(group_id):
    """Gestion de la caisse de solidarité"""
    group = Group.query.get_or_404(group_id)
    
    if current_user not in group.members and current_user.role not in ['admin', 'animateur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('dashboard'))
    
    solidarity_transactions = Transaction.query.filter_by(
        group_id=group_id, 
        type='solidarity'
    ).order_by(Transaction.created_at.desc()).all()
    
    return render_template('avec/solidarity_fund.html', group=group, transactions=solidarity_transactions)

@bp.route('/group/<int:group_id>/solidarity-fund/add', methods=['POST'])
@login_required
def add_solidarity_contribution(group_id):
    """Ajouter une contribution à la caisse de solidarité"""
    group = Group.query.get_or_404(group_id)
    
    if current_user not in group.members:
        flash('Seuls les membres peuvent contribuer', 'error')
        return redirect(url_for('avec.solidarity_fund', group_id=group_id))
    
    amount = request.form.get('amount')
    description = request.form.get('description')
    
    if not amount:
        flash('Montant requis', 'error')
        return redirect(url_for('avec.solidarity_fund', group_id=group_id))
    
    try:
        amount = float(amount)
    except ValueError:
        flash('Montant invalide', 'error')
        return redirect(url_for('avec.solidarity_fund', group_id=group_id))
    
    transaction = Transaction(
        type='solidarity',
        amount=amount,
        description=description,
        group_id=group_id,
        user_id=current_user.id,
        status='completed'
    )
    
    group.solidarity_fund += amount
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'Contribution de {amount} FCFA ajoutée à la caisse de solidarité!', 'success')
    return redirect(url_for('avec.solidarity_fund', group_id=group_id))

@bp.route('/member/<int:user_id>/account-book')
@login_required
def member_account_book(user_id):
    """Carnet de comptes individuel d'un membre"""
    user = User.query.get_or_404(user_id)
    
    # Vérifier que l'utilisateur consulte son propre carnet ou est animateur
    if current_user.id != user_id and current_user.role not in ['admin', 'animateur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('dashboard'))
    
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()
    
    # Calculer les totaux
    total_savings = sum(t.amount for t in transactions if t.type == 'shares_purchase' and t.status == 'completed')
    total_loans = sum(t.amount for t in transactions if t.type == 'loan' and t.status == 'completed')
    total_solidarity = sum(t.amount for t in transactions if t.type == 'solidarity' and t.status == 'completed')
    
    return render_template('avec/member_account_book.html', 
                         user=user, 
                         transactions=transactions,
                         total_savings=total_savings,
                         total_loans=total_loans,
                         total_solidarity=total_solidarity)

@bp.route('/supervision/dashboard')
@login_required
def supervision_dashboard():
    """Tableau de bord de supervision pour les animateurs"""
    if current_user.role not in ['admin', 'animateur']:
        flash('Accès réservé aux animateurs', 'error')
        return redirect(url_for('dashboard'))
    
    # Statistiques de supervision
    total_groups = Group.query.count()
    active_groups = Group.query.filter_by(status='active').count()
    groups_in_preparation = Group.query.join(Cycle).filter(Cycle.phase == 'preparation').count()
    groups_in_intensive = Group.query.join(Cycle).filter(Cycle.phase == 'intensive').count()
    groups_in_supervision = Group.query.join(Cycle).filter(Cycle.phase == 'supervision').count()
    
    # Groupes récents
    recent_groups = Group.query.order_by(Group.created_at.desc()).limit(5).all()
    
    return render_template('avec/supervision_dashboard.html',
                         total_groups=total_groups,
                         active_groups=active_groups,
                         groups_in_preparation=groups_in_preparation,
                         groups_in_intensive=groups_in_intensive,
                         groups_in_supervision=groups_in_supervision,
                         recent_groups=recent_groups) 