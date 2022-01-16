import argparse
import logging
import os

from dbsavior.db.PostgresDbManager import PostgresDbManager
from dbsavior.storage.S3StorageEngine import S3StorageEngine
from dbsavior.storage.LocalStorageEngine import LocalStorageEngine
from dbsavior.DbBackupRestoreBot import DbBackupRestoreBot


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
    # metavar is the surname of the variable next to the option, for explanation purpose
    # help defines the comments which will be printed after option --help
    args_parser.add_argument("--db_type",
                             metavar="db_type",
                             choices=['postgres', 'mysql', 'oracle'],
                             required=True,
                             help="The database type that you want to connect to. Possible values: "
                                  "'postgres', 'mysql', 'oracle'"
                             )
    args_parser.add_argument("--storage_type",
                             metavar="storage_type",
                             choices=['local', 's3', 'hdfs'],
                             required=True,
                             help="The storage type that you want to connect to. Possible values: "
                                  "'local', 's3', 'hdfs'"
                             )
    args_parser.add_argument("--action",
                             metavar="action",
                             choices=['list_backups', 'list_dbs', 'auto_restore', 'auto_backup', 'populate'],
                             required=True,
                             help="The action that CLI provides. Possible values: "
                                  "'list_backups', 'list_dbs', 'auto_restore', 'auto_backup', 'populate'"
                             )
    args_parser.add_argument("--backup_dir",
                             metavar="backup_parent_dir",
                             default=None,
                             help="Parent dir for storing backup files (show with --action list_backups)")
    args_parser.add_argument("--backup_file",
                             metavar="full_file_path",
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

    args = args_parser.parse_args()
    db_manager = None
    storage_engine = None
    # build db_manager with the input db type and params
    if args.db_type == "postgres":
        user_name = args.db_login
        user_password = args.db_pwd
        host_name = args.db_host
        port = args.db_port
        db_manager = PostgresDbManager(user_name, user_password, host_name=host_name, port=port)
    else:
        log.error(
            f"We don't support the server type {args.db_type} for now, please enter a database type that we support")
        exit(1)

    # build storage engine with the input storage type and params
    if args.storage_type == "local":
        storage_engine = LocalStorageEngine()
    elif args.storage_type == "s3":
        endpoint = "https://" + os.getenv("AWS_S3_ENDPOINT")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        session_token = os.getenv("AWS_SESSION_TOKEN")
        storage_engine = S3StorageEngine(endpoint, access_key, secret_key, session_token)
    else:
        log.error(f"We don't support the storage type {args.storage_type} for now, please enter a "
                  f"storage type that we support")
        exit(1)

    # setup db backup restore params
    db_name = args.target_db
    backup_storage_path = args.backup_dir

    # for populate a database, you need to use option --backup_file to give a full file name of the sql dump
    backup_file_name = args.backup_file

    # list task
    if args.action == "list_backups":
        if backup_storage_path:
            backup_files = storage_engine.list_dir(backup_storage_path)
            log.info(f"Find following backup: {backup_files}")
        else:
            log.error("Missing argument backup dir")
            exit(1)

    # list databases task
    elif args.action == "list_dbs":
        if db_manager:
            dbs = db_manager.get_db_list()
            log.info(f"Find below databases: {dbs}")
        else:
            log.error(f"Missing argument. Unable to connect to the database")
            exit(1)

    # auto_backup task
    elif args.action == "auto_backup":
        if db_manager and storage_engine and backup_storage_path:
            # create an instance of DbBackupBot
            backup_bot = DbBackupRestoreBot(storage_engine, db_manager)
            # do the auto backup
            if backup_bot.make_auto_backup(db_name, backup_storage_path):
                log.info("Backup complete")
            else:
                log.error("Backup failed")
                exit(1)
        else:
            log.error(f"Missing argument. Unable to backup the database ")
            exit(1)

    # auto_restore task
    elif args.action == "auto_restore":
        if db_manager and storage_engine and backup_storage_path:
            # create an instance of DbBackupRestoreBot
            restore_bot = DbBackupRestoreBot(storage_engine, db_manager)
            # do the auto restore
            if restore_bot.restore_db_with_latest_backup(db_name, backup_storage_path):
                log.info("Restore complete")
            else:
                log.error("Restore failed")
                exit(1)
        else:
            log.error(f"Missing argument. Unable to restore the database")
            exit(1)

    # populate task
    elif args.action == "populate":
        if db_manager and storage_engine and db_name and backup_file_name:
            # create an instance of DbBackupRestoreBot
            restore_bot = DbBackupRestoreBot(storage_engine, db_manager)
            # do the auto restore
            if restore_bot.populate_db_with_sql_dump(db_name, backup_file_name):
                log.info("Populate database complete")
            else:
                log.error("Populate database failed")
                exit(1)
        else:
            log.error(f"Missing argument. Unable to connect to the database")
            exit(1)


if __name__ == '__main__':
    main()
