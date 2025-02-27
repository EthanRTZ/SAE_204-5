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
    sql = '''
    SELECT s.*, t.libelle_type_ski as libelle, m.nom_marque
    FROM ski s
    LEFT JOIN type_ski t ON s.id_type_ski = t.id_type_ski
    LEFT JOIN marque m ON s.id_marque = m.id_marque
    WHERE 1=1
    '''
    params = []

    # Application des filtres
    if 'filter_word' in session and session['filter_word']:
        sql += ''' AND (s.nom_ski LIKE %s OR m.nom_marque LIKE %s)'''
        search_term = f"%{session['filter_word']}%"
        params.extend([search_term, search_term])

    if 'filter_prix_min' in session and session['filter_prix_min']:
        sql += ''' AND s.prix_ski >= %s'''
        params.append(session['filter_prix_min'])

    if 'filter_prix_max' in session and session['filter_prix_max']:
        sql += ''' AND s.prix_ski <= %s'''
        params.append(session['filter_prix_max'])

    if 'filter_types' in session and session['filter_types']:
        placeholders = ','.join(['%s'] * len(session['filter_types']))
        sql += f''' AND s.id_type_ski IN ({placeholders})'''
        params.extend(session['filter_types'])

    if 'filter_marques' in session and session['filter_marques']:
        placeholders = ','.join(['%s'] * len(session['filter_marques']))
        sql += f''' AND s.id_marque IN ({placeholders})'''
        params.extend(session['filter_marques'])

    # Exécution de la requête finale
    mycursor.execute(sql, tuple(params))
    articles = mycursor.fetchall()

    # Récupération du panier
    sql = '''
    SELECT s.*, lp.quantite, t.libelle_type_ski as libelle, m.nom_marque
    FROM ski s
    INNER JOIN ligne_panier lp ON s.id_ski = lp.id_ski
    LEFT JOIN type_ski t ON s.id_type_ski = t.id_type_ski
    LEFT JOIN marque m ON s.id_marque = m.id_marque
    WHERE lp.id_utilisateur = %s
    '''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()

    # Calcul du prix total du panier
    prix_total = None
    if articles_panier:
        sql = '''
        SELECT SUM(s.prix_ski * lp.quantite) as prix_total
        FROM ski s
        INNER JOIN ligne_panier lp ON s.id_ski = lp.id_ski
        WHERE lp.id_utilisateur = %s
        '''
        mycursor.execute(sql, (id_client,))
        result = mycursor.fetchone()
        prix_total = result['prix_total'] if result else None

    return render_template('client/boutique/panier_article.html',
                         articles=articles,
                         articles_panier=articles_panier,
                         prix_total=prix_total,
                         types_ski=types_ski,
                         marques_ski=marques_ski)
