import gzip
import logging
import os
import subprocess
from datetime import datetime
from StorageEngineInterface import StorageEngineInterface

log = logging.getLogger(__name__)


class PostgresDbManager:
    def __init__(self, user_name: str, user_pwd: str, remote_storage: StorageEngineInterface, host_name: str,
                 port="5432"):
        self.user_name = user_name
        self.user_pwd = user_pwd
        self.host_name = host_name
        self.port = port
        self.remote_storage = remote_storage

    def backup_db(self, db_name, output_path, compress=True):
        """

        :param db_name:
        :param output_path:
        :param compress:
        :return:
        """
        if compress:
            self.backup_postgres_db_to_gz(self.user_name, self.user_pwd, db_name, output_path, self.host_name,
                                          self.port)
        else:
            self.backup_postgres_db_to_sql(self.user_name, self.user_pwd, db_name, output_path, self.host_name,
                                           self.port)

    @staticmethod
    def backup_postgres_db_to_sql(user_name: str, user_pwd: str, db_name: str, output_path: str, host_name="127.0.0.1",
                                  port="5432", verbose=False):
        """
        Backup postgres db to a file.

        :param user_name: username for connecting to the database server
        :param user_pwd: user password for connecting to the database server
        :param db_name: db name that you need to back up
        :param output_path: the path to put the backup dump file
        :param host_name: the host name of the db server
        :param port: the port of the db server
        :param verbose: default value is False, if set to true, it will log the communication message
                        between client and server
        :return: None
        """
        # build the full path of the destination file
        current_date = str(datetime.date(datetime.now()))
        full_path = f"{output_path}/{current_date}_{db_name}_pg_bck.sql"
        if verbose:
            try:
                process = subprocess.Popen(
                    ['pg_dump',
                     '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user_name, user_pwd, host_name, port, db_name),
                     '-C',
                     '-f', full_path,
                     '-v'],
                    stdout=subprocess.PIPE
                )
                output = process.communicate()[0]
                if int(process.returncode) != 0:
                    log.info('Command failed. Return code : {}'.format(process.returncode))
                    exit(1)
                return output
            except Exception as e:
                log.exception(e)
                exit(1)
        else:
            try:
                process = subprocess.Popen(
                    ['pg_dump',
                     '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user_name, user_pwd, host_name, port, db_name),
                     '-f', full_path],
                    stdout=subprocess.PIPE
                )
                output = process.communicate()[0]
                if process.returncode != 0:
                    log.info('Command failed. Return code : {}'.format(process.returncode))
                    exit(1)
                return output
            except Exception as e:
                log.exception(e)
                exit(1)

    @staticmethod
    def backup_postgres_db_to_gz(user_name: str, user_pwd: str, db_name: str, output_path: str, host_name="127.0.0.1",
                                 port="5432"):
        """
        Backup postgres db to a compressed file in format gz.

        :param user_name: username for connecting to the database server
        :param user_pwd: user password for connecting to the database server
        :param db_name: db name that you need to back up
        :param output_path: the path to put the backup dump file
        :param host_name: the host name of the db server
        :param port: the port of the db server

        :return: None
        """
        # cmd = f"pg_dump --dbname=postgresql://{user_name}:{user_pwd}@{host_name}:{port}/{db_name} -v"
        # print(cmd)
        current_date = str(datetime.date(datetime.now()))
        full_path = f"{output_path}/{current_date}_{db_name}_pg_bck.sql.gz"
        with gzip.open(full_path, 'wb') as f:
            # use subprocess to run the pg_dump command
            try:
                process = subprocess.Popen(['pg_dump',
                                            '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user_name, user_pwd,
                                                                                          host_name,
                                                                                          port, db_name),
                                            '-v'],
                                           stdout=subprocess.PIPE, universal_newlines=True)
                # get the output of the subprocess, write output to the gz file line by line in streaming mode
                # this way we don't need very large memory when backup big databases
                for stdout_line in iter(process.stdout.readline, ""):
                    f.write(stdout_line.encode('utf-8'))
                process.stdout.close()
                process.wait()
                output = process.communicate()[0]
                if process.returncode != 0:
                    log.info('Command failed. Return code : {}'.format(process.returncode))
                    exit(1)
                return output
            except Exception as e:
                log.exception(e)
                exit(1)

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
    p_manager = PostgresDbManager(user_name, user_password, None, host_name=host_name)
    p_manager.backup_db(db_name, output_path, False)
    # PostgresDbManager.backup_postgres_db_to_gz(user_name, user_password, db_name, output_path,
    #                                           host_name=host_name)

    pass


if __name__ == "__main__":
    main()
