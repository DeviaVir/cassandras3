import logging
import sh
import os

logger = logging.getLogger('cassandras3')

CASSANDRA_DATA_DIR = '/var/lib/cassandra/data/'


class NodeTool(object):
    def __init__(self, clients, hostname, host='127.0.0.1', port=7199):
        self.s3 = clients.s3()
        self.hostname = hostname
        self.host = host
        self.port = port

    def backup(self, keyspace, bucket, timestamp):
        """
        Execute a backup to a specific s3 bucket with a specific timestamp.
        :param bucket: S3 bucket used for backup.
        :param timestamp: Timestamp int used to identify the backup.
        :return:
        """
        logger.debug('Backing up cassandra "%s" to bucket "%s"' % (
            keyspace, bucket))

        tag = '%s-%s-%s' % (self.hostname, keyspace, timestamp)
        s3_path = '%s/%s/%s' % (self.hostname, keyspace, timestamp)

        self._snapshot(keyspace, tag)

        for cass_dir in self._lookup_snapshots(tag):
            for root, dirs, files in os.walk(cass_dir):
                for filename in files:
                    root_arr = root.split('/')[:-2]
                    table = root_arr[-1]
                    local_path = os.path.join(root, filename)
                    self._upload_file(
                        local_path, bucket, s3_path, table, filename)

        logger.info('Successfully backed up your cassandra keyspace!')

    def restore(self, keyspace, bucket, timestamp):
        """
        Restore a backup to a specific s3 bucket with a specific timestamp.
        :param bucket: S3 bucket used for restore.
        :param timestamp: Timestamp int used to identify the backup.
        :return:
        """
        logger.debug('Restoring cassandra "%s" from bucket "%s"' % (
            keyspace, bucket))

        s3_path = '%s/%s/%s' % (self.hostname, keyspace, timestamp)
        list_objects = self.s3.list_objects(
            Bucket=bucket, Prefix=s3_path, Delimiter='/')
        tables = []
        for key in list_objects.get('Contents'):
            filename = key.get('Key')
            table = filename.split('/')[:-1][-1]

            self._ensure_dir(table)
            self._download_file(bucket, filename, table)
            tables.append(table)

        for table in tables:
            self.refresh(keyspace, table)

        logger.info('Successfully restored your cassandra keyspace!')

    def _upload_file(self, local_path, bucket, s3_path, table, filename):
        self.s3.upload_file(local_path, bucket, '%s/%s/%s' % (
                        s3_path, table, filename))

    def _download_file(self, bucket, filename, table):
        key = filename.split('/')[-1]
        self.s3.download_file(bucket, filename, '%s/%s/%s' % (
            CASSANDRA_DATA_DIR, table, key))

    @staticmethod
    def _ensure_dir(table):
        try:
            sh.mkdir('-p', '%s/%s' % (CASSANDRA_DATA_DIR, table))
        except:
            logger.warn('Could not create directory!')

    @staticmethod
    def _lookup_snapshots(tag):
        try:
            dirs = sh.find(CASSANDRA_DATA_DIR,
                           '-name',
                           tag)
        except sh.ErrorReturnCode:
            logger.warn('Unable to execute find, nodetool did not create ' +
                        'snapshot?')
            dirs = ''

        return dirs.splitlines()

    def _snapshot(self, keyspace, tag):
        try:
            sh.nodetool('-h', self.host, '-p', self.port).snapshot(keyspace, '-t', tag)
        except sh.ErrorReturnCode:
            logger.error('Creating snapshot failed!')
            raise
        except sh.CommandNotFound:
            logger.error('Nodetool not installed!')
            raise
        except sh.AttributeError:
            """."""

    def _refresh(self, keyspace, table):
        try:
            sh.nodetool('-h', self.host, '-p', self.port).refresh(keyspace, table)
        except sh.ErrorReturnCode:
            logger.error('Running refresh failed!')
            raise
        except sh.CommandNotFound:
            logger.error('Nodetool not installed!')
            raise
        except sh.AttributeError:
            """."""
