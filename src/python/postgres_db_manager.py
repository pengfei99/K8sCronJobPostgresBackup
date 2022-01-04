import gzip
import logging
import subprocess
from datetime import datetime

log = logging.getLogger(__name__)


def backup_postgres_db_to_sql(user_name: str, user_pwd: str, db_name: str, output_path: str, host_name="127.0.0.1",
                              port="5432", verbose=False):
    """
    Backup postgres db to a file.
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


def backup_postgres_db_to_gz(user_name: str, user_pwd: str, db_name: str, output_path: str, host_name="127.0.0.1",
                             port="5432"):
    # cmd = f"pg_dump --dbname=postgresql://{user_name}:{user_pwd}@{host_name}:{port}/{db_name} -v"
    # print(cmd)
    current_date = str(datetime.date(datetime.now()))
    full_path = f"{output_path}/{current_date}_{db_name}_pg_bck.sql.gz"
    with gzip.open(full_path, 'wb') as f:
        # use subprocess to run the pg_dump command
        try:
            process = subprocess.Popen(['pg_dump',
                                        '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user_name, user_pwd, host_name,
                                                                                      port, db_name),
                                        '-v'],
                                       stdout=subprocess.PIPE, universal_newlines=True)
            # get the output of the subprocess, write output to the gz file line by line in streaming mode
            # this way we don't need very large memory when backup big databases
            for stdout_line in iter(process.stdout.readline, ""):
                f.write(stdout_line.encode('utf-8'))
            process.stdout.close()
            process.wait()
        except Exception as e:
            log.exception(e)
            exit(1)


def main():
    backup_postgres_db_to_gz("user-pengfei", "gv8eba5xmsw4kt2uk1mn", "north_wind", "./dumps", host_name="10.233.30.220")

    pass


if __name__ == "__main__":
    main()
