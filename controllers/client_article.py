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

    # Récupération des types de ski pour le filtre
    sql = '''SELECT * FROM type_ski'''
    mycursor.execute(sql)
    types_ski = mycursor.fetchall()

    # Récupération des marques pour le filtre
    sql = '''SELECT DISTINCT m.* FROM marque m 
             INNER JOIN ski s ON s.id_marque = m.id_marque'''
    mycursor.execute(sql)
    marques_ski = mycursor.fetchall()

    # Construction de la requête de base pour les skis
    sql_base = '''
    SELECT s.*, t.libelle_type_ski as libelle, m.nom_marque as nom_marque
    FROM ski s
    LEFT JOIN type_ski t ON s.id_type_ski = t.id_type_ski
    LEFT JOIN marque m ON s.id_marque = m.id_marque
    WHERE 1=1
    '''
    params = []

    # Ajout des conditions de filtrage
    if 'filter_word' in session and session['filter_word']:
        sql_base += ''' AND (s.nom_ski LIKE %s OR m.nom_marque LIKE %s)'''
        params.extend(['%' + session['filter_word'] + '%'] * 2)

    if 'filter_types' in session and session['filter_types']:
        sql_base += ''' AND s.id_type_ski IN ({})'''.format(','.join(['%s'] * len(session['filter_types'])))
        params.extend(session['filter_types'])

    if 'filter_marques' in session and session['filter_marques']:
        sql_base += ''' AND s.id_marque IN ({})'''.format(','.join(['%s'] * len(session['filter_marques'])))
        params.extend(session['filter_marques'])

    if 'filter_prix_min' in session and session['filter_prix_min']:
        sql_base += ''' AND s.prix_ski >= %s'''
        params.append(float(session['filter_prix_min']))

    if 'filter_prix_max' in session and session['filter_prix_max']:
        sql_base += ''' AND s.prix_ski <= %s'''
        params.append(float(session['filter_prix_max']))

    # Exécution de la requête finale pour les articles
    mycursor.execute(sql_base, tuple(params))
    articles = mycursor.fetchall()

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
                         types_ski=types_ski,
                         marques_ski=marques_ski)
