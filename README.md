# DataBaseBackupRestoreOnK8s

## Project Introduction
If you have data that you want to import or export from a database that you deployed in a k8s cluster, you need to 
install a database client, create a dump file, then upload the dump file somewhere else. 

This project will help you to avoid all that. The only thing you need to do is to provide the name of the database and
where you want to upload/download the backup file. 

## Features

* Create database backup file
* Upload backup file to remote storage
* Download backup file from remote storage
* Restore/Populate database
* Provide k8s cron job to create backup with configurable time interval 
* If you use auto backup/restore feature in the cronjob/job, the restore job will always find the latest backup of the
  target database to do restore.
* List available database that can be backed up.
* List available backup that can be used to restore

## Usage

There are different ways to use this project. 
1. Use this project as a python package
2. Use this project as a python Command Line Interface
3. Use this project as a k8s cronjob/job

### Use this project as a python package

```shell
# install this project as a pypi package
pip install dbsavior
```

```python3
import os
from dbsavior.db.PostgresDbManager import PostgresDbManager
from dbsavior.storage.S3StorageEngine import S3StorageEngine
from dbsavior.storage.LocalStorageEngine import LocalStorageEngine
from dbsavior.DbBackupRestoreBot import DbBackupRestoreBot


def main():
    # params to be configured in the job or cron job
    user_name:str = "user-pengfei"
    user_password:str = "changeMe"
    host_name:str = "postgresql-124499"
    port:str = "5432"
    db_name:str = "test"
    backup_storage_path:str = "s3://pengfei/tmp/sql_backup"

    # create an instance of postgresDbManager
    p_manager = PostgresDbManager(user_name, user_password, host_name=host_name, port=port)

    # temp local path if you use remote storage
    # get s3 creds
    endpoint = "https://" + os.getenv("AWS_S3_ENDPOINT")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    session_token = os.getenv("AWS_SESSION_TOKEN")
    # build s3 client
    s3 = S3StorageEngine(endpoint, access_key, secret_key, session_token)

    # create an instance of DbBackupBot
    backup_restore_bot = DbBackupRestoreBot(s3, p_manager)
    
    # do an auto backup
    backup_restore_bot.make_auto_backup(db_name,backup_storage_path)
    
    # restore the database by using the latest backup
    backup_restore_bot.restore_db_with_latest_backup(db_name, backup_storage_path)


if __name__ == "__main__":
    main()
```

### Use this project as a python Command Line Interface

Note, if you use remote storage such as s3 (or minio), you need to set up your s3 creds correctly in your env variables.


```shell
git clone https://github.com/pengfei99/K8sCronJobPostgresBackup.git

cd K8sCronJobPostgresBackup

# show the command line options and comments
python dbsavior/main.py -h

# list existing backup
python dbsavior/main.py --db_type postgres --storage_type s3 --action list_backups --backup_dir s3://path/to/sql_backup

# list existing database
python dbsavior/main.py --db_type postgres --storage_type s3 --action list_dbs --db_login user-pengfei --db_pwd changeMe --db_host 127.0.0.1 --db_port 5432

# auto backup
python dbsavior/main.py --db_type postgres --storage_type s3 --action auto_backup --db_login user-pengfei --db_pwd changeMe --db_host 127.0.0.1 --backup_dir s3://path/to/sql_backup --target_db test
 
# auto restore 
python dbsavior/main.py --db_type postgres --storage_type s3 --action auto_restore --db_login user-pengfei --db_pwd changeMe --db_host 127.0.0.1 --backup_dir s3://path/to/sql_backup --target_db test 

# populate a database with a sql dump
python dbsavior/main.py --db_type postgres --storage_type s3 --action populate --db_login user-pengfei --db_pwd changeMe --db_host 127.0.0.1 --backup_file s3://path/to/sql_backup/2022-01-12_test_pg_bck.sql --target_db test

```


### Use this project as a k8s cronjob/job

For the job and cronjob is set up for s3 and postgresql. You need to add your s3 and postgresql server credentials
into the yaml file to run the job and cronjob correctly.

```shell
git clone https://github.com/pengfei99/K8sCronJobPostgresBackup.git

cd K8sCronJobPostgresBackup/k8s

# this job calls auto backup on a database once
kubectl apply -f job_backup.yaml

# this cronjob calls auto backup on a database based on the cron. The default cron starts at mid night every day  
kubectl apply -f cronjob_backup.yaml

# this job calls auto restore of a database, if it finds many available backups, it will apply the latest one
kubeclt apply -f job_restore.yaml

# this job populate a database with a specific backup file.
kubectl apply -f job_populate.yaml

```

## Future works

For now, this project only implements the postgres server for the **DbManagerInterface**. For the 
**StorageEngineInterface**, we only implement the s3 and local filesystem(tested for linux). If you want to back up a
database in a mysql server and store the backup on HDFS, you only need to implement the **DbManagerInterface** and 
**StorageEngineInterface**. The rest of the project can be reused automatically.

## Other docs that may be useful for you
If you are not familiar with postgresql backup and restore procedure. Please visit
this [doc](docs/Postgres_db_backup_restore.md).


