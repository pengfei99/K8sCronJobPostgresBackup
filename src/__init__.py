__version__ = '0.1.0'

# Set default logging handler to avoid "No handler found" warnings.
import logging

logging.getLogger('db_backup_restore').addHandler(logging.NullHandler())
