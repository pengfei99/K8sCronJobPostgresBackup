import abc


class StorageEngineInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'upload_data') and
                callable(subclass.upload_data) and
                hasattr(subclass, 'download_data') and
                callable(subclass.download_data) and
                hasattr(subclass, 'list_dir') and
                callable(subclass.list_dir) and
                hasattr(subclass, 'get_storage_engine_type') and
                callable(subclass.get_storage_engine_type)
                or
                NotImplemented)

    @abc.abstractmethod
    def upload_data(self, source_path: str, destination_path: str) -> bool:
        """upload data from local storage to remote storage

        :param source_path: The path of source file
        :param destination_path: The path and name of the destination of the file after upload.
                       e.g s3a://pengfei/tmp/toto.txt is valid. s3a://pengfei/tmp is not. The uploaded file will be
                       renamed to tmp by using s3a://pengfei/tmp

        :return: true if upload succeed, false if failed
        """
        raise NotImplementedError

    @abc.abstractmethod
    def download_data(self, source_path: str, destination_path: str) -> bool:
        """download data from remote storage to local

        :param source_path: The path of source file
        :param destination_path: The path of the destination of the file after download
        :return: true if upload succeed, false if failed
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list_dir(self, source_path: str) -> list:
        """list the content of a directory

        :param source_path: The path for finding available backup
        :return: a list of available backup
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_storage_engine_type(self) -> str:
        """return the type of storage engine

        :return: the type of the storage engine, e.g. s3, local
        """
        raise NotImplementedError
