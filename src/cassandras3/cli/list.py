import logging

import click
import socket

from cassandras3.aws import ClientCache
from cassandras3.log import setup_logging

logger = logging.getLogger('cassandras3')


@click.group()
def list_cmd():  # pragma: no cover
    pass


@list_cmd.command(help='Execute list')
@click.option('--region', default='us-east-1',
              help='Select the region for your bucket.')
@click.option('--keyspace', prompt='Your keyspace to list',
              help='The cassandra keyspace to list backups for.')
@click.option('--hostname', default='',
              help='The hostname to use for listing backups.')
@click.option('--bucket', prompt='Your s3 bucket to list from',
              help='The s3 bucket used to fetch the list from.')
def list(region, keyspace, hostname, bucket):  # pragma: no cover
    do_list(region, keyspace, hostname, bucket)


def do_list(region, keyspace, hostname, bucket):
    setup_logging(logging.WARN)

    clients = ClientCache(region)
    if not hostname:
        hostname = socket.gethostname()
    prefix = '%s/%s/' % (hostname, keyspace)

    try:
        s3 = clients.s3()
        list_objects = s3.list_objects(
            Bucket=bucket, Prefix=prefix, Delimiter='/')
        for key in list_objects.get('CommonPrefixes'):
            print(key.get('Prefix').split('/')[-2])
    except:
        logger.error('Failed to perform the s3 request.')
