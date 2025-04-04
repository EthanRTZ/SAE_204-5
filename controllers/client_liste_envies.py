#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

client_liste_envies = Blueprint('client_liste_envies', __name__,
                        template_folder='templates')


@client_liste_envies.route('/client/envie/add', methods=['post'])
def client_liste_envies_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    
    # Vérifier si l'article est déjà dans la liste d'envies
    sql_check = "SELECT * FROM liste_envies WHERE id_client = %s AND id_article = %s"
    mycursor.execute(sql_check, (id_client, id_article))
    if mycursor.fetchone() is None:
        # Ajouter l'article à la liste d'envies
        sql_insert = "INSERT INTO liste_envies (id_client, id_article) VALUES (%s, %s)"
        mycursor.execute(sql_insert, (id_client, id_article))
        get_db().commit()
        flash("Article ajouté à la liste d'envies avec succès.")
    else:
        flash("L'article est déjà dans votre liste d'envies.")
    
    return redirect('/client/article/show')


@client_liste_envies.route('/client/envie/delete', methods=['post'])
def client_liste_envies_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    
    # Supprimer l'article de la liste d'envies
    sql_delete = "DELETE FROM liste_envies WHERE id_client = %s AND id_article = %s"
    mycursor.execute(sql_delete, (id_client, id_article))
    get_db().commit()
    flash("Article supprimé de la liste d'envies.")
    
    return redirect('/client/envies/show')


@client_liste_envies.route('/client/envies/show', methods=['get'])
def client_liste_envies_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    
    # Récupérer les articles de la liste d'envies
    sql = '''
    SELECT s.id_ski as id_article, s.nom_ski as nom, s.prix_ski as prix, s.stock as stock, s.photo_ski as image
    FROM liste_envies le
    JOIN ski s ON le.id_article = s.id_ski
    WHERE le.id_client = %s
    '''
    mycursor.execute(sql, (id_client,))
    articles_liste_envies = mycursor.fetchall()
    
    # Récupérer les articles de l'historique (si nécessaire)
    articles_historique = []  # Remplir cette liste si vous avez besoin de l'historique
    
    return render_template('client/liste_envies/liste_envies_show.html',
                           articles_liste_envies=articles_liste_envies,
                           articles_historique=articles_historique)



def client_historique_add(article_id, client_id):
    mycursor = get_db().cursor()
    client_id = session['id_user']
    # rechercher si l'article pour cet utilisateur est dans l'historique
    # si oui mettre
    sql ='''   '''
    mycursor.execute(sql, (article_id, client_id))
    historique_produit = mycursor.fetchall()
    sql ='''   '''
    mycursor.execute(sql, (client_id))
    historiques = mycursor.fetchall()


@client_liste_envies.route('/client/envies/up', methods=['get'])
@client_liste_envies.route('/client/envies/down', methods=['get'])
@client_liste_envies.route('/client/envies/last', methods=['get'])
@client_liste_envies.route('/client/envies/first', methods=['get'])
def client_liste_envies_article_move():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
  
    return redirect('/client/envies/show')
