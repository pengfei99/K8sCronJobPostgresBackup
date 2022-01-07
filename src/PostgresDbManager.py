import gzip
import logging
from typing import Optional

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

    def backup_db(self, db_name, output_path, custom_format=False, creat_db=False) -> Optional[str]:
        """

        :param db_name:
        :param output_path:
        :param custom_format:
        :param creat_db:
        :return:
        """

        # remove the compressed option. The compression is not the job of a db manager.
        # self.backup_postgres_db_to_gz(self.user_name, self.user_pwd, db_name, output_path, self.host_name,
        #                                   self.port, custom_format, creat_db)

        return self.backup_postgres_db_to_sql(self.user_name, self.user_pwd, db_name, output_path, self.host_name,
                                              self.port, custom_format, creat_db)

    def get_db_list(self):
        return self.list_existing_databases(self.user_name, self.user_pwd, self.host_name, self.port)

    @staticmethod
    def backup_postgres_db_to_sql(user_name: str, user_pwd: str, db_name: str, output_path: str, host_name="127.0.0.1",
                                  port="5432", custom_format=False, creat_db=False) -> Optional[str]:
        """
        Backup postgres db to a file.


        :param user_name: username for connecting to the database server
        :param user_pwd: user password for connecting to the database server
        :param db_name: db name that you need to back up
        :param output_path: the path to put the backup dump file
        :param host_name: the host name of the db server
        :param port: the port of the db server
        :param custom_format: default value is False, if set to true, the backup dump file uses postgres custom dump
                      format which is not plain text. This format can be only imported by using pg_restore
        :param creat_db: Default value is False, if set to true, the option -C/--create will be added to the dump
                         parameters, this will add the database name to the dump file. Then the restore will create
                         db automatically. Note if you use a such dump to populate a database that has a different name,
                         it will fail.
        :return: None
        """
        # build the full path of the destination file
        current_date = str(datetime.date(datetime.now()))
        full_path = f"{output_path}/{current_date}_{db_name}_pg_bck.sql"
        try:
            params = ['pg_dump',
                      '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user_name, user_pwd, host_name, port, db_name)]
            if custom_format:
                params.append('-Fc')
                full_path = full_path + ".pgdump"
            if creat_db:
                params.append('-C')
            params.append(['-f', full_path])
            process = subprocess.Popen(params, stdout=subprocess.PIPE)
            if int(process.returncode) != 0:
                log.exception('Command failed. Return code : {}'.format(process.returncode))
                return None
        except Exception as e:
            log.exception(e)
            return None
        return full_path

    @staticmethod
    def backup_postgres_db_to_gz(user_name: str, user_pwd: str, db_name: str, output_path: str, host_name="127.0.0.1",
                                 port="5432", custom_format=False, creat_db=False):
        """
        Backup postgres db to a compressed file in format gz.

        :param user_name: username for connecting to the database server
        :param user_pwd: user password for connecting to the database server
        :param db_name: db name that you need to back up
        :param output_path: the path to put the backup dump file
        :param host_name: the host name of the db server
        :param port: the port of the db server
        :param custom_format: default value is False, if set to true, the backup dump file uses postgres custom dump
                      format which is not plain text. This format can be only imported by using pg_restore
        :param creat_db: Default value is False, if set to true, the option -C/--create will be added to the dump
                         parameters, this will add the database name to the dump file. Then the restore will create
                         db automatically. Note if you use a such dump to populate a database that has a different name,
                         it will fail.
        :return: None
        """

        current_date = str(datetime.date(datetime.now()))
        full_path = f"{output_path}/{current_date}_{db_name}_pg_bck.sql.gz"
        with gzip.open(full_path, 'wb') as f:
            # use subprocess to run the pg_dump command
            try:
                params = ['pg_dump',
                          '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user_name, user_pwd, host_name, port, db_name)]
                process = subprocess.Popen(params, stdout=subprocess.PIPE, universal_newlines=True)
                if custom_format:
                    params.append('-Fc')
                if creat_db:
                    params.append('-C')
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
    def restore_db_with_custom_format(user_name: str, user_pwd: str, db_name: str, backup_file_path: str,
                                      host_name="127.0.0.1",
                                      port="5432", verbose=False):
        """Restore postgres db from a dump file of custom format.
           The dump file must be created by using the -Fc option for example: pg_dump -Fc mydb > db.dump
        """
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
    def restore_db_with_sql_format(user_name: str, user_pwd: str, db_name: str, backup_file_path: str,
                                   host_name="127.0.0.1", port="5432"):
        """
           Restore postgres db from a dump file of sql(text) format.
           The dump file must be created without the -Fc option for example: pg_dump mydb > db.dump
           To restore such dump, we can use below
           psql --dbname=postgresql://{user_name}:{user_pwd}@{host_name}:{port}/{db_name} -f {backup_file_path}
           psql --dbname=postgresql://user-pengfei:pwd@10.233.30.220:5432/test2 -f /home/coder/work/dumps/db_backup.sql
           note if the db_backup.sql is generated with the option -C/--create, it will contain the database information
           and if we use it to populate a database that has a different name, we will have error. So mak

        """
        try:
            subprocess_params = [
                'psql',
                '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user_name,
                                                              user_pwd,
                                                              host_name,
                                                              port,
                                                              db_name),
                '-f', backup_file_path
            ]
            process = subprocess.Popen(subprocess_params, stdout=subprocess.PIPE)
            # Todo need to debug here, the restore works but with warnings
            if int(process.returncode) != 0:
                log.error('Command failed. Return code : {}'.format(process.returncode))
                return False
            return True
        except Exception as e:
            log.error("Issue with the db restore : {}".format(e))
            return False

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
                cur.execute('GRANT ALL PRIVILEGES ON DATABASE "{}" TO "{}" ;'.format(db_name, user_name))
            except Exception as e:
                log.error(e)
                return False
        return True


def main():
    pass


if __name__ == "__main__":
    main()
