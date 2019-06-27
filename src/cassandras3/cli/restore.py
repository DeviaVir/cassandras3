import logging

import socket
import click

from cassandras3.aws import ClientCache
from cassandras3.log import setup_logging
from cassandras3.util import NodeTool

logger = logging.getLogger('cassandras3')


@click.group()
def restore_cmd():  # pragma: no cover
    pass


@restore_cmd.command(help='Execute restore')
@click.option('--region', default='us-east-1',
              help='Select the region for your bucket.')
@click.option('--host', default='127.0.0.1',
              help='Address of the cassandra host')
@click.option('--port', default='7199',
              help='Port of the cassandra host')
@click.option('--backup', prompt='Your backup name',
              help='The backup name to use for restoration')
@click.option('--keyspace', prompt='Your keyspace to restore from',
              help='The cassandra keyspace to restore.')
@click.option('--hostname', default='',
              help='The hostname to use for restoring.')
@click.option('--bucket', prompt='Your s3 bucket to restore from',
              help='The s3 bucket used to fetch the restore from.')
@click.option('--datadir', default='/var/lib/cassandra/data',
              prompt='Your cassandra data directory',
              help='The cassandra directory where data are stored.')
@click.option('--jmxusername', default='',
              help='Cassandra JMX username for nodetool')
@click.option('--jmxpassword', default='',
              help='Cassandra JMX password for nodetool')
@click.option('--kmskeyid', default='',
              help='The KMS key id for the bucket S3')
@click.option('--s3endpoint', default='',
        help='Override S3 endpoint for s3 compatible services')
@click.option('--loglevel',
        type=click.Choice(['NOTSET', 'DEBUG', 'INFO','WARNING', 'ERROR', 'CRITICAL']),
        default='WARNING', help='Set log level for application')

def restore(region, host, port, backup, keyspace, hostname, bucket, datadir,
            jmxusername, jmxpassword, kmskeyid, s3endpoint, loglevel):  # pragma: no cover
    do_restore(region, host, port, backup, keyspace, hostname, bucket, datadir,
               jmxusername, jmxpassword, kmskeyid,
               s3endpoint, loglevel)


def do_restore(region, host, port, backup, keyspace, hostname, bucket, datadir,
               jmxusername, jmxpassword, kmskeyid,
               s3endpoint, loglevel):
    setup_logging(logging.getLevelName(loglevel))
    clients = ClientCache(region, s3endpoint)
    if not hostname:
        hostname = socket.gethostname()

    node = NodeTool(clients, hostname, host, port, datadir, jmxusername, jmxpassword, kmskeyid)
    node.restore(keyspace, bucket, backup)
