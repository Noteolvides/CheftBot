DROP DATABASE IF EXISTS CHEFBOT_USER;
CREATE DATABASE CHEFBOT_USER;
USE CHEFBOT_USER;

#Usuario
DROP TABLE IF EXISTS USER CASCADE;
CREATE TABLE USER (
	user_id		SERIAL,
	username	VARCHAR(255),
	status	    VARCHAR(255),
	token	    VARCHAR(255),-->Id de telegram, seria la clave primaria para buscar.
	created_at	DATE,
	current_keyboard ();
	PRIMARY KEY (user_id)
);

#Despensa
DROP TABLE IF EXISTS PANTRY CASCADE;
CREATE TABLE PANTRY (
	user_id		BIGINT(20) unsigned,
	ingredient	VARCHAR(255),
	quantity	VARCHAR(255),
	healthy	    BOOLEAN,
	img_path    VARCHAR(255),
	PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES USER(user_id)
);

#Recetes Personales
DROP TABLE IF EXISTS URECIPES CASCADE;
CREATE TABLE URECIPES (
	user_id		    BIGINT(20) unsigned,
	recipe_name   	VARCHAR(255),
	interest	    INTEGER,
	img_path        VARCHAR(255),
	steps_path      VARCHAR(255),   #path al documento que contiene los diferentes pasos que mostrará el bot
	PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES USER(user_id)
);

SELECT u.status FROM USER AS u WHERE u.username; #Queria hacer la query para que gus puede pedir status y luego adaptarla a python, pero da palo :_

#Si hay error esto a veces ayuda
SHOW ENGINE INNODB STATUS;


#Recetas que el usuario ya ha hecho.ABSOLUTE
#Lista de la compra