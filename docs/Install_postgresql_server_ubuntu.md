# Install and setup postgresql server on ubuntu

## 1. Install postgresql

```shell

# refresh your server’s local package index:
sudo apt update
 
# Then, install the Postgres package along with a -contrib package that adds some additional utilities and functionality:
sudo apt install postgresql postgresql-contrib

# start the postgresql server
sudo systemctl status postgresql

# enable postgresql at startup
sudo systemctl enable postgresql

```

## 2. Setup postgresql

### 2.1 allow remote access

The main config file of postgresql is located "/etc/postgresql/12/main"

To allow remote access, open the below config file

```shell
sudo vim /etc/postgresql/12/main/postgresql.conf

# find the below line
listen_addresses = 'local'

# by default it only allows connection from local server
# change local to *. So it must looks like
listen_addresses = '*'
```

### 2.2 Allow user remote access with password

To change the user remote access mode, open the below config file

```shell
sudo vim /etc/postgresql/12/main/pg_hba.conf

# add the below line, 
# host means the connection type is remote, 
# first "all" means all the database name
# second "all" means all the user name
# 0.0.0.0/0 means all ip 
# if all the four field match, the authentication uses md5.
host all all 0.0.0.0/0 md5
```


## 3. Create user and database

Below command needs to be run in a psql terminal

```postgresql
-- create db
create database mydb;

-- create user
create user myuser with encrypted password 'mypass';

-- assign privilege to manage a database
grant all privileges on database mydb to myuser;
```

## 4. Grant special privilege

### 4.1 DB creation 
Note by default, user does not have the right to create database. To assign such right, use the following command

```postgresql
-- general format
ALTER USER username CREATEDB;

-- for example
ALTER USER pliu CREATEDB;


```

### 4.2 Superuser


```postgresql
-- Make a user superuser:

ALTER USER myuser WITH SUPERUSER;
```

Remove superuser status:

```postgresql
ALTER USER username WITH NOSUPERUSER;
```

### 4.3 Default privileges

Those statements above only affect the **current existing tables**. As a result, for newly created database, you need
to rerun the above commands. 

To make the privilege apply to newly created tables, you need to use alter default. For example:
```postgresql
ALTER DEFAULT PRIVILEGES
FOR USER username
IN SCHEMA schema_name
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO username;

```
