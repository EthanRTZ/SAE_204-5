#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                        template_folder='templates')

@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')

@admin_commande.route('/admin/commande/show')
def admin_commande_show():
    mycursor = get_db().cursor()
    
    # Récupération de toutes les commandes avec les informations des clients
    sql = '''
    SELECT c.*, u.nom as nom_client, u.email as email_client,
           COUNT(lc.id_ski) as nb_articles,
           SUM(lc.quantite * lc.prix) as prix_total
    FROM commande c
    INNER JOIN utilisateur u ON c.id_utilisateur = u.id_utilisateur
    LEFT JOIN ligne_commande lc ON c.id_commande = lc.id_commande
    GROUP BY c.id_commande
    ORDER BY c.date_achat DESC
    '''
    mycursor.execute(sql)
    commandes = mycursor.fetchall()

    return render_template('admin/commandes/show.html',
                         commandes=commandes)

@admin_commande.route('/admin/commande/details/<int:id_commande>')
def admin_commande_details(id_commande):
    mycursor = get_db().cursor()

    # Informations sur la commande et le client
    sql = '''
    SELECT c.*, u.* 
    FROM commande c
    INNER JOIN utilisateur u ON c.id_utilisateur = u.id_utilisateur
    WHERE c.id_commande = %s
    '''
    mycursor.execute(sql, (id_commande,))
    commande = mycursor.fetchone()

    if not commande:
        flash(u'Commande non trouvée', 'alert-warning')
        return redirect('/admin/commande/show')

    # Détails des articles de la commande
    sql = '''
    SELECT s.nom_ski, s.stock, lc.quantite, lc.prix, lc.quantite * lc.prix as prix_ligne
    FROM ligne_commande lc
    INNER JOIN ski s ON lc.id_ski = s.id_ski
    WHERE lc.id_commande = %s
    '''
    mycursor.execute(sql, (id_commande,))
    articles_commande = mycursor.fetchall()

    return render_template('admin/commandes/details.html',
                         commande=commande,
                         articles_commande=articles_commande)

@admin_commande.route('/admin/commande/valider/<int:id_commande>', methods=['POST'])
def admin_commande_valider(id_commande):
    mycursor = get_db().cursor()
    nouvel_etat = request.form.get('nouvel_etat', 'en préparation')
    
    # Mise à jour de l'état de la commande
    sql = '''UPDATE commande SET etat = %s WHERE id_commande = %s'''
    mycursor.execute(sql, (nouvel_etat, id_commande))
    get_db().commit()
    
    flash(u'État de la commande mis à jour', 'alert-success')
    return redirect('/admin/commande/details/' + str(id_commande))

@admin_commande.route('/admin/stock/show')
def admin_stock_show():
    mycursor = get_db().cursor()
    
    # Récupération de tous les articles avec leur stock
    sql = '''
    SELECT s.*, t.libelle_type_ski, m.nom_marque,
           (SELECT COUNT(*) FROM ligne_commande lc 
            INNER JOIN commande c ON lc.id_commande = c.id_commande 
            WHERE lc.id_ski = s.id_ski AND c.etat = 'en cours') as nb_commandes_en_cours
    FROM ski s
    LEFT JOIN type_ski t ON s.id_type_ski = t.id_type_ski
    LEFT JOIN marque m ON s.id_marque = m.id_marque
    ORDER BY s.stock ASC
    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()

    return render_template('admin/stock/show.html',
                         articles=articles)

@admin_commande.route('/admin/stock/edit/<int:id_ski>', methods=['POST'])
def admin_stock_edit(id_ski):
    mycursor = get_db().cursor()
    nouveau_stock = request.form.get('nouveau_stock', type=int)
    
    if nouveau_stock is None or nouveau_stock < 0:
        flash(u'Stock invalide', 'alert-danger')
        return redirect('/admin/stock/show')
    
    # Mise à jour du stock
    sql = '''UPDATE ski SET stock = %s WHERE id_ski = %s'''
    mycursor.execute(sql, (nouveau_stock, id_ski))
    get_db().commit()
    
    flash(u'Stock mis à jour', 'alert-success')
    return redirect('/admin/stock/show')
