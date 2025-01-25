-- Création des tables

CREATE TABLE longueur (
    id_longueur INT PRIMARY KEY AUTO_INCREMENT,
    libelle_taille INT NOT NULL
);

CREATE TABLE type_ski (
    id_type_ski INT PRIMARY KEY AUTO_INCREMENT,
    libelle_type_ski VARCHAR(50) NOT NULL
);

CREATE TABLE fournisseur (
    id_fournisseur INT PRIMARY KEY AUTO_INCREMENT,
    nom_fournisseur VARCHAR(100) NOT NULL
);

CREATE TABLE marque (
    id_marque INT PRIMARY KEY AUTO_INCREMENT,
    nom_marque VARCHAR(50) NOT NULL
);

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
);

-- Création de la table utilisateur
CREATE TABLE utilisateur (
    id_utilisateur INT PRIMARY KEY AUTO_INCREMENT,
    login VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    est_actif BOOLEAN DEFAULT true,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE ligne_panier (
    id_utilisateur INT,
    id_ski INT,
    quantite INT NOT NULL,
    date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_utilisateur, id_ski),
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur),
    FOREIGN KEY (id_ski) REFERENCES ski(id_ski)
);

-- Insertions des données de base
INSERT INTO longueur (libelle_taille) VALUES 
(150), (160), (170), (180);

INSERT INTO type_ski (libelle_type_ski) VALUES
('Ski de Piste'),
('Ski All Mountain'),
('Ski Freestyle'),
('Ski de Slalom'),
('Ski de Descente'),
('Ski de Randonnée'),
('Ski de Skating'),
('Ski Freeride');

INSERT INTO fournisseur (nom_fournisseur) VALUES
('SkiPro Distribution'),
('AlpineSports'),
('Mountain Equipment');

INSERT INTO marque (nom_marque) VALUES
('Rossignol'),
('Salomon'),
('Atomic'),
('Head'),
('Dynastar'),
('K2'),
('Völkl'),
('Nordica'),
('Elan');

INSERT INTO ski (nom_ski, prix_ski, largeur_ski, conseil_utilisation, id_longueur, id_type_ski, id_fournisseur, id_marque, photo_ski) VALUES
('Experience 80', 399.99, 80, 'Parfait pour les skieurs intermédiaires', 1, 1, 1, 1, 'static/images/experience-80.jpg'),
('QST 92', 549.99, 92, 'Idéal pour le tout-terrain', 2, 2, 2, 2, 'static/images/qst-92.jpg'),
('Redster X9', 699.99, 75, 'Pour la compétition et le ski sportif', 3, 4, 3, 3, 'static/images/redster-x9.jpg'),
('M-Pro 99', 799.99, 99, 'Ski polyvalent freeride, excellent en poudreuse', 2, 8, 1, 5, 'static/images/m-pro-99.jpg'),
('Legend X96', 749.99, 96, 'Pour les skieurs experts cherchant de la performance en tout-terrain', 3, 2, 2, 5, 'static/images/legend-x96.jpg'),
('M-Free 108', 849.99, 108, 'Ski freeride pour la poudreuse profonde', 4, 8, 3, 5, 'static/images/m-free-108.jpg'),
('Speed Zone 4x4 82', 599.99, 82, 'Ski all-mountain performant sur piste', 2, 2, 1, 5, 'static/images/speed-zone-4x4-82.jpg'),
('Mantra V.Werks', 999.99, 96, 'Ski haut de gamme pour skieur technique', 3, 2, 2, 7, 'static/images/mantra-vwerks.jpg'),
('Mindbender 99Ti', 729.99, 99, 'Excellent en conditions variables', 3, 2, 3, 6, 'static/images/mindbender-99ti.jpg'),
('Stance 96', 649.99, 96, 'Polyvalent pour tous types de neige', 2, 2, 1, 2, 'static/images/stance-96.jpg'),
('Race Tiger SL', 899.99, 68, 'Ski de slalom pour compétiteur', 2, 4, 1, 7, 'static/images/race-tiger-sl.jpg'),
('S/Race Rush SL', 849.99, 65, 'Ski de slalom haute performance', 2, 4, 2, 2, 'static/images/srace-rush-sl.jpg'),
('Backland 85', 699.99, 85, 'Ski de randonnée léger et polyvalent', 3, 6, 3, 3, 'static/images/backland-85.jpg'),
('QST Blank', 799.99, 112, 'Ski freeride pour poudreuse profonde', 4, 8, 1, 2, 'static/images/qst-blank.jpg'),
('NFX', 549.99, 85, 'Ski freestyle park et pipe', 2, 3, 2, 1, 'static/images/nfx.jpg'),
('ARV 106', 729.99, 106, 'Ski freestyle backcountry', 3, 3, 3, 2, 'static/images/arv-106.jpg'),
('RC4 WC CT', 999.99, 72, 'Ski de course haut niveau', 2, 5, 1, 4, 'static/images/rc4-wc-ct.jpg'),
('Skating RS', 449.99, 43, 'Ski de skating pour compétition', 1, 7, 2, 5, 'static/images/skating-rs.jpg'),
('Wayback 98', 779.99, 98, 'All mountain pour skieur expert', 3, 2, 3, 6, 'static/images/wayback-98.jpg'),
('Enforcer 94', 749.99, 94, 'All mountain performant', 2, 2, 1, 8, 'static/images/enforcer-94.jpg'),
('Kore 93', 699.99, 93, 'All mountain léger', 3, 2, 2, 4, 'static/images/kore-93.jpg'),
('Soul Rider 87', 599.99, 87, 'Freestyle all mountain', 2, 3, 3, 8, 'static/images/soul-rider-87.jpg'),
('MTN Explore 95', 829.99, 95, 'Randonnée haute performance', 3, 6, 1, 2, 'static/images/mtn-explore-95.jpg'),
('V-Shape V10', 649.99, 85, 'Ski de piste sportif', 2, 1, 2, 4, 'static/images/v-shape-v10.jpg'),
('Ripstick 96', 779.99, 96, 'All mountain freestyle', 3, 2, 3, 9, 'static/images/ripstick-96.jpg');

-- Version 1 : Avec hachage pbkdf2:sha256
INSERT INTO utilisateur(id_utilisateur, login, email, password, role, nom, est_actif) VALUES
(1, 'admin', 'admin@admin.fr',
    'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988',
    'ROLE_admin', 'admin', '1'),
(2, 'client', 'client@client.fr',
    'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349',
    'ROLE_client', 'client', '1'),
(3, 'client2', 'client2@client2.fr',
    'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080',
    'ROLE_client', 'client2', '1');
