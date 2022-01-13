# K8sCronJobPostgresBackup

In this project, we will discuss how to back up and restore a database of a postgresql server in a k8s cluster.

If you are not familiar with postgresql backup and restore procedure. Please visit
this [doc](docs/Postgres_db_backup_restore.md).

If you are familiar with postgresql backup and restore, then we can continue our journey:
Part 1: Back up

1. Create the backup files by using python
2. Copy the backup file to S3 by using python
3. Build a docker image that host the above code and able to run it
4. Build a k8s cronJob that uses the above docker img to back up a database periodically.

Part 2: Restore

1. Get available backups
2. Choose and Download preferred backups
3. Restore the database

# Code Examples

## DbManager

### PostgresDbManager

```python
user_name = "user-pengfei"
user_password = "changeMe"
host_name = "10.233.30.220"
db_name = "north_wind"
output_path = "/tmp"

# create an instance
p_manager = PostgresDbManager(user_name, user_password, host_name=host_name, port="5432")
# call the backup method
p_manager.backup_db(db_name, output_path, False)

# It also has static method, you can do backup without creating an instance of the PostgresDbManager 
# create db
PostgresDbManager.create_db(user_name, user_password, 'test', host_name)
# rename db
PostgresDbManager.rename_db(user_name, user_password, "test", "toto", host_name)

PostgresDbManager.restore_db_with_sql_format(user_name, user_password, "test",
                                             "/home/coder/work/dumps/db_backup.sql", host_name)

# pg_dump --dbname=postgresql://user-pengfei:gv8eba5xmsw4kt2uk1mn@10.233.30.220:5432/north_wind -f /tmp/dump.sql -Fc -v
# pg_restore --no-owner --dbname=postgresql://user-pengfei:gv8eba5xmsw4kt2uk1mn@10.233.30.220:5432/north_wind /tmp/dump.sql

# psql --dbname=postgresql://pliu:pliu@127.0.0.1:5432/test -f /home/pliu/git/LearningSQL/SQL_practice_problems/data_base/northwind_ddl.sql
```

## Storage Engine

### S3 storage engine

```python
endpoint = "https://" + os.getenv("AWS_S3_ENDPOINT")
access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
session_token = os.getenv("AWS_SESSION_TOKEN")

s3 = S3StorageEngine(endpoint, access_key, secret_key, session_token)
source_path = "/tmp/2022-01-06_north_wind_pg_bck.sql"
destination_path = "s3a://pengfei/me"

# upload the backup file to s3
s3.upload_data("/home/coder/work/tmp.sql", "s3a://pengfei/me/2022-01-06_north_wind_pg_bck.sql")

# download the backup file and restore
s3.download_data("s3a://pengfei/me/2022-01-06_north_wind_pg_bck.sql", "/home/coder/work/tmp1.sql")



```

## DbBackupBot

Code example of using DbBackupBot to back up a database and save the backup on s3StorageEngine

```python
def main():
    # params to be configured in the job or cron job
    user_name = "user-pengfei"
    user_password = "changeMe"
    host_name = "postgresql-124499"
    port = "5432"
    db_name = "test"
    backup_storage_path = "s3://pengfei/tmp/sql_backup"

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
    backup_bot = DbBackupBot(s3, p_manager)

    backup_bot.make_auto_backup(db_name,backup_storage_path)


if __name__ == "__main__":
    main()
```

Code example of using DbBackupBot to back up a database and save the backup on LocalStorageEngine
```python
local = LocalStorageEngine()
    user_name = "pliu"
    user_password = "pliu"
    host_name = "127.0.0.1"
    port="5432"

    # create an instance of postgresDbManager
    p_manager = PostgresDbManager(user_name, user_password, host_name=host_name, port=port)

    # create an instance of DbBackupBot
    backup_bot = DbBackupBot(local, p_manager)

    backup_bot.make_backup("test","/tmp/sql_backup")
```

## DbRestoreBot
Code example of using DbRestoreBot to download backup from s3StorageEngine and restore the database
```python
def main():
    # create an instance of local storage
    user_name = "user-pengfei"
    user_password = "changeMe"
    host_name = "postgresql-124499"
    port="5432"
    db_name = "test"
    backup_storage_path = "s3://pengfei/tmp/sql_backup"


    # create an instance of postgresDbManager
    p_manager = PostgresDbManager(user_name, user_password, host_name=host_name, port=port)
    

    endpoint = "https://" + os.getenv("AWS_S3_ENDPOINT")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    session_token = os.getenv("AWS_SESSION_TOKEN")
    # build s3 client
    s3 = S3StorageEngine(endpoint, access_key, secret_key, session_token)

    # create an instance of DbRestoreBot
    restore_bot = DbRestoreBot(s3, p_manager)

    restore_bot.restore_db_with_latest_backup(db_name,backup_storage_path)

    # restore a specific backup
    # backup_file1 = "/home/pliu/git/LearningSQL/SQL_practice_problems/data_base/northwind_ddl.sql"
    # backup_file2 = "/home/pliu/git/LearningSQL/SQL_practice_problems/data_base/northwind_data.sql"
    # restore_bot.restore_db_backup("test", backup_file1)
    # restore_bot.restore_db_backup("test", backup_file2)
```

Code example of using DbRestoreBot to restore the database from localStorageEngine

```python
# create an instance of local storage
    local = LocalStorageEngine()
    user_name = "pliu"
    user_password = "pliu"
    host_name = "127.0.0.1"

    # create an instance of postgresDbManager
    p_manager = PostgresDbManager(user_name, user_password, host_name=host_name, port="5432")

    # create an instance of DbRestoreBot
    restore_bot = DbRestoreBot(local, p_manager)

    # restore latest backup
    storage_path = "/tmp/sql_backup"
    db_name = "test"
    restore_bot.restore_db_with_latest_backup(db_name, storage_path)
```

### main

```shell
# list existing backup
python src/main.py --action list_backups --backup_dir s3://pengfei/tmp/sql_backup

# list existing database
python src/main.py --action list_dbs --db_login user-pengfei --db_pwd changeMe --db_host postgresql-124499 --db_port 5432

# auto backup
 python src/main.py --action auto_backup --db_login user-pengfei --db_pwd changeMe --db_host postgresql-124499 --backup_dir s3://pengfei/tmp/sql_backup --target_db test
 
# auto restore
python src/main.py --action auto_restore --db_login user-pengfei --db_pwd changeMe --db_host postgresql-124499 --backup_dir s3://pengfei/tmp/sql_backup --target_db test 
```