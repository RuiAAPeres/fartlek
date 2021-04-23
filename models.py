from app import db

class AthleteNotifications(db.Model):
    __tablename__ = 'athleteNotifications'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String())
    
    def __init__(self, id, token):
        self.id = id
        self.token = token

    def __repr__(self):
        return '<id {}>'.format(self.id)