# inspired by https://github.com/cenkalti/github-flask/blob/master/example.py
# setup flask
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, g, session
from flask.ext.seasurf import SeaSurf
app = Flask(__name__)
csrf = SeaSurf(app)
# setup ssl if needed
"""import ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('/etc/ssl/private/server.pem')"""

# setup client id and secret of github application for oauth 
from flask.ext.github import GitHub

# config application
app.config['GITHUB_CLIENT_ID'] = 'XXX'
app.config['GITHUB_CLIENT_SECRET'] = 'YYY'
app_secret = 'ZZZ'
github_callback_url = "http://localhost:5000/github-callback"
github = GitHub(app)

# setup sqlalchemy
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker,scoped_session
from database_setup import Base, Category, Item, User
engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

# http://docs.sqlalchemy.org/en/rel_0_8/orm/session.html#sqlalchemy.orm.scoping.scoped_session
db_session = scoped_session(sessionmaker(autocommit=False,
	autoflush=False,
	bind=engine))

Base.query = db_session.query_property()

# flask functions 
##################
@app.route('/')
@app.route('/catalog/')
def showCatalog():
	"""show catalog items"""
	categories = Category.query.all()
	items = Item.query.order_by(Item.created.desc()).all()
	return render_template('catalog.html', categories = categories,items=items,user=g.user)

@app.route('/catalog/<int:category_id>/')
def showCategory(category_id):
	"""show a category with its items"""
	categories = Category.query.all()
	category = Category.query.filter_by(id=category_id).one()
	items = Item.query.filter_by(category = category).all()
	return render_template('catalog.html', categories = categories,items=items,category=category,user=g.user)

@app.route('/item/<int:item_id>/')
def showItem(item_id):
	"""show a item"""
	item = Item.query.filter_by(id = item_id).one()
	return render_template('item.html', item = item,user=g.user)

@app.route('/catalog/<int:category_id>/add/', methods = ['GET', 'POST'])
def addItem(category_id):
	"""add a item"""
	categories = Category.query.all()
	category = Category.query.filter_by(id = category_id).one()
	# check if user is authenticated
	user = g.user	
	if user is not None:
		if request.method == 'POST':
			# check if an item name was entered
			if request.form['name'] != "":
				mycategory = Category.query.filter_by(name=request.form['category']).one()
				item = Item(name=request.form['name'],
					image=request.form['image'],
					description=request.form['description'],
					category=mycategory,
					owner=user)
				db_session.add(item)
				db_session.commit()
				flash("Item " + item.name + " added to " + item.category.name)
				return redirect(url_for('showCategory',category_name=mycategory.name))
			else:
				flash("Item name must not be empty")
				return redirect(url_for('addItem',category_name=category_name))
		else:
			return render_template('additem.html',category=category,categories=categories,user=user)
	else:
		flash("Unauthorized user")
		return redirect(url_for('showCatalog'))

@app.route('/item/<int:item_id>/edit/', methods = ['GET', 'POST'])
def editItem(item_id):
	"""edit a item"""
	user = g.user
	if user is None:
		flash("You need to log in first")
		return redirect(url_for('showCatalog'))
	item = Item.query.filter_by(id = item_id).one()
	# check if user is owner
	if user == item.owner:
		if request.method == 'POST':
			# check if an item name was entered
			if request.form['name'] !="":
				item.name = request.form['name']
				item.image = request.form['image']
				item.description = request.form['description']
				if request.form['category']:
					category = Category.query.filter_by(name=request.form['category']).one()
					item.category = category
				db_session.add(item)
				db_session.commit()
				flash("Item " + item.name + "saved")
				return redirect(url_for('editItem', item_id=item.id))
			else:
				flash("Item name must not be empty")
				return redirect(url_for('editItem',item_id=item.id))
		else:
			categories = Category.query.all()
			return render_temlate('edititem.html, item =item,categories,user=user')
	else:
		flash("Unauthorized user")
		return redirect(url_for('showCatalog'))


@app.route('/item/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteItem(item_id):
    """delete a item"""
    user = g.user
    if user is None:
        flash("You need to log in first")
        return redirect(url_for('showCatalog'))
    item = Item.query.filter_by(id = item_id).one()
    category = item.category
    # check if user is owner
    if user == item.owner:
        if request.method == 'POST':
            flash("Item " + item.name + " deleted")
            db_session.delete(item)
            db_session.commit()
            return redirect(url_for('showCategory', category_name=category.name))
        else:
            return render_template('deleteitem.html', item = item, user=g.user)
    else:
        flash("Unauthorized user")
        return redirect(url_for('showCatalog'))

@app.route('/login')
def loginUser():
	"""user Login"""
	# send user back to the source page
	uri = github_callback_url + "?next=" + request.referrer
	return github.authorize(redirect_uri=uri)
	
@app.route('/logout')
def logoutUser():
	"""logout user and show main catalog view"""
	session.pop('user_id', None)
	flash('User logged out')
	return redirect(url_for('showCatalog'))

@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
	"""callback for github oauth"""
	next_url = request.args.get('next') or url_for('showCatalog')
	if oauth_token is None:
		# something went wront
		flash("Authorization failed")
		flash(request.args.get('error'))
		flash(request.args.get('error_description'))
		flash(request.args.get('error_uri'))
		return redirect(next_url)
	user = User.query.filter_by(github_access_token=oauth_token).first()
	if user is None:
		# new user is not in database
		user = User(name="",github_access_token=oauth_token)
		db_session.add(user)
	# save oauth token in database
	user.github_access_token = oauth_token
	db_session.commit()
	session['user_id'] = user.id
	flash("User " + user.name + " logged in")
	return redirect(next_url)

@github.access_token_getter
def token_getter():
	"""github token getter"""
	user = g.user
	if user is not None:
		return user.github_access_token

# Registers a function to run before each request.
@app.before_request
def before_request():
	"""save user data to database, maybe it changed or user is new"""
	g.user = None
	if 'user_id' in session:
		g.user = User.query.get(session['user_id'])
		g.user.name = github.get('user')["name"]
		g.user.avatar = github.get('user')["avatar_url"]
		db_session.add(g.user)
		db_session.commit()

@app.after_request
def after_request(response):
	"""Register a function to be run after each request"""
	db_session.remove()
	return response

@app.route('/json')
def catalogjson():
	"""json api for list of all items"""
	list = []
	items = Item.query.all()
	for item in items:
		list.append({"name" : item.name,
			"id" : item.id,
			"description" : item.description,
			"category" : item.category.name,
			"image" : item.image,
			"owner" : item.owner.name
		})
	return jsonify({"items":list})
	
# run flask server if script is started directly 
if __name__ == '__main__':
	app.debug = False
	app.secret_key = app_secret
	app.run(host = '0.0.0.0', port = 5000)
