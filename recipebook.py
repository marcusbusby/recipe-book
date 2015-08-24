import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, session
from contextlib import closing
from functools import wraps


# Application Config

DATABASE = '/tmp/recipebook.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

#Database Communication

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

#Views

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			return redirect(url_for('login'))
	return wrap

@app.route('/')
@login_required
def home():
	#import pdb; pdb.set_trace()
	username = session['username']
	return render_template("home.html", username=username)

@app.route('/recipes', methods=['GET'])
def show_recipes():
	#import pdb; pdb.set_trace()
	cur1 = g.db.execute('select e_id, title, instructions from recipes order by e_id desc')
	recipes = []
	for row1 in cur1.fetchall():
		cur2 = g.db.execute('select ingredient, amount from ingredients where e_id=' + str(row1[0]))
		ingredientlist = []
		for row2 in cur2.fetchall():
			ingredientlist.append(row2)
		recipes.append(dict(title=row1[1], instructions=row1[2], ingredients = ingredientlist))
	return render_template('recipes.html', recipes=recipes)

@app.route('/login')
def login():
		session['logged_in'] = True
		session['username'] = USERNAME
		#import pdb; pdb.set_trace()
		return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	session.pop('username', None)
	return render_template('logout.html')

@app.route('/add', methods=['GET'])
def add_recipe_get():
	return render_template('add_recipe.html')


@app.route('/add', methods=['POST'])
def add_recipe_post():
	cursor = g.db.execute('insert into recipes (title, instructions) values (?, ?)', 
			     [request.form['title'], request.form['instructions']])
	g.db.commit()
	if 'ingredientname1' in request.form:
		for x in range(1, (int((len(request.form)-2)/2)+1)):
			g.db.execute('insert into ingredients (ingredient, amount, e_id) values (?, ?, ?)',
				         [request.form['ingredientname' + str(x)], request.form['ingredientamount' + str(x)], cursor.lastrowid])
		g.db.commit()
	return redirect(url_for('show_recipes'))



if __name__ == '__main__':
	app.run()

