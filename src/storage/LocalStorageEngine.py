from StorageEngineInterface import StorageEngineInterface
import shutil


class LocalStorageEngine(StorageEngineInterface):
    def __init__(self):
        self.storage_engine_type = "local"

    def upload_data(self, source_path: str, destination_path: str) -> bool:
        if source_path == destination_path:
            return True
        else:
            shutil

    def download_data(self, source_path: str, destination_path: str) -> bool:
        pass

    def list_dir(self, source_path: str) -> list:
        pass

    def get_storage_engine_type(self) -> str:
        pass
