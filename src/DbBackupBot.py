import locale
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
    # input params
    storage = ''
    user_name = "user-pengfei"
    user_password = "changeMe"
    host_name = "10.233.30.220"
    db_name = "north_wind"
    destination_path = "s3a://pengfei/me"

    # temp local path if you use remote storage
    tmp_output_path = "/tmp"
    # Step0: Check storage
    if storage == 's3':
        # step1: build backup
        backup_file_path = make_backup(user_name, user_password, host_name, db_name, tmp_output_path)
        if backup_file_path:
            log.info("Backup complete, start uploading")
            # step 2: upload backup
            # get s3 creds
            endpoint = "https://" + os.getenv("AWS_S3_ENDPOINT")
            access_key = os.getenv("AWS_ACCESS_KEY_ID")
            secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            session_token = os.getenv("AWS_SESSION_TOKEN")
            # build s3 client
            s3 = S3StorageEngine(endpoint, access_key, secret_key, session_token)
            # upload file
            if destination_path.startswith("s3"):
                if s3.upload_data(backup_file_path, destination_path):
                    log.info(f"The backup file has been uploaded to {destination_path}")
            else:
                log.error("The s3 path is not valid. Please enter a valid s3 path. e.g. s3a://bucket_name/bucket_key")
        else:
            log.error("Backup process failed")
    elif storage == locale:
        # step1: build backup
        backup_file_path = make_backup(user_name, user_password, host_name, db_name, destination_path)
        if backup_file_path:
            log.info(f"Backup process complete. The backup file is located at {backup_file_path}")
        else:
            log.error("Backup process failed")


if __name__ == "__main__":
    main()
