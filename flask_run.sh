#!/bin/bash

HOST=SAE2024grp20.mysql.pythonanywhere-services.com
LOGIN=SAE2024grp20
PASSWORD=zqsd2025
DATABASE=SAE2024grp20$default

sed -i "s/host=./host="${HOST}",/g" connexion_db.py
sed -i "s/user=./user="${LOGIN}",/g" connexion_db.py
sed -i "s/password=./password="${PASSWORD}",/g" connexion_db.py
sed -i "s/database=./database="${DATABASE}",/g" connexion_db.py

Vérification du fichier SQL
projet=$(ls -l sql_projet.sql)
if [ $? -ne 0 ]
then
    echo -e "\033[0;31m \n* pas de fichier sql_projet.sql \033[0m"
    nb_fic_sql=$(ls -l .sql | wc -l)
    if [ "${nb_fic_sql}" -eq "1" ]
    then
        NOM_FIC_SQL=$(echo.sql)
        cp "$NOM_FIC_SQL" sql_projet.sql
        echo -e "\033[0;32m \n* fichier copier $NOM_FIC_SQL sql_projet.sql \033[0m"
    else
        echo -e "\033[0;31m \n* pas de fichier **.sql \033[0m"
        exit 2
    fi
fi

Création de la base de données et exécution du script SQL
echo "DROP DATABASE IF EXISTS ${DATABASE}; CREATE DATABASE ${DATABASE};" | mysql --user=${LOGIN} --password=${PASSWORD} --host=${HOST} ${DATABASE}
mysql --user=${LOGIN} --password=${PASSWORD} --host=${HOST} ${DATABASE} < sql_projet.sql

Démarrage de l'application Flask
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
