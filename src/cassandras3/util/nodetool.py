import logging
import os
import sh

logger = logging.getLogger('cassandras3')


class NodeTool(object):
    def __init__(self, clients, hostname='localhost', host='127.0.0.1', port=7199,
                 cassandra_data_dir='/var/lib/cassandra/data'):
        self.s3 = clients.s3()
        self.hostname = hostname
        self.host = host
        self.port = port
        self.cassandra_data_dir = cassandra_data_dir

    def backup(self, keyspace, bucket, timestamp):
        """
        Execute a backup to a specific s3 bucket with a specific timestamp.
        :param bucket: S3 bucket used for backup.
        :param timestamp: Timestamp int used to identify the backup.
        :return:
        """
        logger.debug('Backing up cassandra "%s" to bucket "%s"',
                     keyspace, bucket)

        tag = '%s-%s-%s' % (self.hostname, keyspace, timestamp)
        s3_path = '%s/%s/%s' % (self.hostname, keyspace, timestamp)

        self._snapshot(keyspace, tag)

        for cass_dir in self._lookup_snapshots(tag):
            for root, _, files in os.walk(cass_dir):
                for filename in files:
                    root_arr = root.split('/')[:-2]
                    table = root_arr[-1]
                    local_path = os.path.join(root, filename)
                    self._upload_file(
                        local_path, bucket, s3_path, table, filename)

        print('Successfully backed up your cassandra keyspace with backup' +
              ' ID "%s"!' % timestamp)

        self._clearsnapshot(keyspace, tag)

    def restore(self, keyspace, bucket, timestamp):
        """
        Restore a backup to a specific s3 bucket with a specific timestamp.
        :param bucket: S3 bucket used for restore.
        :param timestamp: Timestamp int used to identify the backup.
        :return:
        """
        logger.debug('Restoring cassandra "%s" from bucket "%s"',
                     keyspace, bucket)

        s3_path = '%s/%s/%s' % (self.hostname, keyspace, timestamp)
        list_objects = self._folders(bucket, s3_path)
        tables = []
        for filename in list(list_objects):
            table = filename.split('/')[:-1][-1]

            if table not in tables:
                self._ensure_dir(table)
                tables.append(table)
            self._download_file(bucket, filename, keyspace, table)

        for table in tables:
            table_name = table.split('-')[0]
            self._refresh(keyspace, table_name)

        print('Successfully restored your cassandra keyspace!')

    def view(self, keyspace, bucket):
        prefix = '%s/%s/' % (self.hostname, keyspace)

        try:
            view_objects = self.s3.list_objects(
                Bucket=bucket, Prefix=prefix, Delimiter='/')
            if view_objects.get('CommonPrefixes'):
                for key in view_objects.get('CommonPrefixes'):  # pragma: no cover
                    print(key.get('Prefix').split('/')[-2])
        except:
            logger.error('Failed to perform the s3 request!')
            raise

    def _folders(self, bucket, prefix=''):
        paginator = self.s3.get_paginator('list_objects_v2')
        for result in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for item in result.get('Contents'):
                yield item.get('Key')

    def _upload_file(self, local_path, bucket, s3_path, table, filename):
        self.s3.upload_file(local_path, bucket, '%s/%s/%s' % (
            s3_path, table, filename))

    def _download_file(self, bucket, filename, keyspace, table):
        key = filename.split('/')[-1]
        self.s3.download_file(bucket, filename, '%s/%s/%s/%s' % (
            self.cassandra_data_dir, keyspace, table, key))

    def _ensure_dir(self, table):
        try:
            sh.mkdir('-p', '%s/%s' % (self.cassandra_data_dir, table))
        except:
            logger.warn('Could not create directory!')

    def _lookup_snapshots(self, tag):
        try:
            dirs = sh.find(self.cassandra_data_dir,
                           '-name',
                           tag)
        except:
            logger.warn('Unable to execute find, nodetool did not create ' +
                        'snapshot?')
            dirs = ''

        return dirs.splitlines()

    def _snapshot(self, keyspace, tag):
        try:
            sh.nodetool('-h', self.host, '-p', self.port, 'snapshot', '-t', tag, keyspace)
        except:
            logger.error('Command possibly unfinished due to errors!')
            raise

    def _clearsnapshot(self, keyspace, tag):
        try:
            sh.nodetool('-h', self.host, '-p', self.port, 'clearsnapshot', '-t', tag, keyspace)
        except:
            logger.error('Command possibly unfinished due to errors!')
            raise

    def _refresh(self, keyspace, table):
        try:
            sh.nodetool('-h', self.host, '-p', self.port, 'refresh', keyspace, table)
        except:
            logger.error('Command possibly unfinished due to errors!')
            raise
