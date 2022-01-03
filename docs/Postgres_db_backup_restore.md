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
about the database. To avoid this, we can use the -C (--create) option when creating the backup. Below code is an example

```shell
pg_dump -U user-pengfei -h 10.233.30.220 -p 5432  -W -C -d school  > ./dumps/db_backup_creation.sql 
```

## 3. Backup all database with pg_dumpall

In section 2, we have backed up a single table, multiple tables, and a single database. But it may not enough. 
For example, the user account and their privilege are not backed up. 

As a result, to back up the entire PostgreSQL cluster (e.g. user account, etc.), we need to use **pg_dumpall**.

The main differences between pg_dump and pg_dumpall is the **user privilege**.
1. You will most likely have to connect to the DB server as a database superuser in order to produce a complete dump. 
That's because pg_dumpall reads tables from all databases. 
2. You will also need superuser privileges to execute the saved script (backup dump) in order to be allowed to add 
users and groups and to create databases.

Below command is an example, that will back up the entire PostgreSQL cluster and save it in the entire_cluster.sql file:
```shell
pg_dumpall -U user-pengfei -h 10.233.30.220 -p 5432 -W -f ./dumps/entire_cluster.sql
```

The prompt console will ask you your password. You will have to enter it multiple times. Because pg_dumpall needs to
reconnect to the database server multiple times to complete the dump of all tables.

To avoid this, you can configure the connection credential at "~/.pgpass" file. The credential must have the following
format.
```text
# general format
hostname:port:database:username:password

# for example
10.233.30.220:5432:school:user-pengfei:changeMe
```

> Note
> You can have multiple credentials in the .pgpass. When a command of psql client (e.g. psql, pgdump, etc), the 
> password of first match on host:port:db:username will be used.

For the .pgpass to work, you need to satisfait the following points:
1. .pgpass must have 0600 as ACL
2. Your psql command can't have option -W (Force psql to prompt for a password before connecting to a database)
3. Your psql command must have -U username -h hostname dbname to allow .pgpass to find the possible matching

## 4. Using shell script to make backup easier

### 4.1 Backup one database
Suppose we name the following script as "pg_bkp.sh", and you have .pgpass setup correctly. Otherwise, you may want to
adapt below script by adding port and password

```shell
#!/bin/bash
# pg_bkp.sh
# This script performs a pg_dump, saving the file the specified dir.
# The first arg ($1) is the database user to connect with.
# The second arg ($2) is the host name of the database
# The third arg ($3) is the database name to backup and is included in the file name
# The fourth arg ($4) is the path of where to put the backup
# $(date +"%Y_%m_%d") includes the current system date into the actual file name.

# Notice the -C option in the command so that we can restore if the database happens to be non-existent, without 
# the need to manually create it beforehand. 
pg_dump -U "$1" -h "$2" -C -d "$3" > "$4"/$(date +"%Y_%m_%d")_"$3".sql

# example to run this script
# sh pg_bkp.sh user-pengfei 10.233.30.220 north_wind /home/coder/work/dumps
```

If we run the script with the following parameters, it will create a backup of database school by using
```shell
sh pg_bkp.sh user-pengfei localhost school /tmp
```

### 4.2 Backup the entire postgres cluster

Suppose we name the following script as "pg_cluster_bkp.sh", and you have .pgpass setup correctly. Otherwise, you may want to
adapt below script by adding port and password. 

Note the user should have admin privilege on the postgresql cluster. If you have no clue, we recommend you to 
use **postgres** (the default admin user). 

```shell
#!/bin/bash
# pg_cluster_bkp.sh
# This shell script calls pg_dumpall and pipes into the gzip utility, then directs to
# a directory for storage.
# $(date +"%Y_%m_%d") incorporates the current system date into the file name.
# The first arg ($1) is the database user to connect with.
# The second arg ($2) is the host name of the database
# The third arg ($3) is the path of where to put the backup
  
pg_dumpall -U "$1" -h "$2" | gzip > "$3"/$(date +"%Y_%m_%d")_pg_bck.gz
```