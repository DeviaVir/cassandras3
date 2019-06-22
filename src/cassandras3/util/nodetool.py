import logging
import os
import sh

from botocore.exceptions import ClientError

logger = logging.getLogger('cassandras3')


class NodeTool(object):
    def __init__(self, clients, hostname='localhost', host='127.0.0.1', port=7199,
                 cassandra_data_dir='/var/lib/cassandra/data', jmxusername='', jmxpassword='',
                 kmskeyid=''):
        self.s3 = clients.s3()
        self.hostname = hostname
        self.host = host
        self.port = port
        self.cassandra_data_dir = cassandra_data_dir
        self.jmxusername = jmxusername
        self.jmxpassword = jmxpassword
        self.kmskeyid = kmskeyid

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

        logger.debug('s3 path is %s', s3_path)

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
              ' ID "%s"' % timestamp)

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
                self._ensure_dir(keyspace, table)
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

    def _s3_extra_args(self):
        extra_args = dict()

        if self.kmskeyid:
            extra_args.update({"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": self.kmskeyid})

        return extra_args

    def _upload_file(self, local_path, bucket, s3_path, table, filename):
        logger.debug('Uploading file {}/{}/{}'.format(s3_path, table, filename))
        try:
            self.s3.upload_file(local_path,
                    bucket,
                    '%s/%s/%s' % (s3_path, table, filename),
                    ExtraArgs=self._s3_extra_args())
        except:
            logger.error('Failed in uploading file')

    def _download_file(self, bucket, filename, keyspace, table):
        key = filename.split('/')[-1]
        self.s3.download_file(bucket,
                filename,
                '%s/%s/%s/%s' % (self.cassandra_data_dir, keyspace, table, key),
                ExtraArgs=self._s3_extra_args())

    def _ensure_dir(self, keyspace, table):
        logger.debug('Ensuring directory {} exists'.format(self.cassandra_data_dir + keyspace + table + key))
        try:
            sh.mkdir('-p', '%s/%s/%s' % (self.cassandra_data_dir, keyspace, table))
        except:
            logger.warning('Could not create directory!')

    def _lookup_snapshots(self, tag):
        logger.debug('Searching for snapshots with tag: {} '.format(tag))
        try:
            dirs = sh.find(self.cassandra_data_dir,
                           '-name',
                           tag)
            logger.debug('Found directory: {}'.format(dirs))
        except:
            logger.warning('Unable to execute find, nodetool did not create snapshot?')
            dirs = ''

        return dirs.splitlines()

    def _snapshot(self, keyspace, tag):
        logger.debug('Taking snapshot for {0} keyspace with tag: {1}'.format(keyspace, tag))
        try:
            if self.jmxusername and self.jmxpassword:
                output = sh.nodetool('-u', self.jmxusername, '-pw', self.jmxpassword,
                            '-h', self.host, '-p', self.port, 'snapshot', '-t', tag, keyspace)
            else:
                output = sh.nodetool('-h', self.host, '-p', self.port, 'snapshot', '-t', tag, keyspace)

            logger.error('Snapshot returned with status code {}'.format(output.exit_code))
        except:
            logger.error('Command possibly unfinished due to errors!')
            raise

    def _clearsnapshot(self, keyspace, tag):
        try:
            logger.debug('Clearing snapshots for {} keyspace and {} tag'.format(keyspace, tag))
            if self.jmxusername and self.jmxpassword:
                sh.nodetool('-u', self.jmxusername, '-pw', self.jmxpassword,
                            '-h', self.host, '-p', self.port, 'clearsnapshot', '-t', tag, keyspace)
            else:
                sh.nodetool('-h', self.host, '-p', self.port, 'clearsnapshot', '-t', tag, keyspace)
        except:
            logger.error('Command possibly unfinished due to errors!')
            raise

    def _refresh(self, keyspace, table):
        try:
            logger.debug('Refreshing: nodetool refresh')
            if self.jmxusername and self.jmxpassword:
                sh.nodetool('-u', self.jmxusername, '-pw', self.jmxpassword,
                            '-h', self.host, '-p', self.port, 'refresh', keyspace, table)
            else:
                sh.nodetool('-h', self.host, '-p', self.port, 'refresh', keyspace, table)
        except:
            logger.error('Command possibly unfinished due to errors!')
            raise
