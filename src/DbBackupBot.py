import locale
import logging
from typing import Optional

from src.db.DbManagerInterface import DbManagerInterface
from src.db.PostgresDbManager import PostgresDbManager
import os

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

    def make_backup(self, db_name: str, backup_file_parent_dir: str, tmp_dir='/tmp') -> Optional[str]:
        # step 1: check if the target db exist
        if self.db_manager.has_db(db_name):
            # step 2: check the storage engine type, if remote(s3), need to add an upload step
            storage_engine_type = self.storage_engine.get_storage_engine_type()
            # s3 case
            if storage_engine_type == 's3':
                tmp_file_path = self.db_manager.backup_db(db_name, tmp_dir)
                if self.storage_engine.upload_data(tmp_file_path, backup_file_parent_dir):
                    backup_file_path = f"{backup_file_parent_dir}/{os.path.basename(tmp_file_path)}"
                else:
                    log.error(f"Unable to upload backup file {tmp_file_path} to s3 {backup_file_parent_dir} ")
                    backup_file_path = None
            # local case
            elif storage_engine_type == 'local':
                backup_file_path = self.db_manager.backup_db(db_name, backup_file_parent_dir)
            log.info(f"Backup complete. Creat backup file {backup_file_path} for db {db_name}")
            return backup_file_path
        else:
            log.exception(f"The input database {db_name} does not exist in the target server")
            return None


def main():
    # create an instance of local storage
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
