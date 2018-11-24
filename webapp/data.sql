becauseICare.sql


CREATE DATABASE becauseICare;

CREATE TABLE user (
id int auto_increment PRIMARY KEY,
username varchar(50)  NOT NULL,
password varchar(50) NOT NULL
);

CREATE TABLE items (
    iid int auto_increment PRIMARY KEY,
    item varchar(100) NOT NULL,
    finished_item varchar(100));