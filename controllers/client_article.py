#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_article = Blueprint('client_article', __name__,
                        template_folder='templates')

@client_article.route('/client/index')
@client_article.route('/client/article/show')
def client_article_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''
    SELECT s.*, t.libelle_type_ski as libelle
    FROM ski s
    LEFT JOIN type_ski t ON s.id_type_ski = t.id_type_ski
    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()

    # Pour le filtre
    sql = '''SELECT * FROM type_ski'''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()

    # Calcul du panier
    sql = '''
    SELECT s.*, lp.quantite 
    FROM ski s 
    INNER JOIN ligne_panier lp ON s.id_ski = lp.id_ski 
    WHERE lp.id_utilisateur = %s
    '''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()

    prix_total = None
    if len(articles_panier) >= 1:
        sql = '''
        SELECT SUM(s.prix_ski * lp.quantite) as prix_total
        FROM ski s
        INNER JOIN ligne_panier lp ON s.id_ski = lp.id_ski
        WHERE lp.id_utilisateur = %s
        '''
        mycursor.execute(sql, (id_client,))
        prix_total = mycursor.fetchone()['prix_total']

    return render_template('client/boutique/panier_article.html',
                         articles=articles,
                         articles_panier=articles_panier,
                         prix_total=prix_total,
                         items_filtre=types_article)
