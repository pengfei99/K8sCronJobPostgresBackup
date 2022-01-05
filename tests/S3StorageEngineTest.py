from src.python.S3StorageEngine import S3StorageEngine


def test_parse_path():
    path = "s3a://user-pengfei/tmp/sparkcv/input"
    result_name = "user-pengfei"
    result_key = "tmp/sparkcv/input"
    bucket_name, bucket_key = S3StorageEngine.parse_path(path)
    assert bucket_name == result_name and bucket_key == result_key
