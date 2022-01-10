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
