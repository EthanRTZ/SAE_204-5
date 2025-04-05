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
    # Initialisation des variables
    nombre_articles = 0
    articles_liste_envies = []
    articles_historique = []
    info_wishlist = None
    info_wishlist_categorie = None

    # Récupération de l'ID de l'article sélectionné dans la wishlist
    id_article_detail = request.args.get('id_article_detail_wishlist')

    try:
        # Récupérer les articles de la liste d'envies avec leurs informations détaillées
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
        nombre_articles = len(articles_liste_envies)

        # Récupérer l'historique
        sql = '''
                SELECT 
                    s.nom_ski as nom,
                    s.prix_ski as prix,
                    s.photo_ski as image,
                    s.id_ski as id_article
                FROM historique h
                JOIN ski s ON h.id_article = s.id_ski
                WHERE h.id_client = %s
                ORDER BY h.date_consultation DESC
                '''
        mycursor.execute(sql, (id_client,))
        articles_historique = mycursor.fetchall()

        # Si un article est sélectionné, récupérer ses détails
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

            # 2. Compter le nombre d'articles de la même catégorie
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

            if info_wishlist:
                # 3. Mettre à jour les statistiques
                sql = '''
                            INSERT INTO wishlist_details 
                                (id_article, id_utilisateur, nb_wish_list_other, nb_wish_list_other_categorie)
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

    except Exception as e:
        flash(f"Une erreur s'est produite : {str(e)}", "error")

    nb_liste_historique = len(articles_historique)

    return render_template('client/liste_envies/liste_envies_show.html',
                           articles_liste_envies=articles_liste_envies,
                           articles_historique=articles_historique,
                           nb_liste_envies=nombre_articles,
                           nb_liste_historique=nb_liste_historique,
                           info_wishlist=info_wishlist,
                           info_wishlist_categorie=info_wishlist_categorie,
                           id_article_detail=id_article_detail)


def client_historique_add(article_id, client_id):
    mycursor = get_db().cursor()
    client_id = session['id_user']
    # rechercher si l'article pour cet utilisateur est dans l'historique
    sql = '''
    SELECT *
    FROM historique
    WHERE id_client = %s AND id_article = %s
    '''
    mycursor.execute(sql, (client_id, article_id))
    historique_produit = mycursor.fetchone()

    # Compter le nombre total d'articles dans l'historique
    sql = '''
    SELECT COUNT(*) as nb_articles
    FROM historique
    WHERE id_client = %s
    '''
    mycursor.execute(sql, (client_id,))
    nb_articles = mycursor.fetchone()['nb_articles']

    if historique_produit:
        # Si l'article existe déjà, mettre à jour la date
        sql = '''
        UPDATE historique
        SET date_consultation = CURRENT_TIMESTAMP
        WHERE id_client = %s AND id_article = %s
        '''
        mycursor.execute(sql, (client_id, article_id))
    else:
        # Si l'historique est plein (6 articles), supprimer le plus ancien
        if nb_articles >= 6:
            sql = '''
            DELETE FROM historique
            WHERE id_client = %s
            ORDER BY date_consultation ASC
            LIMIT 1
            '''
            mycursor.execute(sql, (client_id,))

        # Ajouter le nouvel article
        sql = '''
        INSERT INTO historique (id_client, id_article, date_consultation)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
        '''
        mycursor.execute(sql, (client_id, article_id))

    get_db().commit()


@client_liste_envies.route('/client/envies/up', methods=['get'])
@client_liste_envies.route('/client/envies/down', methods=['get'])
@client_liste_envies.route('/client/envies/last', methods=['get'])
@client_liste_envies.route('/client/envies/first', methods=['get'])
def client_liste_envies_article_move():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')

    return redirect('/client/envies/show')
