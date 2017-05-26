import logging

import boto3

logger = logging.getLogger('cassandras3')


class ClientCache(object):
    """
    Lazy instantiation container for AWS clients.
    """

    def __init__(self, region):
        self._clients = {}
        self.region = region

    def s3(self):
        """
        Get s3 client.
        :return: s3 client.
        """
        return self.client('s3')

    def client(self, service_name, region=None):
        cached = self._clients.get(service_name)
        if cached:
            return cached
        region = region or self.region
        logger.debug('Connecting to %s in %s.', service_name, region)
        client = boto3.client(service_name, region)
        self._clients[service_name] = client
        return client
