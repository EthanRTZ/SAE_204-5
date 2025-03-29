#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                        template_folder='templates')


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    if not id_article:
        flash(u'Article invalide', 'alert-warning')
        return redirect('/client/article/show')

    quantite = int(request.form.get('quantite', 1))
    if quantite <= 0:
        flash(u'Quantité invalide', 'alert-warning')
        return redirect('/client/article/show')

    # Vérifier le stock disponible avec un SELECT FOR UPDATE pour éviter les conflits
    sql = '''SELECT stock FROM ski WHERE id_ski = %s FOR UPDATE'''
    mycursor.execute(sql, (id_article,))
    result = mycursor.fetchone()

    if not result:
        flash(u'Article non trouvé', 'alert-warning')
        return redirect('/client/article/show')

    if result['stock'] < quantite:
        flash(u'Stock insuffisant', 'alert-warning')
        return redirect('/client/article/show')

    # Vérifier si l'article est déjà dans le panier
    sql = '''SELECT quantite FROM ligne_panier 
             WHERE id_utilisateur = %s AND id_ski = %s FOR UPDATE'''
    mycursor.execute(sql, (id_client, id_article))
    panier_existant = mycursor.fetchone()

    if panier_existant:
        # Mettre à jour la quantité si l'article existe déjà
        nouvelle_quantite = panier_existant['quantite'] + quantite
        if nouvelle_quantite > result['stock']:
            flash(u'Stock insuffisant pour cette quantité totale', 'alert-warning')
            return redirect('/client/article/show')

        sql = '''UPDATE ligne_panier 
                 SET quantite = %s 
                 WHERE id_utilisateur = %s AND id_ski = %s'''
        mycursor.execute(sql, (nouvelle_quantite, id_client, id_article))
    else:
        # Ajouter l'article au panier
        sql = '''INSERT INTO ligne_panier (id_utilisateur, id_ski, quantite) 
                 VALUES (%s, %s, %s)'''
        mycursor.execute(sql, (id_client, id_article, quantite))

    # Mettre à jour le stock
    sql = '''UPDATE ski SET stock = stock - %s WHERE id_ski = %s'''
    mycursor.execute(sql, (quantite, id_article))

    get_db().commit()
    flash(u'Article ajouté au panier', 'alert-success')
    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')

    # Récupérer la quantité dans le panier
    sql = '''SELECT quantite FROM ligne_panier 
             WHERE id_utilisateur = %s AND id_ski = %s'''
    mycursor.execute(sql, (id_client, id_article))
    article_panier = mycursor.fetchone()

    if article_panier:
        if article_panier['quantite'] > 1:
            # Diminuer la quantité de 1
            sql = '''UPDATE ligne_panier 
                     SET quantite = quantite - 1 
                     WHERE id_utilisateur = %s AND id_ski = %s'''
            mycursor.execute(sql, (id_client, id_article))
        else:
            # Supprimer l'article du panier
            sql = '''DELETE FROM ligne_panier 
                     WHERE id_utilisateur = %s AND id_ski = %s'''
            mycursor.execute(sql, (id_client, id_article))

        # Remettre à jour le stock
        sql = '''UPDATE ski SET stock = stock + 1 WHERE id_ski = %s'''
        mycursor.execute(sql, (id_article,))
        
        get_db().commit()
    return redirect('/client/article/show')

@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']

    # Récupérer tous les articles du panier
    sql = '''SELECT id_ski, quantite FROM ligne_panier WHERE id_utilisateur = %s'''
    mycursor.execute(sql, (client_id,))
    items_panier = mycursor.fetchall()

    for item in items_panier:
        # Remettre à jour le stock pour chaque article
        sql = '''UPDATE ski SET stock = stock + %s WHERE id_ski = %s'''
        mycursor.execute(sql, (item['quantite'], item['id_ski']))

    # Vider le panier
    sql = '''DELETE FROM ligne_panier WHERE id_utilisateur = %s'''
    mycursor.execute(sql, (client_id,))
    
    get_db().commit()
    return redirect('/client/article/show')

@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')

    # Récupérer la quantité dans le panier
    sql = '''SELECT quantite FROM ligne_panier 
             WHERE id_utilisateur = %s AND id_ski = %s'''
    mycursor.execute(sql, (id_client, id_article))
    ligne_panier = mycursor.fetchone()

    if ligne_panier:
        # Remettre à jour le stock
        sql = '''UPDATE ski SET stock = stock + %s WHERE id_ski = %s'''
        mycursor.execute(sql, (ligne_panier['quantite'], id_article))

        # Supprimer la ligne du panier
        sql = '''DELETE FROM ligne_panier 
                 WHERE id_utilisateur = %s AND id_ski = %s'''
        mycursor.execute(sql, (id_client, id_article))
        
        get_db().commit()
    return redirect('/client/article/show')

@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    filter_word = request.form.get('filter_word', None)
    filter_prix_min = request.form.get('filter_prix_min', None)
    filter_prix_max = request.form.get('filter_prix_max', None)
    filter_types = request.form.getlist('filter_types')
    filter_marques = request.form.getlist('filter_marques')

    # Stockage des filtres en session
    if filter_word:
        session['filter_word'] = filter_word
    else:
        if 'filter_word' in session:
            session.pop('filter_word')

    if filter_prix_min:
        session['filter_prix_min'] = float(filter_prix_min)
    else:
        if 'filter_prix_min' in session:
            session.pop('filter_prix_min')

    if filter_prix_max:
        session['filter_prix_max'] = float(filter_prix_max)
    else:
        if 'filter_prix_max' in session:
            session.pop('filter_prix_max')

    if filter_types:
        session['filter_types'] = filter_types
    else:
        if 'filter_types' in session:
            session.pop('filter_types')

    if filter_marques:
        session['filter_marques'] = filter_marques
    else:
        if 'filter_marques' in session:
            session.pop('filter_marques')

    return redirect('/client/article/show')

@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    session.pop('filter_word', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    session.pop('filter_types', None)
    session.pop('filter_marques', None)
    return redirect('/client/article/show')
