import logging
import os.path
import datetime
import re

from src.db.DbManagerInterface import DbManagerInterface
from src.db.PostgresDbManager import PostgresDbManager
from src.storage.StorageEngineInterface import StorageEngineInterface
from src.storage.LocalStorageEngine import LocalStorageEngine

log = logging.getLogger(__name__)


class DbRestoreBot:

    def __init__(self, storage_engine: StorageEngineInterface, db_manager: DbManagerInterface):
        self.db_manager = db_manager
        self.storage_engine = storage_engine

    def list_available_backups(self, storage_path: str):
        return self.storage_engine.list_dir(storage_path)

    @staticmethod
    def is_backup_of_db(file_name, db_name):
        return db_name in file_name

    def get_latest_backup_name(self, storage_path: str, db_name: str) -> str:
        """
        This function search the latest backup

        :param db_name:
        :param storage_path:
        :return:
        """
        all_backups = self.list_available_backups(storage_path)
        backup_list = [f for f in all_backups if self.is_backup_of_db(f, db_name)]
        current_date = datetime.datetime.now()
        latest_backup_path = ""
        min_time = datetime.timedelta(days=30)
        for file_name in backup_list:
            time_stamp = datetime.datetime.strptime(file_name.split("_")[0], '%Y-%M-%d')
            # arithmetic operations on datetime will return a timedelta type
            if min_time > current_date - time_stamp:
                min_time = current_date - time_stamp
                latest_backup_path = os.path.join(storage_path, file_name)
        return latest_backup_path

    def restore_latest_db_backup(self, db_name: str, backup_file_path: str):
        # in our case, we name the postgres custom format with extension .pgdump; the plain text sql format with .sql
        if backup_file_path.endswith(".pgdump"):
            return self.db_manager.restore_db(db_name, backup_file_path, backup_format="psql")
        elif backup_file_path.endswith(".sql"):
            return self.db_manager.restore_db(db_name, backup_file_path, backup_format="sql")


def main():
    # create an instance of local storage
    local = LocalStorageEngine()
    user_name = "user-pengfei"
    user_password = "changeMe"
    host_name = "10.233.30.220"

    # create an instance of postgresDbManager
    p_manager = PostgresDbManager(user_name, user_password, host_name=host_name, port="5432")

    # create an instance of DbRestoreBot
    restore_bot = DbRestoreBot(local, p_manager)

    # get latest backup
    storage_path = "/tmp/sql_bkp"
    db_name = "north_wind"
    latest_backup = restore_bot.get_latest_backup_name(storage_path, db_name)
    print(latest_backup)

    # start restore process
    # step1 download data
    local_path = f"/tmp/latest_{db_name}_backup.sql"
    if local.download_data(latest_backup, local_path):
        # step2: restore
        restore_bot.restore_latest_db_backup()
    else:
        log.error("Fail to download the backup file")


if __name__ == "__main__":
    main()
