import pymysql
pymysql.install_as_MySQLdb()

from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

# 1. MariaDB version check bypass
BaseDatabaseWrapper.check_database_version_supported = lambda self: None

# 2. MariaDB 10.4 me RETURNING clause disable karein
DatabaseFeatures.can_return_rows_from_bulk_insert = property(lambda self: False)
DatabaseFeatures.can_return_columns_from_insert = property(lambda self: False)