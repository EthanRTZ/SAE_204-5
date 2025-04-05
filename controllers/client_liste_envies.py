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
    # Récupération de l'ID de l'article sélectionné dans la wishlist (quand on clique sur son nom)
    id_article_detail = request.args.get('id_article_detail_wishlist')

    # Récupérer les articles de la liste d'envies avec leurs informations détaillées
    # On ajoute la jointure avec type_ski pour avoir le libellé de la catégorie
    sql = '''
    SELECT s.id_ski as id_article, s.nom_ski as nom, s.prix_ski as prix, s.stock as stock, s.photo_ski as image,
           t.libelle_type_ski as libelle
    FROM liste_envies le
    JOIN ski s ON le.id_article = s.id_ski
    LEFT JOIN type_ski t ON s.id_type_ski = t.id_type_ski
    WHERE le.id_client = %s
    ORDER BY le.date_ajout DESC
    '''
    mycursor.execute(sql, (id_client,))
    articles_liste_envies = mycursor.fetchall()

    # Compter les articles
    nombre_articles = len(articles_liste_envies)

    # Variables pour stocker les informations détaillées de l'article sélectionné
    info_wishlist = None
    info_wishlist_categorie = None
    
    # Si un article est sélectionné (clic sur son nom), on récupère ses détails
    if id_article_detail:
        # 1. Compter combien d'autres utilisateurs ont cet article dans leur wishlist
        sql = '''
        SELECT COUNT(*) as nb_wish_list_other
        FROM liste_envies
        WHERE id_article = %s AND id_client != %s
        '''
        mycursor.execute(sql, (id_article_detail, id_client))
        info_wishlist = mycursor.fetchone()
        # On ajoute le nom de l'article aux informations
        for article in articles_liste_envies:
            if str(article['id_article']) == str(id_article_detail):
                info_wishlist['nom'] = article['nom']
                break

        # 2. Compter le nombre d'articles de la même catégorie dans la wishlist de l'utilisateur
        sql = '''
        SELECT COUNT(*) as nb_wish_list_other_categorie, t.libelle_type_ski as libelle
        FROM liste_envies le
        JOIN ski s ON le.id_article = s.id_ski
        JOIN type_ski t ON s.id_type_ski = t.id_type_ski
        WHERE s.id_type_ski = (
            SELECT id_type_ski FROM ski WHERE id_ski = %s
        ) AND le.id_client = %s
        GROUP BY t.libelle_type_ski
        '''
        mycursor.execute(sql, (id_article_detail, id_client))
        info_wishlist_categorie = mycursor.fetchone()

        # 3. Mettre à jour ou insérer ces statistiques dans la table wishlist_details
        sql = '''
        INSERT INTO wishlist_details (id_article, id_utilisateur, nb_wish_list_other, nb_wish_list_other_categorie)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        nb_wish_list_other = %s,
        nb_wish_list_other_categorie = %s
        '''
        mycursor.execute(sql, (
            id_article_detail, 
            id_client, 
            info_wishlist['nb_wish_list_other'],
            info_wishlist_categorie['nb_wish_list_other_categorie'] if info_wishlist_categorie else 0,
            info_wishlist['nb_wish_list_other'],
            info_wishlist_categorie['nb_wish_list_other_categorie'] if info_wishlist_categorie else 0
        ))
        get_db().commit()

    # Historique (à remplir si besoin)
    articles_historique = []

    # On renvoie toutes les informations au template
    # - articles_liste_envies : la liste complète des articles dans la wishlist
    # - info_wishlist : les stats sur combien d'autres utilisateurs ont cet article
    # - info_wishlist_categorie : les stats sur les articles de même catégorie
    # - id_article_detail : l'ID de l'article sélectionné pour afficher ses détails
    return render_template('client/liste_envies/liste_envies_show.html',
                           articles_liste_envies=articles_liste_envies,
                           articles_historique=articles_historique,
                           nb_liste_envies=nombre_articles,
                           info_wishlist=info_wishlist,
                           info_wishlist_categorie=info_wishlist_categorie,
                           id_article_detail=id_article_detail)


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


@client_liste_envies.route('/client/envie/add-to-cart', methods=['POST'])
def client_liste_envies_add_to_cart():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')

    # 1. Vérifier le stock disponible
    sql = '''
    SELECT stock 
    FROM ski 
    WHERE id_ski = %s
    FOR UPDATE
    '''
    mycursor.execute(sql, (id_article,))
    result = mycursor.fetchone()

    if not result or result['stock'] <= 0:
        flash(u'Article momentanément indisponible', 'alert-warning')
        return redirect('/client/envies/show')

    # 2. Ajouter l'article au panier
    sql = '''
    INSERT INTO ligne_panier (id_utilisateur, id_ski, quantite) 
    VALUES (%s, %s, 1)
    ON DUPLICATE KEY UPDATE quantite = quantite + 1
    '''
    mycursor.execute(sql, (id_client, id_article))

    # 3. Mettre à jour le stock
    sql = '''UPDATE ski SET stock = stock - 1 WHERE id_ski = %s'''
    mycursor.execute(sql, (id_article,))

    # 4. Supprimer l'article de la liste d'envies
    sql = '''DELETE FROM liste_envies WHERE id_client = %s AND id_article = %s'''
    mycursor.execute(sql, (id_client, id_article))

    get_db().commit()
    flash(u'Article ajouté au panier et retiré de la liste d\'envies', 'alert-success')
    return redirect('/client/envies/show')
