from flask import Flask, redirect, url_for, render_template, request, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user,\
	current_user
from oauth import OAuthSignIn
from facebook import get_user_from_cookie, GraphAPI, GraphAPIError
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '1642955085978865',
        'secret': '8472b62a4c53bd729472d93ed221b204'
    },
    'twitter': {
        'id': 'nbuT4BXa8k82JqjbR8nI68KwM',
        'secret': '17xMljJO2KRwelygKVxhE5ZaxoC3DAj9keMvVO372qzF23CTG8'
    },
    'google': {
    	'id': '117651806022-p0u07crof7qh9gfpqv5qc5dpcghb4d63.apps.googleusercontent.com',
    	'secret': 'YZFlaStt2Kt6PTt25-egzP9D'
    }
}

# Facebook app details
FB_APP_ID = '1642955085978865'
FB_APP_NAME = 'testOAuth'
FB_APP_SECRET = '8472b62a4c53bd729472d93ed221b204'
FB_USER_ID = ''
FB_ACCESS_TOKEN = 'CAACEdEose0cBAM7I1BVCsqJWrBDdsaOXM0W8yYtyStfRhwx3DXIGRLUqxZA9r0PlYmqtLylvqvwJDaZAnhlcZA4CnjEdIJRmMHX52uzvy0cLMhlMTGkg05ZCN95wtDztf0uy9p2r3s33xT7bjncR7DOCIBQGhKCYBYdPoU62OXZBc1fHWPmAn2Nte7KQ8xZBtNTpl77qDj0AZDZD'

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'

class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	social_id = db.Column(db.String(64), nullable=False, unique=True)
	nickname = db.Column(db.String(64), nullable=False)
	email = db.Column(db.String(64), nullable=True)

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/facebook')
def facebook():
	# Attempt to get the short term access token for the current user
	result = get_fb_token(FB_APP_ID, FB_APP_SECRET)
	# If there is no result, we assume the user is not logged in.
	if result:
		graph = GraphAPI(access_token=FB_ACCESS_TOKEN, version='2.5')
		resp = graph.get_object('me/accounts')
		print "Response: ", resp
		attachment =  {
			'name': 'Mystic Light',
			'link': 'http://www.mysticlight.in/',
			'caption': 'Check out this site!',
			'description': 'Oh wow.',
			'picture': 'http://www.mysticlight.in/thumbnail.jpg'
		}
		try:
			fb_response = graph.put_wall_post(message="Hello World!", attachment=attachment)
			print fb_response
		except GraphAPIError as e:
			print 'Something went wrong:', e.type, e.message
		# friends = graph2.get_object("me/friends")
	
		# for friend in friends['data']:
		# 	print "{0} has id {1}".format(friend['name'].encode('utf-8'), friend['id'])
	return render_template('facebook.html')

def get_fb_token(app_id, app_secret):           
    payload = {'grant_type': 'client_credentials', 'client_id': app_id, 'client_secret': app_secret}
    file1 = requests.post('https://graph.facebook.com/oauth/access_token?', params = payload)
    # print file1.text #to test what the FB api responded with
    result = file1.text.split("=")[1]
    print file1.text #to test the TOKEN
    return result

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	social_id, username, email = oauth.callback()
	if social_id is None:
		flash('Authentication failed.')
		return redirect(url_for('index'))
	user = User.query.filter_by(social_id=social_id).first()
	if not user:
		user = User(social_id=social_id, nickname=username, email=email)
		db.session.add(user)
		db.session.commit()
	login_user(user, True)
	if provider == 'facebook':
		FB_USER_ID = social_id.split('$')[1]
		return redirect(url_for('facebook'))
	return redirect(url_for('index'))

if __name__ == '__main__':
	db.create_all()
	app.run(debug=True)