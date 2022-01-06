import logging
from PostgresDbManager import PostgresDbManager
import os
from S3StorageEngine import S3StorageEngine

log = logging.getLogger(__name__)


class DbRestoreBot:

    def __init__(self,):
        pass

    def list_available_backups(self, storage_path: str):
        backup_list = []
        # if the manager has a remote storage, use remote storage, if not use local storage
        if self.remote_storage:
            try:
                backup_list = self.remote_storage.list_dir(storage_path)
            except Exception as e:
                log.exception(e)
                exit(1)
        else:
            # logger.info('Listing S3 bucket s3://{}/{} content :'.format(aws_bucket_name, aws_bucket_path))
            try:
                backup_list = os.listdir(storage_path)
            except FileNotFoundError:
                log.error(f'Could not found {storage_path} when searching for backups.'
                          f'Check your .config file settings')
                exit(1)
        return backup_list


def main():
    user_name = "user-pengfei"
    user_password = "changeMe"
    host_name = "10.233.30.220"
    db_name = "north_wind"
    output_path = "/tmp"
    p_manager = PostgresDbManager(user_name, user_password, remote_storage=None, host_name=host_name)
    p_manager.backup_db(db_name, output_path, False)

    endpoint = "https://" + os.getenv("AWS_S3_ENDPOINT")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    session_token = os.getenv("AWS_SESSION_TOKEN")

    s3 = S3StorageEngine(endpoint, access_key, secret_key, session_token)

    source_path = "/tmp/2022-01-06_north_wind_pg_bck.sql"
    destination_path = "s3a://pengfei/me"
    # download the backup file and restore
    s3.download_data("s3a://pengfei/me/2022-01-06_north_wind_pg_bck.sql", "/home/coder/work/tmp.sql")


if __name__ == "__main__":
    main()
