from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    profile_picture = db.Column(db.String(120), default='default.jpg')
    xp_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_guest = db.Column(db.Boolean, default=False)
    google_id = db.Column(db.String(128), unique=True, nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_hatims = db.relationship('Hatim', backref='creator', lazy='dynamic')
    participations = db.relationship('HatimParticipation', backref='user', lazy='dynamic')
    achievements = db.relationship('Achievement', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Hatim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    target_completion_date = db.Column(db.DateTime)
    is_public = db.Column(db.Boolean, default=True)
    auto_join = db.Column(db.Boolean, default=True)
    is_complete = db.Column(db.Boolean, default=False)
    
    # Relationships
    participations = db.relationship('HatimParticipation', backref='hatim', lazy='dynamic')

class HatimParticipation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hatim_id = db.Column(db.Integer, db.ForeignKey('hatim.id'), nullable=False)
    assigned_juz = db.Column(db.String(50))  # Stored as comma-separated values
    completion_status = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
