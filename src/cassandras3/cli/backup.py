import logging

import socket
import time
import click

from cassandras3.aws import ClientCache
from cassandras3.log import setup_logging
from cassandras3.util import NodeTool

logger = logging.getLogger('cassandras3')


@click.group()
def backup_cmd():  # pragma: no cover
    pass


@backup_cmd.command(help='Execute backup')
@click.option('--region', default='us-east-1',
        help='Select the region for your bucket.')
@click.option('--host', default='127.0.0.1',
        help='Address of the cassandra host')
@click.option('--port', default='7199',
        help='Port of the cassandra host')
@click.option('--keyspace', prompt='Your keyspace to backup',
        help='The cassandra keyspace to backup.')
@click.option('--datadir', default='/var/lib/cassandra/data',
        prompt='Your cassandra data directory',
        help='The cassandra directory where data are stored.')
@click.option('--jmxusername', default='',
        help='Cassandra JMX username for nodetool')
@click.option('--jmxpassword', default='',
        help='Cassandra JMX password for nodetool')
@click.option('--bucket', prompt='Your s3 bucket to backup to',
        help='The s3 bucket used to place the backup.')
@click.option('--kmskeyid', default='',
        help='The KMS key id for the bucket S3')
@click.option('--s3endpoint', default='',
        help='Override S3 endpoint for s3 compatible services')
@click.option('--loglevel',
        type=click.Choice(['NOTSET', 'DEBUG', 'INFO','WARNING', 'ERROR', 'CRITICAL']),
        default='WARNING', help='Set log level for application')


def backup(host, port, keyspace, datadir, jmxusername, jmxpassword,
         region, bucket, kmskeyid, s3endpoint, loglevel):  # pragma: no cover
    do_backup(host, port, keyspace, datadir, jmxusername, jmxpassword, region, bucket, kmskeyid, s3endpoint, loglevel)


def do_backup(host, port, keyspace, datadir, jmxusername, jmxpassword,
              region, bucket, kmskeyid, s3endpoint, loglevel):
    setup_logging(logging.getLevelName(loglevel))
    clients = ClientCache(region, s3endpoint)
    hostname = socket.gethostname()

    timestamp = time.strftime("%Z-%Y-%m-%d-%H:%M:%S", time.localtime())

    node = NodeTool(clients, hostname, host, port, datadir, jmxusername, jmxpassword, kmskeyid)
    node.backup(keyspace, bucket, timestamp)

