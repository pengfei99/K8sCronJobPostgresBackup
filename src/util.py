
def get_date_format():
    """
    This function is called by DbBackupBot and DbRestoreBot for creating and restoring backup file with timestamp
    in the file name. The returned string is the format for timestamp
    :return: a string which is the format for timestamp in the backup file
    """
    return '%Y_%m_%d_%H_%M_%S'
