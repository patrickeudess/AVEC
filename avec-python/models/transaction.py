from datetime import datetime
from . import db

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # savings, loan, repayment
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    due_date = db.Column(db.Date)
    interest_rate = db.Column(db.Numeric(5, 2), default=0)  # Taux d'intérêt pour les prêts
    loan_term = db.Column(db.Integer)  # Durée du prêt en mois
    remaining_balance = db.Column(db.Numeric(10, 2), default=0)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    approver = db.relationship('User', foreign_keys=[approved_by])
    
    def calculate_interest(self):
        if self.type == 'loan' and self.interest_rate > 0:
            return (self.amount * self.interest_rate) / 100
        return 0
    
    def is_loan(self):
        return self.type == 'loan'
    
    def is_repayment(self):
        return self.type == 'repayment'
    
    def is_savings(self):
        return self.type == 'savings'
    
    def approve(self, approver_user):
        self.status = 'approved'
        self.approved_by = approver_user.id
        self.approved_at = datetime.utcnow()
        
        # Mettre à jour les totaux du groupe
        if self.is_savings():
            self.group.total_savings += self.amount
        elif self.is_loan():
            self.group.total_loans += self.amount
            self.remaining_balance = self.amount
    
    def reject(self):
        self.status = 'rejected'
    
    def complete(self):
        self.status = 'completed'
        if self.is_repayment():
            self.remaining_balance = max(0, self.remaining_balance - self.amount)
    
    def __repr__(self):
        return f'<Transaction {self.type} {self.amount}>' 