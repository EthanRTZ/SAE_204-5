#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                        template_folder='templates')


# validation de la commande : partie 2 -- vue pour choisir les adresses (livraision et facturation)
@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = ''' selection des articles d'un panier 
    '''
    articles_panier = []
    if len(articles_panier) >= 1:
        sql = ''' calcul du prix total du panier '''
        prix_total = None
    else:
        prix_total = None
    # etape 2 : selection des adresses
    return render_template('client/boutique/panier_validation_adresses.html'
                           #, adresses=adresses
                           , articles_panier=articles_panier
                           , prix_total= prix_total
                           , validation=1
                           #, id_adresse_fav=id_adresse_fav
                           )


@client_commande.route('/client/commande/add', methods=['POST', 'GET'])
def client_commande_add():
    try:
        mycursor = get_db().cursor()
        id_client = session['id_user']

        # Sélection du contenu du panier de l'utilisateur
        sql = '''
        SELECT s.*, lp.quantite, s.prix_ski * lp.quantite as prix_ligne
        FROM ski s
        INNER JOIN ligne_panier lp ON s.id_ski = lp.id_ski
        WHERE lp.id_utilisateur = %s
        '''
        mycursor.execute(sql, (id_client,))
        items_ligne_panier = mycursor.fetchall()

        if not items_ligne_panier or len(items_ligne_panier) < 1:
            flash(u'Pas d\'articles dans le panier', 'alert-warning')
            return redirect('/client/article/show')

        # Calcul du prix total
        prix_total = sum(item['prix_ligne'] for item in items_ligne_panier)

        # Création de la commande
        sql = '''
        INSERT INTO commande(id_utilisateur, date_achat, etat)
        VALUES (%s, NOW(), 'en cours')
        '''
        mycursor.execute(sql, (id_client,))

        # Récupération de l'ID de la commande
        sql = '''SELECT LAST_INSERT_ID() as last_insert_id'''
        mycursor.execute(sql)
        id_commande = mycursor.fetchone()['last_insert_id']

        # Ajout des lignes de commande
        for item in items_ligne_panier:
            sql = '''
            INSERT INTO ligne_commande(id_commande, id_ski, quantite, prix)
            VALUES (%s, %s, %s, %s)
            '''
            mycursor.execute(sql, (id_commande, item['id_ski'], item['quantite'], item['prix_ski']))

        # Suppression du panier
        sql = '''DELETE FROM ligne_panier WHERE id_utilisateur = %s'''
        mycursor.execute(sql, (id_client,))

        get_db().commit()
        flash(u'Commande validée avec succès', 'alert-success')
        return redirect('/client/article/show')

    except Exception as e:
        print("Erreur lors de la commande:", str(e))
        get_db().rollback()
        flash(u'Erreur lors de la validation de la commande', 'alert-danger')
        return redirect('/client/article/show')


@client_commande.route('/client/commande/show', methods=['GET'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Récupération des commandes de l'utilisateur
    sql = '''
    SELECT c.*, 
           COUNT(lc.id_ski) as nb_articles,
           SUM(lc.quantite * lc.prix) as prix_total
    FROM commande c
    LEFT JOIN ligne_commande lc ON c.id_commande = lc.id_commande
    WHERE c.id_utilisateur = %s
    GROUP BY c.id_commande
    ORDER BY c.date_achat DESC
    '''
    mycursor.execute(sql, (id_client,))
    commandes = mycursor.fetchall()

    return render_template('client/commandes/show.html',
                         commandes=commandes)

@client_commande.route('/client/commande/details/<int:id_commande>', methods=['GET'])
def client_commande_details(id_commande):
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Vérification que la commande appartient bien au client
    sql = '''
    SELECT c.* 
    FROM commande c
    WHERE c.id_commande = %s AND c.id_utilisateur = %s
    '''
    mycursor.execute(sql, (id_commande, id_client))
    commande = mycursor.fetchone()

    if not commande:
        flash(u'Commande non trouvée', 'alert-warning')
        return redirect('/client/commande/show')

    # Récupération des détails de la commande
    sql = '''
    SELECT s.nom_ski, lc.quantite, lc.prix, lc.quantite * lc.prix as prix_ligne
    FROM ligne_commande lc
    INNER JOIN ski s ON lc.id_ski = s.id_ski
    WHERE lc.id_commande = %s
    '''
    mycursor.execute(sql, (id_commande,))
    articles_commande = mycursor.fetchall()

    return render_template('client/commandes/details.html',
                         commande=commande,
                         articles_commande=articles_commande)

