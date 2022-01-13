import argparse
import datetime
import logging


def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    args_parser = argparse.ArgumentParser(description='Postgres database management')
    # when required is set to True, you must provide this parameter when calling this function
    args_parser.add_argument("--action",
                             metavar="action",
                             choices=['list_backups', 'list_dbs', 'restore', 'backup'],
                             required=True)
    args_parser.add_argument("--backup_parent_dir",
                             metavar="s3://bucket_name/bucket_key",
                             help="Parent dir for storing backup files (show with --action list_backups)")
    args_parser.add_argument("--dest-db",
                             metavar="dest_db",
                             default=None,
                             help="Name of the new restored database")
    # args_parser.add_argument("--verbose",
    #                          default=False,
    #                          help="Verbose output")

    args = args_parser.parse_args()


    # # list task
    # if args.action == "list":
    #     backup_objects = sorted(list_available_backups(storage_engine, manager_config), reverse=True)
    #     for key in backup_objects:
    #         logger.info("Key : {}".format(key))
    # # list databases task
    # elif args.action == "list_dbs":
    #     result = list_postgres_databases(postgres_host,
    #                                      postgres_db,
    #                                      postgres_port,
    #                                      postgres_user,
    #                                      postgres_password)
    #     for line in result.splitlines():
    #         logger.info(line)
    # # backup task
    # elif args.action == "backup":
    #     logger.info('Backing up {} database to {}'.format(postgres_db, local_file_path))
    #     result = backup_postgres_db(postgres_host,
    #                                 postgres_db,
    #                                 postgres_port,
    #                                 postgres_user,
    #                                 postgres_password,
    #                                 local_file_path, args.verbose)
    #     if args.verbose:
    #         for line in result.splitlines():
    #             logger.info(line)
    #
    #     logger.info("Backup complete")
    #     logger.info("Compressing {}".format(local_file_path))
    #     comp_file = compress_file(local_file_path)
    #     if storage_engine == 'LOCAL':
    #         logger.info('Moving {} to local storage...'.format(comp_file))
    #         move_to_local_storage(comp_file, filename_compressed, manager_config)
    #         logger.info("Moved to {}{}".format(manager_config.get('LOCAL_BACKUP_PATH'), filename_compressed))
    #     elif storage_engine == 'S3':
    #         logger.info('Uploading {} to Amazon S3...'.format(comp_file))
    #         upload_to_s3(comp_file, filename_compressed, manager_config)
    #         logger.info("Uploaded to {}".format(filename_compressed))
    # # restore task
    # elif args.action == "restore":
    #     if not args.date:
    #         logger.warn('No date was chosen for restore. Run again with the "list" '
    #                     'action to see available restore dates')
    #     else:
    #         try:
    #             os.remove(restore_filename)
    #         except Exception as e:
    #             logger.info(e)
    #         all_backup_keys = list_available_backups(storage_engine, manager_config)
    #         backup_match = [s for s in all_backup_keys if args.date in s]
    #         if backup_match:
    #             logger.info("Found the following backup : {}".format(backup_match))
    #         else:
    #             logger.error("No match found for backups with date : {}".format(args.date))
    #             logger.info("Available keys : {}".format([s for s in all_backup_keys]))
    #             exit(1)
    #
    #         if storage_engine == 'LOCAL':
    #             logger.info("Choosing {} from local storage".format(backup_match[0]))
    #             shutil.copy('{}/{}'.format(manager_config.get('LOCAL_BACKUP_PATH'), backup_match[0]),
    #                         restore_filename)
    #             logger.info("Fetch complete")
    #         elif storage_engine == 'S3':
    #             logger.info("Downloading {} from S3 into : {}".format(backup_match[0], restore_filename))
    #             download_from_s3(backup_match[0], restore_filename, manager_config)
    #             logger.info("Download complete")
    #
    #         logger.info("Extracting {}".format(restore_filename))
    #         ext_file = extract_file(restore_filename)
    #         # cleaned_ext_file = remove_faulty_statement_from_dump(ext_file)
    #         logger.info("Extracted to : {}".format(ext_file))
    #         logger.info("Creating temp database for restore : {}".format(postgres_restore))
    #         tmp_database = create_db(postgres_host,
    #                                  postgres_restore,
    #                                  postgres_port,
    #                                  postgres_user,
    #                                  postgres_password)
    #         logger.info("Created temp database for restore : {}".format(tmp_database))
    #         logger.info("Restore starting")
    #         result = restore_postgres_db(postgres_host,
    #                                      postgres_restore,
    #                                      postgres_port,
    #                                      postgres_user,
    #                                      postgres_password,
    #                                      restore_uncompressed,
    #                                      args.verbose)
    #         if args.verbose:
    #             for line in result.splitlines():
    #                 logger.info(line)
    #         logger.info("Restore complete")
    #         if args.dest_db is not None:
    #             restored_db_name = args.dest_db
    #             logger.info("Switching restored database with new one : {} > {}".format(
    #                 postgres_restore, restored_db_name
    #             ))
    #         else:
    #             restored_db_name = postgres_db
    #             logger.info("Switching restored database with active one : {} > {}".format(
    #                 postgres_restore, restored_db_name
    #             ))
    #
    #         swap_after_restore(postgres_host,
    #                            postgres_restore,
    #                            restored_db_name,
    #                            postgres_port,
    #                            postgres_user,
    #                            postgres_password)
    #         logger.info("Database restored and active.")
    # else:
    #     logger.warn("No valid argument was given.")
    #     logger.warn(args)


if __name__ == '__main__':
    main()
