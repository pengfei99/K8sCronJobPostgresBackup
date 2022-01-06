import abc


class StorageEngineInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'upload_data') and
                callable(subclass.upload_data) and
                hasattr(subclass, 'download_data') and
                callable(subclass.download_data) and
                hasattr(subclass, 'list_dir') and
                callable(subclass.list_dir)
                or
                NotImplemented)

    @abc.abstractmethod
    def upload_data(self, source_path: str, destination_path: str):
        """upload data from local to remote storage"""
        raise NotImplementedError

    @abc.abstractmethod
    def download_data(self, source_path: str, destination_path: str):
        """download data from remote storage to local"""
        raise NotImplementedError

    @abc.abstractmethod
    def list_dir(self, source_path: str):
        """list the content of a directory"""
        raise NotImplementedError
