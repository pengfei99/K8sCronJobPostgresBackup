from datetime import datetime
import logging
from typing import Optional

from src.db.DbManagerInterface import DbManagerInterface
from src.db.PostgresDbManager import PostgresDbManager
from util import get_date_format

from src.storage.LocalStorageEngine import LocalStorageEngine
from src.storage.S3StorageEngine import S3StorageEngine
from src.storage.StorageEngineInterface import StorageEngineInterface

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


class DbBackupBot:
    def __init__(self, storage_engine: StorageEngineInterface, db_manager: DbManagerInterface):
        self.storage_engine = storage_engine
        self.db_manager = db_manager

    def make_auto_backup(self, db_name: str, backup_file_parent_dir: str, tmp_dir='/tmp') -> Optional[str]:
        current_date = datetime.now().strftime(get_date_format())
        backup_file_name = f"{current_date}_{db_name}_pg_bck.sql"
        return self.make_backup_with_custom_file_name(db_name, backup_file_parent_dir, backup_file_name, tmp_dir)

    def make_backup_with_custom_file_name(self, db_name: str, backup_file_parent_dir: str, backup_file_name: str,
                                          tmp_dir='/tmp') -> Optional[str]:
        # step 1: check if the target db exist
        if self.db_manager.has_db(db_name):
            # if db exist, start step 2: build the backup file
            tmp_bk_file_path = self.db_manager.backup_db(db_name, tmp_dir, backup_file_name)
            if tmp_bk_file_path:
                # if backup success, start step 3: upload backup file
                destination_path = f"{backup_file_parent_dir}/{backup_file_name}"
                if self.storage_engine.upload_data(tmp_bk_file_path, destination_path):
                    log.info(f"Backup complete. Creat backup file {destination_path} for db {db_name}")
                    return destination_path
                else:
                    log.error(f"Unable to upload backup file {tmp_bk_file_path} to {backup_file_parent_dir}")
                    return None
            else:
                log.error(f"Unable to create backup for database {db_name}")
                return None
        else:
            log.exception(f"The input database {db_name} does not exist in the target server")
            return None


def main():
    # create an instance of local storage
    local = LocalStorageEngine()
    user_name = "pliu"
    user_password = "pliu"
    host_name = "127.0.0.1"
    port = "5432"

    # create an instance of postgresDbManager
    p_manager = PostgresDbManager(user_name, user_password, host_name=host_name, port=port)

    # create an instance of DbBackupBot
    backup_bot = DbBackupBot(local, p_manager)

    backup_bot.make_backup("test", "/tmp/sql_backup")

    # temp local path if you use remote storage
    # get s3 creds
    # endpoint = "https://" + os.getenv("AWS_S3_ENDPOINT")
    # access_key = os.getenv("AWS_ACCESS_KEY_ID")
    # secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    # session_token = os.getenv("AWS_SESSION_TOKEN")
    # build s3 client
    # s3 = S3StorageEngine(endpoint, access_key, secret_key, session_token)


if __name__ == "__main__":
    main()
