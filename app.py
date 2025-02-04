#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, flash

app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'

from flask import session, g
import pymysql.cursors

import os                                 # à ajouter
from dotenv import load_dotenv            # à ajouter
project_folder = os.path.expanduser('~/SAE_204-5')  # adjust as appropriate (avec le dossier où se trouve le fichier .env et app.py)
load_dotenv(os.path.join(project_folder, '.env'))                            # à ajouter

def get_db():
    if 'db' not in g:
        g.db =  pymysql.connect(
            host=os.environ.get("HOST"),                # à modifier
            user=os.environ.get("LOGIN"),               # à modifier
            password=os.environ.get("PASSWORD"),        # à modifier
            database=os.environ.get("DATABASE"),        # à modifier
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/')
def show_accueil():
    if 'role' in session:
        if session['role'] == 'ROLE_admin':
            return redirect('/admin/commande/index')
        else:
            return redirect('/client/article/show')
    return render_template('auth/layout.html')

##################
# Authentification
##################

# Middleware de sécurité

@app.before_request
def before_request():
     if request.path.startswith('/admin') or request.path.startswith('/client'):
        print('session start with /admin or /client')
        if 'role' not in session:
            return redirect('/login')
        else:
            print('role',session['role'])
            if (request.path.startswith('/client') and session['role'] != 'ROLE_client') or (request.path.startswith('/admin') and session['role'] != 'ROLE_admin'):
                print('pb de route : ', session['role'], request.path.title(), ' => deconnexion')
                session.pop('login', None)
                session.pop('role', None)
                flash("PB route / rôle / autorisation", "alert-warning")
                return redirect('/logout')



app.register_blueprint(auth_security)
app.register_blueprint(fixtures_load)

app.register_blueprint(client_article)
app.register_blueprint(client_commande)
app.register_blueprint(client_commentaire)
app.register_blueprint(client_panier)
app.register_blueprint(client_coordonnee)
app.register_blueprint(client_liste_envies)

app.register_blueprint(admin_article)
app.register_blueprint(admin_declinaison_article)
app.register_blueprint(admin_commande)
app.register_blueprint(admin_type_article)
app.register_blueprint(admin_dataviz)
app.register_blueprint(admin_commentaire)


if __name__ == '__main__':
    app.run()

