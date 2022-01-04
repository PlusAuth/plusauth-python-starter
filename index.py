from os import environ as env
from flask import Flask, jsonify, render_template, redirect, session
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc.user_session import UserSession
from dotenv import load_dotenv

load_dotenv() # Load environment variables

app = Flask(__name__)
app.config.update(
    OIDC_REDIRECT_URI = 'http://localhost:3000/login/callback',
    SECRET_KEY = 'SessionSecretKey' # flask_pyoidc extension relies on Flask sessions, which requires SECRET_KEY
)

client_metadata = ClientMetadata(
    client_id=env.get("CLIENT_ID"),
    client_secret=env.get("CLIENT_SECRET"))
auth_params = {'scope': ['openid', 'profile', 'email']}
# Create auth config
config = ProviderConfiguration(
    issuer=env.get("AUTH_URL"),
    client_metadata=client_metadata,
    auth_request_params=auth_params)

auth = OIDCAuthentication({'default': config}, app)

@app.route('/login')
@auth.oidc_auth('default')
def login():
    return redirect('/')

# Post Logout URL
@app.route('/logout')
@auth.oidc_logout
def logout():
    return redirect('/')

@auth.error_view
def error(error=None, error_description=None):
    return jsonify({'error': error, 'message': error_description})

@app.route('/')
def index():
    user_session = UserSession(session, 'default')
    return render_template('index.html', user=user_session.userinfo)

@app.route('/profile')
@auth.oidc_auth('default')
def profile():
    user_session = UserSession(session, 'default')
    return render_template('profile.html', user=user_session.userinfo)

if __name__ == '__main__':
    app.run(debug=True, port=3000)