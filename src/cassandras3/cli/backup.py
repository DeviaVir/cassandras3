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
@click.option('--bucket', prompt='Your s3 bucket to backup to',
              help='The s3 bucket used to place the backup.')
@click.option('--datadir', default='/var/lib/cassandra/data',
              prompt='Your cassandra data directory',
              help='The cassandra directory where data are stored.')
@click.option('--jmxusername', default='',
              help='Cassandra JMX username for nodetool')
@click.option('--jmxpassword', default='',
              help='Cassandra JMX password for nodetool')
def backup(region, host, port, keyspace, bucket, datadir,
           jmxusername, jmxpassword):  # pragma: no cover
    do_backup(region, host, port, keyspace, bucket, datadir, jmxusername, jmxpassword)


def do_backup(region, host, port, keyspace, bucket, datadir,
              jmxusername, jmxpassword):
    setup_logging(logging.WARN)

    clients = ClientCache(region)
    hostname = socket.gethostname()

    timestamp = int(time.time())

    node = NodeTool(clients, hostname, host, port, datadir, jmxusername, jmxpassword)
    node.backup(keyspace, bucket, timestamp)
