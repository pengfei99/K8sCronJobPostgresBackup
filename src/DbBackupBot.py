import logging
from typing import Optional

from PostgresDbManager import PostgresDbManager
import os

from S3StorageEngine import S3StorageEngine

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


def make_backup(user_name, user_password, host_name, db_name, backup_file_parent_folder, port="5432") -> Optional[str]:
    p_manager = PostgresDbManager(user_name, user_password, host_name=host_name, port=port)
    if db_name in p_manager.get_db_list():
        backup_file_path = p_manager.backup_db(db_name, backup_file_parent_folder)
        log.info(f"Creating backup file {backup_file_path}")
        return backup_file_path
    else:
        log.exception(f"The input database {db_name} does not exist in the target server")
        return None


def main():
    storage = ''
    # Step0: Check storage
    if storage == 's3':
        # step1: build backup
        user_name = "user-pengfei"
        user_password = "changeMe"
        host_name = "10.233.30.220"
        db_name = "north_wind"
        tmp_output_path = "/tmp"
        log.info()
        # step 2: upload backup
        endpoint = "https://" + os.getenv("AWS_S3_ENDPOINT")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        session_token = os.getenv("AWS_SESSION_TOKEN")

        s3 = S3StorageEngine(endpoint, access_key, secret_key, session_token)

        source_path = "/tmp/2022-01-06_north_wind_pg_bck.sql"
        destination_path = "s3a://pengfei/me"

        s3.upload_data(source_path, destination_path)
        # PostgresDbManager.backup_postgres_db_to_gz(user_name, user_password, db_name, output_path,
    #                                           host_name=host_name)


if __name__ == "__main__":
    main()
