import logging

import click
import socket
import time

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
@click.option('--keyspace', prompt='Your keyspace to backup',
              help='The cassandra keyspace to backup.')
@click.option('--bucket', prompt='Your s3 bucket to backup to',
              help='The s3 bucket used to place the backup.')
def backup(region, keyspace, bucket):  # pragma: no cover
    do_backup(region, keyspace, bucket)


def do_backup(region, keyspace, bucket):
    setup_logging(logging.WARN)

    clients = ClientCache(region)
    hostname = socket.gethostname()

    timestamp = int(time.time())

    node = NodeTool(clients, hostname)
    node.backup(keyspace, bucket, timestamp)
