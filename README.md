# K8sCronJobPostgresBackup

In this project, we will discuss how to back up and restore a database of a postgresql server in a k8s cluster.

If you are not familiar with postgresql backup and restore procedure. Please visit this [doc](docs/Postgres_db_backup_restore.md).

If you are familiar with postgresql backup and restore, then we can continue our journey:
Part 1: Back up 
1. Create the backup files by using python
2. Copy the backup file to S3 by using python
3. Build a docker image that host the above code and able to run it
4. Build a k8s cronJob that uses the above docker img to back up a database periodically. 

Part 2: Restore
1. 

