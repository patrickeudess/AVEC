from datetime import datetime
from . import db

class Cycle(db.Model):
    __tablename__ = 'cycles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='preparation')  # preparation, formation, supervision, completed
    target_amount = db.Column(db.Numeric(10, 2), default=0)
    current_amount = db.Column(db.Numeric(10, 2), default=0)
    interest_rate = db.Column(db.Numeric(5, 2), default=0)  # Taux d'intérêt en pourcentage
    meeting_frequency = db.Column(db.String(20), default='weekly')  # weekly, monthly
    meeting_day = db.Column(db.String(20))  # lundi, mardi, etc.
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    groups = db.relationship('Group', backref='cycle', lazy='dynamic')
    
    def get_progress_percentage(self):
        if self.target_amount > 0:
            return (self.current_amount / self.target_amount) * 100
        return 0
    
    def is_active(self):
        return self.status in ['preparation', 'formation', 'supervision']
    
    def next_phase(self):
        phases = ['preparation', 'formation', 'supervision', 'completed']
        current_index = phases.index(self.status)
        if current_index < len(phases) - 1:
            self.status = phases[current_index + 1]
            return True
        return False
    
    def __repr__(self):
        return f'<Cycle {self.name}>' 