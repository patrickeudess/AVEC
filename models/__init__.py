from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='member')  # admin, animateur, member
    status = db.Column(db.String(20), default='active')
    village = db.Column(db.String(100))  # Village d'origine
    literacy_level = db.Column(db.String(20), default='basic')  # basic, intermediate, advanced
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.email}>'

class Cycle(db.Model):
    __tablename__ = 'cycles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    phase = db.Column(db.String(20), default='preparation')  # preparation, intensive, supervision
    status = db.Column(db.String(20), default='active')
    target_amount = db.Column(db.Numeric(15, 2), default=0)  # Montant en FCFA
    current_amount = db.Column(db.Numeric(15, 2), default=0)
    interest_rate = db.Column(db.Numeric(5, 2), default=0)
    meeting_frequency = db.Column(db.String(20), default='weekly')
    meeting_day = db.Column(db.String(20))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Cycle annuel AVEC
    cycle_year = db.Column(db.Integer, default=1)  # Année du cycle
    is_cycle_completed = db.Column(db.Boolean, default=False)  # Cycle terminé
    profit_sharing_date = db.Column(db.DateTime)  # Date de partage des bénéfices
    
    groups = db.relationship('Group', backref='cycle', lazy='dynamic')
    
    def get_progress_percentage(self):
        if not self.target_amount or self.target_amount == 0:
            return 0
        return min((self.current_amount / self.target_amount) * 100, 100)
    
    def is_cycle_ready_for_sharing(self):
        """Vérifie si le cycle est prêt pour le partage des bénéfices"""
        if self.end_date and datetime.utcnow() >= self.end_date:
            return True
        return False
    
    def __repr__(self):
        return f'<Cycle {self.name}>'

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    village = db.Column(db.String(100), nullable=False)
    max_members = db.Column(db.Integer, default=25)
    current_members = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')
    meeting_location = db.Column(db.String(200))
    meeting_time = db.Column(db.String(10))  # Format "HH:MM"
    share_value = db.Column(db.Numeric(10, 2), default=0)  # Valeur d'une part en FCFA
    contribution_amount = db.Column(db.Numeric(10, 2), default=0)  # Contribution mensuelle
    total_savings = db.Column(db.Numeric(15, 2), default=0)
    total_loans = db.Column(db.Numeric(15, 2), default=0)
    solidarity_fund = db.Column(db.Numeric(15, 2), default=0)  # Caisse de solidarité
    cycle_id = db.Column(db.Integer, db.ForeignKey('cycles.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Comité de gestion AVEC
    president_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    secretary_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    treasurer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Règles du groupe AVEC
    loan_interest_rate = db.Column(db.Numeric(5, 2), default=0)  # Taux d'intérêt pour les prêts
    max_loan_amount = db.Column(db.Numeric(15, 2), default=0)  # Montant maximum de prêt
    loan_duration_months = db.Column(db.Integer, default=6)  # Durée maximale de prêt
    solidarity_contribution_rate = db.Column(db.Numeric(5, 2), default=5)  # % pour la solidarité
    
    members = db.relationship('User', secondary='user_groups', backref=db.backref('groups', lazy='dynamic'))
    transactions = db.relationship('Transaction', backref='group', lazy='dynamic')
    
    def can_accept_members(self):
        return self.status == 'active' and self.current_members < self.max_members
    
    def get_president(self):
        return User.query.get(self.president_id)
    
    def get_secretary(self):
        return User.query.get(self.secretary_id)
    
    def get_treasurer(self):
        return User.query.get(self.treasurer_id)
    
    def get_total_shares(self):
        """Calcule le nombre total de parts achetées"""
        shares_transactions = Transaction.query.filter_by(
            group_id=self.id,
            type='shares_purchase',
            status='completed'
        ).all()
        return sum(t.amount / self.share_value for t in shares_transactions)
    
    def get_member_shares(self, user_id):
        """Calcule le nombre de parts d'un membre"""
        shares_transactions = Transaction.query.filter_by(
            group_id=self.id,
            user_id=user_id,
            type='shares_purchase',
            status='completed'
        ).all()
        return sum(t.amount / self.share_value for t in shares_transactions)
    
    def __repr__(self):
        return f'<Group {self.name}>'

user_groups = db.Table('user_groups',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow),
    db.Column('role_in_group', db.String(20), default='member')  # member, president, secretary, treasurer
)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # shares_purchase, loan, loan_repayment, solidarity, interest
    amount = db.Column(db.Numeric(15, 2), nullable=False)  # Montant en FCFA
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, completed, rejected
    due_date = db.Column(db.DateTime)
    interest_rate = db.Column(db.Numeric(5, 2), default=0)
    loan_term = db.Column(db.Integer)  # Durée du prêt en mois
    remaining_balance = db.Column(db.Numeric(15, 2), default=0)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Pour les prêts
    loan_purpose = db.Column(db.String(200))  # Raison du prêt
    guarantors = db.Column(db.Text)  # Garants du prêt
    
    # Transparence AVEC - témoins de la transaction
    witnesses = db.Column(db.Text)  # Membres présents lors de la transaction
    meeting_date = db.Column(db.DateTime)  # Date de la réunion
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'))  # Réunion associée
    
    # Relations
    user = db.relationship('User', foreign_keys=[user_id], backref='transactions')
    approved_by_user = db.relationship('User', foreign_keys=[approved_by], backref='approved_transactions')
    
    def __repr__(self):
        return f'<Transaction {self.type} {self.amount} FCFA>'

class Meeting(db.Model):
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    meeting_date = db.Column(db.DateTime, nullable=False)
    meeting_type = db.Column(db.String(20), default='regular')  # regular, emergency, formation
    attendees_count = db.Column(db.Integer, default=0)
    agenda = db.Column(db.Text)
    decisions = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Transactions effectuées lors de cette réunion
    transactions = db.relationship('Transaction', backref='meeting', lazy='dynamic', 
                                 foreign_keys='Transaction.meeting_id')
    
    def __repr__(self):
        return f'<Meeting {self.group.name} - {self.meeting_date}>'

class FormationModule(db.Model):
    __tablename__ = 'formation_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # Contenu du module
    order = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    completed_at = db.Column(db.DateTime)
    completed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<FormationModule {self.name}>'

class CommunityEvaluation(db.Model):
    __tablename__ = 'community_evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    village_name = db.Column(db.String(100), nullable=False)
    population = db.Column(db.Integer)
    main_activities = db.Column(db.Text)
    existing_groups = db.Column(db.Text)
    needs_assessment = db.Column(db.Text)
    community_interest = db.Column(db.Boolean, default=False)
    evaluation_date = db.Column(db.DateTime, default=datetime.utcnow)
    evaluated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<CommunityEvaluation {self.village_name}>' 