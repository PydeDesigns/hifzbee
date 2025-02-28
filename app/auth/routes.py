from flask import render_template, flash, redirect, url_for, request, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm, GuestLoginForm
from urllib.parse import urlparse
import uuid
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
import os

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Initialize OAuth client
client = WebApplicationClient(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else None

def get_google_provider_cfg():
    try:
        return requests.get(GOOGLE_DISCOVERY_URL).json()
    except Exception as e:
        current_app.logger.error(f"Error fetching Google provider config: {str(e)}")
        return None

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    guest_form = GuestLoginForm()
    
    try:
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid email or password', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        flash('An error occurred during login. Please try again.', 'danger')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html', title='Sign In', 
                         form=form, guest_form=guest_form)

@bp.route('/guest-login', methods=['POST'])
def guest_login():
    try:
        form = GuestLoginForm()
        if form.validate_on_submit():
            device_id = form.device_id.data or str(uuid.uuid4())
            guest_name = form.guest_name.data or f'Guest_{device_id[:8]}'
            
            # Create or get guest user
            user = User.query.filter_by(email=f'guest_{device_id}@hifzbee.local').first()
            
            if user is None:
                user = User(
                    username=guest_name,
                    email=f'guest_{device_id}@hifzbee.local',
                    is_guest=True
                )
                user.set_password(str(uuid.uuid4()))
                db.session.add(user)
                db.session.commit()
            
            login_user(user)
            flash(f'Welcome, {guest_name}!', 'success')
            return redirect(url_for('main.index'))
    except Exception as e:
        current_app.logger.error(f"Guest login error: {str(e)}")
        flash('An error occurred during guest login. Please try again.', 'danger')
    
    return redirect(url_for('auth.login'))

@bp.route('/google-login')
def google_login():
    if not GOOGLE_CLIENT_ID or not client:
        flash('Google login is not configured', 'warning')
        return redirect(url_for('auth.login'))
    
    try:
        # Get Google provider configuration
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            flash('Error connecting to Google services', 'danger')
            return redirect(url_for('auth.login'))

        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Use library to construct the request for login
        callback_url = url_for('auth.google_callback', _external=True)
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=callback_url,
            scope=["openid", "email", "profile"],
        )
        return redirect(request_uri)
    except Exception as e:
        current_app.logger.error(f"Google login error: {str(e)}")
        flash('An error occurred with Google login. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

@bp.route('/google-login/callback')
def google_callback():
    if not GOOGLE_CLIENT_ID or not client:
        flash('Google login is not configured', 'warning')
        return redirect(url_for('auth.login'))

    try:
        # Get Google provider configuration
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            flash('Error connecting to Google services', 'danger')
            return redirect(url_for('auth.login'))

        # Get authorization code from Google
        code = request.args.get("code")
        if not code:
            flash('No authorization code received from Google', 'danger')
            return redirect(url_for('auth.login'))

        # Find out what URL to hit to get tokens
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Get callback URL
        callback_url = url_for('auth.google_callback', _external=True)

        # Prepare and send request to get tokens
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=callback_url,
            code=code
        )
        
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        # Parse the tokens
        client.parse_request_body_response(json.dumps(token_response.json()))

        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            users_name = userinfo_response.json().get("given_name", users_email.split('@')[0])

            # Create or get user
            user = User.query.filter_by(email=users_email).first()
            if not user:
                user = User(
                    username=users_name,
                    email=users_email
                )
                db.session.add(user)
                db.session.commit()

            # Begin user session by logging the user in
            login_user(user)
            flash('Successfully logged in with Google!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Email not verified by Google', 'danger')
            return redirect(url_for('auth.login'))

    except Exception as e:
        current_app.logger.error(f"Google callback error: {str(e)}")
        flash('Failed to log in with Google. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email address already registered', 'danger')
                return redirect(url_for('auth.register'))
            
            existing_username = User.query.filter_by(username=form.username.data).first()
            if existing_username:
                flash('Username already taken', 'danger')
                return redirect(url_for('auth.register'))
            
            # Create new user
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            
            # Log the attempt
            current_app.logger.info(f"Attempting to register user: {form.username.data}")
            
            # Add to database
            db.session.add(user)
            db.session.commit()
            
            current_app.logger.info(f"Successfully registered user: {form.username.data}")
            flash('Congratulations, you are now registered!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error for user {form.username.data}: {str(e)}")
            current_app.logger.exception("Full traceback:")
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
