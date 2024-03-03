/*SQL script used to intialize the database. 
database_helper or SQLite3 command tool - create table , insert the default data
completed , excuted before server side procedure.*/
drop table if exists users;
drop table if exists loggedinusers;

create table loggedinusers(
    email text NOT NULL,
    token text NOT NULL
);

create table users(
    email text PRIMARY KEY NOT NULL,
    password text NOT NULL,
    firstname text NOT NULL,
    familyname text NOT NULL,
    gender text NOT NULL,
    city text NOT NULL,
    country text NOT NULL,
    messages text NOT NULL
);




