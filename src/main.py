import argparse
import datetime
import logging
import os

from src.DbBackupBot import DbBackupBot
from src.DbRestoreBot import DbRestoreBot
from src.db.PostgresDbManager import PostgresDbManager
from src.storage.S3StorageEngine import S3StorageEngine


def main():
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    args_parser = argparse.ArgumentParser(description='Postgres database management')
    # when required is set to True, you must provide this parameter when calling this function
    # choices=[] will check the input with items in the list. If no match, error will be raised
    args_parser.add_argument("--action",
                             metavar="action",
                             choices=['list_backups', 'list_dbs', 'auto_restore', 'auto_backup'],
                             required=True)
    args_parser.add_argument("--backup_dir",
                             metavar="backup_parent_dir",
                             default=None,
                             help="Parent dir for storing backup files (show with --action list_backups)")
    args_parser.add_argument("--db_login",
                             metavar="db_login",
                             default=None,
                             help="User login for connecting database (show with --action list_dbs)")
    args_parser.add_argument("--db_pwd",
                             metavar="db_pwd",
                             default=None,
                             help="User login for connecting database (show with --action list_dbs)")
    args_parser.add_argument("--db_host",
                             metavar="db_host",
                             default=None,
                             help="database host name (show with --action list_dbs)")
    args_parser.add_argument("--db_port",
                             metavar="db_port",
                             default="5432",
                             help="database host name (show with --action list_dbs)")
    args_parser.add_argument("--target_db",
                             metavar="db_name",
                             default=None,
                             help="Name of the database that need to be restored or backup")
    # args_parser.add_argument("--verbose",
    #                          default=False,
    #                          help="Verbose output")

    args = args_parser.parse_args()

    # setup params
    user_name = args.db_login
    user_password = args.db_pwd
    host_name = args.db_host
    port = args.db_port
    db_name = args.target_db
    backup_storage_path = args.backup_dir
    endpoint = "https://" + os.getenv("AWS_S3_ENDPOINT")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    session_token = os.getenv("AWS_SESSION_TOKEN")

    # list task
    if args.action == "list_backups":
        # build s3 client
        s3 = S3StorageEngine(endpoint, access_key, secret_key, session_token)
        if backup_storage_path:
            backup_files = s3.list_dir(backup_storage_path)
            log.info(f"Find following backup: {backup_files}")

    # list databases task
    elif args.action == "list_dbs":
        if user_name and user_password and host_name:
            db_manager = PostgresDbManager(user_name, user_password, host_name=host_name, port=port)
            dbs = db_manager.get_db_list()
            log.info(f"Find belows databases: {dbs}")
        else:
            log.error(f"Missing argument. Unable to connect to the database "
                      f"With the given argument {user_name}, {user_password}, {host_name}, {port}")

    # auto_backup task
    elif args.action == "auto_backup":
        # build s3 client
        s3 = S3StorageEngine(endpoint, access_key, secret_key, session_token)
        if user_name and user_password and host_name:
            db_manager = PostgresDbManager(user_name, user_password, host_name=host_name, port=port)
            # create an instance of DbBackupBot
            backup_bot = DbBackupBot(s3, db_manager)
            # do the auto backup
            backup_bot.make_auto_backup(db_name, backup_storage_path)
            log.info("Backup complete")
        else:
            log.error(f"Missing argument. Unable to connect to the database "
                      f"With the given argument {user_name}, {user_password}, {host_name}, {port}")

    # auto_restore task
    elif args.action == "auto_restore":
        s3 = S3StorageEngine(endpoint, access_key, secret_key, session_token)
        if user_name and user_password and host_name:
            db_manager = PostgresDbManager(user_name, user_password, host_name=host_name, port=port)
            # create an instance of DbRestoreBot
            restore_bot = DbRestoreBot(s3, db_manager)
            # do the auto restore
            restore_bot.restore_db_with_latest_backup(db_name, backup_storage_path)
            log.info("Restore complete")
        else:
            log.error(f"Missing argument. Unable to connect to the database "
                      f"With the given argument {user_name}, {user_password}, {host_name}, {port}")


if __name__ == '__main__':
    main()
