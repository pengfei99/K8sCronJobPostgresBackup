import pytest
from S3StorageEngine import S3StorageEngine


def test_parse_path():
    path = "s3a://user-pengfei/tmp/sparkcv/input"
    result_name = "user-pengfei"
    result_key = "tmp/sparkcv/input"
    bucket_name, bucket_key = S3StorageEngine.parse_path(path)
    assert bucket_name == result_name and bucket_key == result_key


def test_build_s3_object_key():
    source_file_path = "/tmp/backup/2022-01-04_north_wind_pg_bck.sql"
    bucket_key = "me"
    result = "me/2022-01-04_north_wind_pg_bck.sql"
    assert result == S3StorageEngine.build_s3_object_key(source_file_path, bucket_key)
