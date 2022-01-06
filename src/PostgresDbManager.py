import gzip
import logging
import psycopg2
import subprocess
from datetime import datetime

from psycopg2 import DatabaseError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

log = logging.getLogger(__name__)


class PostgresDbManager:
    def __init__(self, user_name: str, user_pwd: str, host_name: str, port="5432"):
        self.user_name = user_name
        self.user_pwd = user_pwd
        self.host_name = host_name
        self.port = port

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
                     '--create',
                     '-f', full_path,
                     '-v'],
                    stdout=subprocess.PIPE
                )
                output = process.communicate()[0]
                if int(process.returncode) != 0:
                    log.info('Command failed. Return code : {}'.format(process.returncode))
                    raise
                return output
            except Exception as e:
                log.exception(e)
                raise
        else:
            try:
                process = subprocess.Popen(
                    ['pg_dump',
                     '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user_name, user_pwd, host_name, port, db_name),
                     '--create',
                     '-f', full_path],
                    stdout=subprocess.PIPE
                )
                output = process.communicate()[0]
                if process.returncode != 0:
                    log.info('Command failed. Return code : {}'.format(process.returncode))
                    raise
                return output
            except Exception as e:
                log.exception(e)
                raise

    @staticmethod
    def restore_postgres_db(user_name: str, user_pwd: str, db_name: str, backup_file_path: str, host_name="127.0.0.1",
                            port="5432", verbose=False):
        """Restore postgres db from a file."""
        try:
            subprocess_params = [
                'pg_restore',
                '--no-owner',
                '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user_name,
                                                              user_pwd,
                                                              host_name,
                                                              port,
                                                              db_name)
            ]

            if verbose:
                subprocess_params.append('-v')

            subprocess_params.append(backup_file_path)
            process = subprocess.Popen(subprocess_params, stdout=subprocess.PIPE)

            if int(process.returncode) != 0:
                log.error('Command failed. Return code : {}'.format(process.returncode))
                return False

            return True
        except Exception as e:
            log.error("Issue with the db restore : {}".format(e))
            return False

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
                    raise
                return output
            except Exception as e:
                log.exception(e)
                raise

    @staticmethod
    def list_existing_databases(user_name: str, user_pwd: str, host_name="127.0.0.1", port="5432"):
        con = None
        db_list = []
        try:
            # connect to the default db of postgresql server (postgres) 
            con = psycopg2.connect(dbname='postgres', port=port, user=user_name, host=host_name, password=user_pwd)
        except Exception as e:
            log.error(e)
            raise

        if con:
            con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            con.autocommit = True
            cur = con.cursor()
            cur.execute("SELECT datname FROM pg_database;")
            # note the raw result of cur.fetchall is a list of tuple
            # [('postgres',), ('template1',), ('template0',), ('north_wind',)]
            # we need to convert it to list
            for item in cur.fetchall():
                db_list.append(item[0])
        return db_list

    @staticmethod
    def restore_db_with_existing_db():
        pass

    @staticmethod
    # note only the owner of the db has the right to alter the name
    def rename_db(user_name: str, user_pwd: str, old_db_name: str, new_db_name: str, host_name="127.0.0.1",
                  port="5432", force=False):
        try:
            # connect to the default db of postgresql server (postgres) 
            con = psycopg2.connect(dbname='postgres', port=port,
                                   user=user_name, host=host_name,
                                   password=user_pwd)
            con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = con.cursor()
            existing_dbs = PostgresDbManager.list_existing_databases(user_name, user_pwd, host_name)
            # if the new db exist already and forch is true, we delete the existing db, and rename the old_db_name to 
            # a new_db_name
            if (new_db_name in existing_dbs) and force:
                # close the existing db, and delete it
                cur.execute("SELECT pg_terminate_backend( pid ) "
                            "FROM pg_stat_activity "
                            "WHERE pid <> pg_backend_pid( ) "
                            "AND datname = '{}'".format(new_db_name))
                cur.execute("DROP DATABASE IF EXISTS {}".format(new_db_name))
            elif (new_db_name in existing_dbs) and not force:
                log.exception("The new db name that you give already exist in the database server. Please use another "
                              "name as the new db_name")
                raise DatabaseError
            # rename the old db name to new db name
            cur.execute('ALTER DATABASE "{}" RENAME TO "{}";'.format(old_db_name, new_db_name))

        except Exception as e:
            log.error(e)
            raise

    @staticmethod
    def create_db(user_name: str, user_pwd: str, db_name: str, host_name="127.0.0.1", port="5432") -> bool:
        try:
            con = psycopg2.connect(dbname='postgres', port=port,
                                   user=user_name, host=host_name,
                                   password=user_pwd)
        except Exception as e:
            log.error(e)
            return False

        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        existing_dbs = PostgresDbManager.list_existing_databases(user_name, user_pwd, host_name)
        if db_name in existing_dbs:
            log.exception("The db name that you give already exist in the database server. Please use another "
                          "name as the new db_name")
            return False
        else:
            try:
                cur.execute("CREATE DATABASE {} ;".format(db_name))
                cur.execute("GRANT ALL PRIVILEGES ON DATABASE {} TO {} ;".format(db_name, user_name))
            except Exception as e:
                log.error(e)
                return False
        return True


def main():
    pass


if __name__ == "__main__":
    main()
