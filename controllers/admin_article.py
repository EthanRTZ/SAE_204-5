#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash, session
from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_article = Blueprint('admin_article', __name__,
                          template_folder='templates')


@admin_article.route('/admin/article/show')
def admin_article_show():
    mycursor = get_db().cursor()
    
    # Récupération de tous les articles avec leurs informations
    sql = '''
    SELECT s.*, t.libelle_type_ski, m.nom_marque, l.libelle_taille, f.nom_fournisseur
    FROM ski s
    LEFT JOIN type_ski t ON s.id_type_ski = t.id_type_ski
    LEFT JOIN marque m ON s.id_marque = m.id_marque
    LEFT JOIN longueur l ON s.id_longueur = l.id_longueur
    LEFT JOIN fournisseur f ON s.id_fournisseur = f.id_fournisseur
    ORDER BY s.nom_ski
    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()

    # Récupération des types de ski
    sql = '''SELECT * FROM type_ski ORDER BY libelle_type_ski'''
    mycursor.execute(sql)
    types_ski = mycursor.fetchall()

    # Récupération des marques
    sql = '''SELECT * FROM marque ORDER BY nom_marque'''
    mycursor.execute(sql)
    marques = mycursor.fetchall()

    # Récupération des longueurs
    sql = '''SELECT * FROM longueur ORDER BY libelle_taille'''
    mycursor.execute(sql)
    longueurs = mycursor.fetchall()

    # Récupération des fournisseurs
    sql = '''SELECT * FROM fournisseur ORDER BY nom_fournisseur'''
    mycursor.execute(sql)
    fournisseurs = mycursor.fetchall()

    return render_template('admin/article/show.html',
                         articles=articles,
                         types_ski=types_ski,
                         marques=marques,
                         longueurs=longueurs,
                         fournisseurs=fournisseurs)


@admin_article.route('/admin/article/add', methods=['GET', 'POST'])
def admin_article_add():
    if request.method == 'POST':
        mycursor = get_db().cursor()

        nom = request.form.get('nom', '')
        prix = request.form.get('prix', type=float)
        largeur = request.form.get('largeur', type=int)
        conseil = request.form.get('conseil', '')
        stock = request.form.get('stock', type=int)
        id_type = request.form.get('type', type=int)
        id_marque = request.form.get('marque', type=int)
        id_longueur = request.form.get('longueur', type=int)
        id_fournisseur = request.form.get('fournisseur', type=int)

        # Validation des données
        if not all([nom, prix, largeur, stock, id_type, id_marque, id_longueur, id_fournisseur]):
            flash(u'Tous les champs obligatoires doivent être remplis', 'alert-warning')
            return redirect('/admin/article/show')

        # Gestion de l'upload de photo
        photo = request.files.get('photo')
        photo_path = None
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo_path = os.path.join('static/images', filename)
            photo.save(os.path.join('static/images', filename))

        # Insertion de l'article
        sql = '''
        INSERT INTO ski (nom_ski, prix_ski, largeur_ski, conseil_utilisation, 
                       stock, id_type_ski, id_marque, id_longueur, id_fournisseur, photo_ski)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        mycursor.execute(sql, (nom, prix, largeur, conseil, stock,
                               id_type, id_marque, id_longueur, id_fournisseur, photo_path))
        get_db().commit()

        flash(u'Article ajouté avec succès', 'alert-success')

        return redirect('/admin/article/show')


@admin_article.route('/admin/article/edit/<int:id_article>', methods=['POST'])
def admin_article_edit(id_article):
    mycursor = get_db().cursor()

    nom = request.form.get('nom', '')
    prix = request.form.get('prix', type=float)
    largeur = request.form.get('largeur', type=int)
    conseil = request.form.get('conseil', '')
    stock = request.form.get('stock', type=int)
    id_type = request.form.get('type', type=int)
    id_marque = request.form.get('marque', type=int)
    id_longueur = request.form.get('longueur', type=int)
    id_fournisseur = request.form.get('fournisseur', type=int)

    # Validation des données
    if not all([nom, prix, largeur, stock, id_type, id_marque, id_longueur, id_fournisseur]):
        flash(u'Tous les champs obligatoires doivent être remplis', 'alert-warning')
        return redirect('/admin/article/show')

    # Gestion de l'upload de photo
    photo = request.files.get('photo')
    photo_path = None
    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        photo_path = os.path.join('static/images', filename)
        photo.save(os.path.join('static/images', filename))

        # Mise à jour avec nouvelle photo
        sql = '''
        UPDATE ski 
        SET nom_ski = %s, prix_ski = %s, largeur_ski = %s, conseil_utilisation = %s,
            stock = %s, id_type_ski = %s, id_marque = %s, id_longueur = %s, 
            id_fournisseur = %s, photo_ski = %s
        WHERE id_ski = %s
        '''
        mycursor.execute(sql, (nom, prix, largeur, conseil, stock,
                               id_type, id_marque, id_longueur, id_fournisseur,
                               photo_path, id_article))
    else:
        # Mise à jour sans changer la photo
        sql = '''
        UPDATE ski 
        SET nom_ski = %s, prix_ski = %s, largeur_ski = %s, conseil_utilisation = %s,
            stock = %s, id_type_ski = %s, id_marque = %s, id_longueur = %s, 
            id_fournisseur = %s
        WHERE id_ski = %s
        '''
        mycursor.execute(sql, (nom, prix, largeur, conseil, stock,
                               id_type, id_marque, id_longueur, id_fournisseur, id_article))

    get_db().commit()
    flash(u'Article modifié avec succès', 'alert-success')

    return redirect('/admin/article/show')


@admin_article.route('/admin/article/delete/<int:id_article>', methods=['POST'])
def admin_article_delete(id_article):
    mycursor = get_db().cursor()

    # Vérifier si l'article est dans des commandes
    sql = '''
    SELECT COUNT(*) as nb_commandes 
    FROM ligne_commande 
    WHERE id_ski = %s
    '''
    mycursor.execute(sql, (id_article,))
    result = mycursor.fetchone()

    if result['nb_commandes'] > 0:
        flash(u'Impossible de supprimer cet article car il est présent dans des commandes', 'alert-warning')
        return redirect('/admin/article/show')

    # Supprimer l'article du panier
    sql = '''DELETE FROM ligne_panier WHERE id_ski = %s'''
    mycursor.execute(sql, (id_article,))

    # Supprimer l'article
    sql = '''DELETE FROM ski WHERE id_ski = %s'''
    mycursor.execute(sql, (id_article,))

    get_db().commit()
    flash(u'Article supprimé avec succès', 'alert-success')

    return redirect('/admin/article/show')


@admin_article.route('/admin/article/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    article=[]
    commentaires = {}
    return render_template('admin/article/show_avis.html'
                           , article=article
                           , commentaires=commentaires
                           )


@admin_article.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    article_id = request.form.get('idArticle', None)
    userId = request.form.get('idUser', None)

    return admin_avis(article_id)
