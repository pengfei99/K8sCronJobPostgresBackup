# Postgres DB server backup and restore

In this document, I will show you how to use psql client (i.e. pg_dump, pg_dumpall) to create backups of tables, dbs or
even the whole postgresql server.

We assume you already have a postgresql server up running, and you are able to login into it. If not, please check my
other tutorial on how to install a postgresql server.



## 1.0 Initialize a database for testing

If you don't have a client, you can install it by using:
```shell
# install psql client on ubuntu
sudo apt-get install postgresql-client

# connect to the db server
psql -U user-pengfei -h 10.233.30.220 -p 5432 
```

### 1.1 Create a database
Note after connecting to the db server, you are no longer on a shell, you are on the psql terminal. So you can only
run psql commands now. The shell command won't work here.

```postgresql
create database school;
```


### 1.2 create tables

```postgresql
CREATE TABLE students(id INTEGER,f_name VARCHAR(20), l_name VARCHAR(20));

CREATE TABLE classes(id INTEGER, subject VARCHAR(20));

```

### 1.3 Populate the tables
```postgresql
INSERT INTO students(id, f_name, l_name) VALUES (1, 'John', 'Doe'), (2, 'Tim', 'Hampt'), (3, 'Alice', 'Dean'), (4, 'Johnny', 'Rames')
, (5, 'Bob', 'Haha'), (6, 'Jane', 'Titi');
INSERT INTO classes(id, subject) VALUES (1, 'Math'), (2, 'Science'), (3, 'Biology'), (4, 'Computer Science'), (5, 'PE') , (6, 'History');
```


### 1.4 show the created tables
Note **\dt** is the postgresql command not a standard sql command
```postgresql
-- show tables
\dt
-- show the content of a table
select * from students;
```



## 2 Backup your database by using pg_dump

### 2.1 Backup a single table
Below is the general form for dumping one table of a database. Note you need to create the directory dumps, if it does not exist
```shell
# general form
pg_dump -U <login> -h <host> -p <port> -t <table_name> <db_name> > /path/to/backup_file

# In this example, we only backup the students table of database school
pg_dump -U user-pengfei -h 10.233.30.220 -p 5432 -t students school > ~/dumps/students.sql

```

Now you should see the dump of the table in the students.sql. The content looks like
```postgresql
--
-- PostgreSQL database dump
--

-- Dumped from database version 12.7
-- Dumped by pg_dump version 13.5 (Debian 13.5-0+deb11u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: students; Type: TABLE; Schema: public; Owner: user-pengfei
--

CREATE TABLE public.students (
    id integer,
    f_name character varying(20),
    l_name character varying(20)
);


ALTER TABLE public.students OWNER TO "user-pengfei";

--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: user-pengfei
--

COPY public.students (id, f_name, l_name) FROM stdin;
1       John    Thorn
2       Phil    Hampt
3       Sue     Dean
4       Johnny  Rames
\.


--
-- PostgreSQL database dump complete
--
```

### 2.2 Test the backup
To test your backup, we will delete the table, and restore it by using the backup file

```postgresql
DROP TABLE students;

-- check the tables after deletion
\dt
```

To apply the backup, we use below command

```shell
psql -U user-pengfei -h 10.233.30.220 -p 5432 -W -d school -f ./dumps/students.sql

```

### 2.3 Backup multiple tables

You can back up multiple table by using multiple -t <table_name>. For example, below code backup two tables 
(e.g. students and classes)

```shell
pg_dump -U user-pengfei -h 10.233.30.220 -p 5432 -t students -t classes school > ./dumps/all_tables.sql
```

### 2.4 Backup all tables in a db
If you don't specify any -t <table_name>, pg_dump will back up the whole db. For example below code will backup all
the tables inside the db school

```shell
pg_dump -U user-pengfei -h 10.233.30.220 -p 5432  -W -d school  > ./dumps/db_backup.sql 
```

### 2.5 Test entire db backup 

To test the db backup, we will drop the db this time
```postgresql
drop database school;

```
To restore it, we need to create an empty db first, then apply the backup on the empty db

Step 1. Create db
```postgresql
create database school;
```
Step 2. Apply backup
```shell
psql -U user-pengfei -h 10.233.30.220 -p 5432 -W -d school -f ./dumps/db_backup.sql
```

We have to create database before we apply the backup, that's because in the backup, pg_dump does not put any information
about the database. To avoid this, we can use the -C option 

