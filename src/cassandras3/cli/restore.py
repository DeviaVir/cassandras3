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
def restore(region, host, port, backup, keyspace, hostname, bucket, datadir):  # pragma: no cover
    do_restore(region, host, port, backup, keyspace, hostname, bucket, datadir)


def do_restore(region, host, port, backup, keyspace, hostname, bucket, datadir):
    setup_logging(logging.WARN)

    clients = ClientCache(region)
    if not hostname:
        hostname = socket.gethostname()

    node = NodeTool(clients, hostname, host, port, datadir)
    node.restore(keyspace, bucket, backup)
