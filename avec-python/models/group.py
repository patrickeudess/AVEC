from datetime import datetime
from . import db

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    cycle_id = db.Column(db.Integer, db.ForeignKey('cycles.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    max_members = db.Column(db.Integer, default=25)
    current_members = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')  # active, inactive, completed
    meeting_location = db.Column(db.String(200))
    meeting_time = db.Column(db.Time)
    contribution_amount = db.Column(db.Numeric(10, 2), default=0)
    total_savings = db.Column(db.Numeric(10, 2), default=0)
    total_loans = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    members = db.relationship('User', secondary='group_members', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='group', lazy='dynamic')
    
    def can_accept_members(self):
        return self.current_members < self.max_members and self.status == 'active'
    
    def add_member(self, user):
        if self.can_accept_members():
            if user not in self.members:
                self.members.append(user)
                self.current_members += 1
                return True
        return False
    
    def remove_member(self, user):
        if user in self.members:
            self.members.remove(user)
            self.current_members -= 1
            return True
        return False
    
    def get_fill_percentage(self):
        if self.max_members > 0:
            return (self.current_members / self.max_members) * 100
        return 0
    
    def __repr__(self):
        return f'<Group {self.name}>'

# Table de liaison pour les membres des groupes
group_members = db.Table('group_members',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
) 