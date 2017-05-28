import logging

import socket
import click

from cassandras3.aws import ClientCache
from cassandras3.log import setup_logging
from cassandras3.util import NodeTool

logger = logging.getLogger('cassandras3')


@click.group()
def view_cmd():  # pragma: no cover
    pass


@view_cmd.command(help='Execute view')
@click.option('--region', default='us-east-1',
              help='Select the region for your bucket.')
@click.option('--keyspace', prompt='Your keyspace to view',
              help='The cassandra keyspace to view backups for.')
@click.option('--hostname', default='',
              help='The hostname to use for viewing backups.')
@click.option('--bucket', prompt='Your s3 bucket to view from',
              help='The s3 bucket used to fetch the view from.')
def view(region, keyspace, hostname, bucket):  # pragma: no cover
    do_view(region, keyspace, hostname, bucket)


def do_view(region, keyspace, hostname, bucket):
    setup_logging(logging.WARN)

    clients = ClientCache(region)
    if not hostname:
        hostname = socket.gethostname()

    node = NodeTool(clients, hostname)
    node.view(keyspace, bucket)
