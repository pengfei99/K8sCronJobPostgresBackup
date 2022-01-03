import gzip
import subprocess
from datetime import datetime


def backup_db(user_name: str, db_name: str, db_pwd: str, output_path: str, host_name="127.0.0.1", port="5432", ):
    backup_cmd = f"pg_dump -U {user_name} -h {host_name} -p {port} -C -d {db_name}"
    current_date = str(datetime.date(datetime.now()))
    full_path = f"{output_path}/{current_date}_{db_name}_pg_bck.gz"
    print(backup_cmd)
    print(full_path)
    with gzip.open(f'backup.gz', 'wb') as f:
        # use subprocess to run the pg_dump command
        process_open = subprocess.Popen(backup_cmd, stdout=subprocess.PIPE, universal_newlines=True)
        # send the password to the prompt
        result = process_open.communicate('{}\n'.format(db_pwd))
        for stdout_line in iter(result.stdout.readline, ""):
            f.write(stdout_line.encode('utf - 8'))
            process_open.stdout.close()
            process_open.wait()


def main():
    backup_db("user-pengfei", "north_wind", "/tmp")


if __name__ == "__main__":
    main()
