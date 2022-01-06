from PostgresDbManager import PostgresDbManager
import os

from S3StorageEngine import S3StorageEngine


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

    s3.upload_data(source_path, destination_path)
    # PostgresDbManager.backup_postgres_db_to_gz(user_name, user_password, db_name, output_path,
    #                                           host_name=host_name)


if __name__ == "__main__":
    main()
