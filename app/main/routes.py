from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app.main import bp
from app.models import User, Hatim, HatimParticipation

@bp.route('/')
@bp.route('/index')
def index():
    public_hatims = None
    if current_user.is_authenticated:
        # Get recent public hatims that the user hasn't joined
        public_hatims = Hatim.query.filter_by(is_public=True)\
            .filter(~Hatim.participations.any(HatimParticipation.user_id == current_user.id))\
            .order_by(Hatim.created_at.desc())\
            .limit(5)\
            .all()
    return render_template('main/index.html', public_hatims=public_hatims)

@bp.route('/profile')
@login_required
def profile():
    # Get user's hatims and achievements
    created_hatims = current_user.created_hatims.order_by(Hatim.created_at.desc()).all()
    participations = current_user.participations.order_by(HatimParticipation.joined_at.desc()).all()
    return render_template('main/profile.html', created_hatims=created_hatims, 
                         participations=participations)

@bp.route('/settings')
@login_required
def settings():
    return render_template('main/settings.html')
