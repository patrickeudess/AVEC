from datetime import datetime
from . import db

class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(300))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    logo_url = db.Column(db.String(300))
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    users = db.relationship('User', backref='organization', lazy='dynamic')
    cycles = db.relationship('Cycle', backref='organization', lazy='dynamic')
    
    def get_total_groups(self):
        return sum(cycle.groups.count() for cycle in self.cycles.all())
    
    def get_total_members(self):
        total = 0
        for cycle in self.cycles.all():
            for group in cycle.groups.all():
                total += group.current_members
        return total
    
    def get_total_savings(self):
        total = 0
        for cycle in self.cycles.all():
            for group in cycle.groups.all():
                total += group.total_savings
        return total
    
    def get_total_loans(self):
        total = 0
        for cycle in self.cycles.all():
            for group in cycle.groups.all():
                total += group.total_loans
        return total
    
    def __repr__(self):
        return f'<Organization {self.name}>' 