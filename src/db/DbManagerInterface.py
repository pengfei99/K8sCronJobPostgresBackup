import abc
from typing import Optional


class DbManagerInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'backup_db') and
                callable(subclass.backup_db) and
                hasattr(subclass, 'get_db_list') and
                callable(subclass.get_db_list) and
                hasattr(subclass, 'restore_db') and
                callable(subclass.restore_db) and
                hasattr(subclass, 'create_db') and
                callable(subclass.create_db) and
                hasattr(subclass, 'has_db') and
                callable(subclass.has_db)
                or
                NotImplemented)

    @abc.abstractmethod
    def backup_db(self, db_name: str, output_dir: str, backup_file_name: str, custom_format=False, creat_db=False) \
            -> Optional[str]:
        """
        backup a database and output the dump file to local storage

        :param db_name: The name of the database that needs to be backed up
        :param output_dir: the path of the output backup dump file
        :param backup_file_name: The name of the backup file
        :param custom_format: default value is False, if set to true, the backup dump file uses postgres custom dump
                      format which is not plain text. This format can be only imported by using pg_restore
        :param creat_db: Default value is False, if set to true, the option -C/--create will be added to the dump
                         parameters, this will add the database name to the dump file. Then the restore will create
                         db automatically. Note if you use a such dump to populate a database that has a different name,
                         it will fail.
        :return: the full file name of the database backup file. If none means backup process failed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_db_list(self) -> list:
        """
        return a list of existing database in the target db server

        :return: a list of existing database in the target db server
        """
        raise NotImplementedError

    @abc.abstractmethod
    def restore_db(self, target_db_name: str, backup_file_path: str, backup_format: str) -> bool:
        """ restore a database
        :param target_db_name: The name of the database to be restored
        :param backup_file_path: The full file path of the backup file
        :param backup_format: The format of the backup file. It supports [sql,psql] for now
        :return: return true if restore complete successfully. return false if failed

        """

        raise NotImplementedError

    @abc.abstractmethod
    def create_db(self, target_db_name: str) -> bool:
        """ create an empty database
        :param target_db_name: The name of the database to be created
        :return: return true if db creation complete successfully. return false if failed

        """
        raise NotImplementedError

    @abc.abstractmethod
    def has_db(self, target_db_name: str) -> bool:
        """
        check if the give database name already exist or not

        :param target_db_name: The name of the database to be checked
        :return: return true if db exist. return false if it does not exist

        """
        raise NotImplementedError
