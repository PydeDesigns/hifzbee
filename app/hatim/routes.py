from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.hatim import bp
from app.hatim.forms import CreateHatimForm, JoinHatimForm, UpdateProgressForm
from app.models import Hatim, HatimParticipation, User
from datetime import datetime

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's active hatims
    active_participations = current_user.participations.filter_by(completion_status=False).all()
    completed_participations = current_user.participations.filter_by(completion_status=True).all()
    
    return render_template('hatim/dashboard.html',
                         active_participations=active_participations,
                         completed_participations=completed_participations)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateHatimForm()
    if form.validate_on_submit():
        hatim = Hatim(
            title=form.title.data,
            creator_id=current_user.id,
            target_completion_date=form.target_completion_date.data,
            is_public=form.is_public.data,
            auto_join=form.auto_join.data
        )
        db.session.add(hatim)
        db.session.commit()
        
        # Add XP points for creating a hatim
        current_user.xp_points += 50
        db.session.commit()
        
        flash('Your hatim has been created!', 'success')
        return redirect(url_for('hatim.dashboard'))
    
    return render_template('hatim/create.html', form=form)

@bp.route('/browse')
@login_required
def browse():
    # Get all public hatims that aren't completed
    public_hatims = Hatim.query.filter_by(is_public=True, is_complete=False)\
        .order_by(Hatim.created_at.desc())\
        .all()
    return render_template('hatim/browse.html', hatims=public_hatims)

@bp.route('/join/<int:hatim_id>', methods=['GET', 'POST'])
@login_required
def join(hatim_id):
    hatim = Hatim.query.get_or_404(hatim_id)
    
    # Check if user is already participating
    if current_user.participations.filter_by(hatim_id=hatim_id).first():
        flash('You are already participating in this hatim!', 'warning')
        return redirect(url_for('hatim.dashboard'))
    
    form = JoinHatimForm()
    if form.validate_on_submit():
        # Create new participation
        participation = HatimParticipation(
            user_id=current_user.id,
            hatim_id=hatim_id,
            assigned_juz=','.join(form.juz_selection.data)
        )
        db.session.add(participation)
        
        # Add XP points for joining a hatim
        current_user.xp_points += 20
        db.session.commit()
        
        flash('You have successfully joined the hatim!', 'success')
        return redirect(url_for('hatim.dashboard'))
    
    return render_template('hatim/join.html', hatim=hatim, form=form)

@bp.route('/progress/<int:participation_id>', methods=['GET', 'POST'])
@login_required
def update_progress(participation_id):
    participation = HatimParticipation.query.get_or_404(participation_id)
    
    # Ensure user owns this participation
    if participation.user_id != current_user.id:
        flash('You cannot update progress for other users!', 'danger')
        return redirect(url_for('hatim.dashboard'))
    
    form = UpdateProgressForm()
    if form.validate_on_submit():
        # Update completion status
        participation.completion_status = True
        
        # Add XP points for completing juz
        current_user.xp_points += len(form.completed_juz.data) * 10
        db.session.commit()
        
        # Check if entire hatim is complete
        hatim = participation.hatim
        all_complete = all(p.completion_status for p in hatim.participations)
        if all_complete:
            hatim.is_complete = True
            # Bonus XP for completing entire hatim
            for p in hatim.participations:
                p.user.xp_points += 100
            db.session.commit()
            flash('Congratulations! The entire hatim has been completed!', 'success')
        else:
            flash('Your progress has been updated!', 'success')
        
        return redirect(url_for('hatim.dashboard'))
    
    # Pre-select completed juz
    if participation.assigned_juz:
        form.completed_juz.data = participation.assigned_juz.split(',')
    
    return render_template('hatim/progress.html', 
                         participation=participation, 
                         form=form)
