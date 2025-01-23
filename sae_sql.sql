CREATE TABLE longueur (
    id_longueur INT PRIMARY KEY AUTO_INCREMENT,
    libelle_taille INT NOT NULL UNIQUE
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
    conseil_utilisation TEXT,
    id_longueur INT,
    id_type_ski INT,
    id_fournisseur INT,
    id_marque INT,
    FOREIGN KEY (id_longueur) REFERENCES longueur(id_longueur),
    FOREIGN KEY (id_type_ski) REFERENCES type_ski(id_type_ski),
    FOREIGN KEY (id_fournisseur) REFERENCES fournisseur(id_fournisseur),
    FOREIGN KEY (id_marque) REFERENCES marque(id_marque)
);



INSERT INTO longueur (libelle_taille) VALUES 
(150),
(160),
(170),
(180);


INSERT INTO type_ski (libelle_type_ski) VALUES
('Ski Alpin'),
('Ski de Fond'),
('Ski de Randonnée'),
('Ski Freestyle');


INSERT INTO fournisseur (nom_fournisseur) VALUES
('SkiPro Distribution'),
('AlpineSports'),
('Mountain Equipment');


INSERT INTO marque (nom_marque) VALUES
('Rossignol'),
('Salomon'),
('Atomic'),
('Head');


INSERT INTO ski (nom_ski, prix_ski, conseil_utilisation, id_longueur, id_type_ski, id_fournisseur, id_marque) VALUES
('Experience 80', 399.99, 'Parfait pour les skieurs intermédiaires', 1, 1, 1, 1),
('QST 92', 549.99, 'Idéal pour le tout-terrain', 2, 1, 2, 2),
('Redster X9', 699.99, 'Pour la compétition et le ski sportif', 3, 1, 3, 3);
