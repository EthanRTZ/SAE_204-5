#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import *
import datetime
from decimal import *
from connexion_db import get_db

fixtures_load = Blueprint('fixtures_load', __name__,
                        template_folder='templates')

@fixtures_load.route('/base/init')
def fct_fixtures_load():
    mycursor = get_db().cursor()
    
    # Suppression des tables existantes
    sql = '''DROP TABLE IF EXISTS ligne_panier, ligne_commande, commande, ski, marque, fournisseur, type_ski, longueur, utilisateur'''
    mycursor.execute(sql)
    
    # Création des tables dans l'ordre
    sql = '''
    CREATE TABLE longueur (
        id_longueur INT PRIMARY KEY AUTO_INCREMENT,
        libelle_taille INT NOT NULL
    );'''
    mycursor.execute(sql)
    
    sql = '''
    CREATE TABLE type_ski (
        id_type_ski INT PRIMARY KEY AUTO_INCREMENT,
        libelle_type_ski VARCHAR(50) NOT NULL
    );'''
    mycursor.execute(sql)
    
    sql = '''
    CREATE TABLE fournisseur (
        id_fournisseur INT PRIMARY KEY AUTO_INCREMENT,
        nom_fournisseur VARCHAR(100) NOT NULL
    );'''
    mycursor.execute(sql)
    
    sql = '''
    CREATE TABLE marque (
        id_marque INT PRIMARY KEY AUTO_INCREMENT,
        nom_marque VARCHAR(50) NOT NULL
    );'''
    mycursor.execute(sql)
    
    sql = '''
    CREATE TABLE ski (
        id_ski INT PRIMARY KEY AUTO_INCREMENT,
        nom_ski VARCHAR(100) NOT NULL,
        prix_ski DECIMAL(10,2) NOT NULL,
        largeur_ski INT NOT NULL,
        conseil_utilisation TEXT,
        id_longueur INT,
        id_type_ski INT,
        id_fournisseur INT,
        id_marque INT,
        photo_ski VARCHAR(255),
        FOREIGN KEY (id_longueur) REFERENCES longueur(id_longueur),
        FOREIGN KEY (id_type_ski) REFERENCES type_ski(id_type_ski),
        FOREIGN KEY (id_fournisseur) REFERENCES fournisseur(id_fournisseur),
        FOREIGN KEY (id_marque) REFERENCES marque(id_marque)
    );'''
    mycursor.execute(sql)
    
    # Insertion des données de base
    sql = '''INSERT INTO longueur (libelle_taille) VALUES 
    (150), (160), (170), (180);'''
    mycursor.execute(sql)
    
    sql = '''INSERT INTO type_ski (libelle_type_ski) VALUES
    ('Ski de Piste'),
    ('Ski All Mountain'),
    ('Ski Freestyle'),
    ('Ski de Slalom'),
    ('Ski de Descente'),
    ('Ski de Randonnée'),
    ('Ski de Skating'),
    ('Ski Freeride');'''
    mycursor.execute(sql)
    
    sql = '''INSERT INTO fournisseur (nom_fournisseur) VALUES 
    ('Intersport'),
    ('Décathlon'),
    ('Go Sport'),
    ('Sport 2000');'''
    mycursor.execute(sql)

    sql = '''INSERT INTO marque (nom_marque) VALUES 
    ('Salomon'),
    ('Rossignol'),
    ('Atomic'),
    ('Head'),
    ('Fischer'),
    ('K2'),
    ('Völkl'),
    ('Dynastar'),
    ('Elan'),
    ('Black Crows');'''
    mycursor.execute(sql)

    sql = '''INSERT INTO ski (nom_ski, prix_ski, largeur_ski, conseil_utilisation, id_longueur, id_type_ski, id_fournisseur, id_marque, photo_ski) VALUES
    ('MTN Explore 95', 829.99, 95, 'Randonnée haute performance', 3, 6, 1, 2, 'static/images/mtn-explore-95.jpg'),
    ('V-Shape V10', 649.99, 85, 'Ski de piste sportif', 2, 1, 2, 4, 'static/images/v-shape-v10.jpg'),
    ('Ripstick 96', 779.99, 96, 'All mountain freestyle', 3, 2, 3, 9, 'static/images/ripstick-96.jpg');'''
    mycursor.execute(sql)

    sql = '''INSERT INTO utilisateur(id_utilisateur, login, email, password, role, nom, est_actif) VALUES
    (1, 'admin', 'admin@admin.fr',
        'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988',
        'ROLE_admin', 'admin', '1'),
    (2, 'client', 'client@client.fr',
        'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349',
        'ROLE_client', 'client', '1'),
    (3, 'client2', 'client2@client2.fr',
        'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080',
        'ROLE_client', 'client2', '1');'''
    mycursor.execute(sql)

    # Tables pour les commandes et le panier
    sql = '''CREATE TABLE ligne_panier (
        id_utilisateur INT,
        id_ski INT,
        quantite INT NOT NULL,
        date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id_utilisateur, id_ski),
        FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur),
        FOREIGN KEY (id_ski) REFERENCES ski(id_ski)
    );'''
    mycursor.execute(sql)

    sql = '''CREATE TABLE commande (
        id_commande INT PRIMARY KEY AUTO_INCREMENT,
        id_utilisateur INT,
        date_achat DATETIME DEFAULT CURRENT_TIMESTAMP,
        etat VARCHAR(20) DEFAULT 'en cours',
        FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur)
    );'''
    mycursor.execute(sql)

    sql = '''CREATE TABLE ligne_commande (
        id_commande INT,
        id_ski INT,
        quantite INT NOT NULL,
        prix DECIMAL(10,2) NOT NULL,
        PRIMARY KEY (id_commande, id_ski),
        FOREIGN KEY (id_commande) REFERENCES commande(id_commande),
        FOREIGN KEY (id_ski) REFERENCES ski(id_ski)
    );'''
    mycursor.execute(sql)
    
    get_db().commit()
    return redirect('/')

