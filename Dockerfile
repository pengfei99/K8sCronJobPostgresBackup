#
FROM python:3.8-bullseye

# set api as the current work dir
WORKDIR /app

# install postgresql client
RUN apt-get update && apt-get install -y postgresql-client

# copy the requirements lists
COPY ./requirements.txt /app/requirements.txt

# install all the requirements
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# copy the main code of backup
COPY ./src /app/src


# call the function
CMD ["python", "src/main.py", "--action", "list_backups", "--backup_dir", "s3://pengfei/tmp/sql_backup"]