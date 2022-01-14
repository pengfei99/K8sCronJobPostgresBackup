def get_date_format():
    """
    This function is called by DbBackupBot and DbRestoreBot for creating and restoring backup file with timestamp
    in the file name. The returned string is the format for timestamp
    :return: a string which is the format for timestamp in the backup file
    """
    return '%Y-%m-%d-%H-%M-%S'


def get_date_limit_of_backup_file():
    """
    This function returns the date limit (in days) for the backup file. By default, the value is 30. It means the
    DbRetoreBot will only search the backup that are less than 30 days from the current date.

    :return: the date limit of the backup file
    """
    day = 30
    return day
