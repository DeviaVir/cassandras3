import unittest

from mock import patch
from cassandras3.aws.clients import ClientCache

REGION = 'us-east-1'


class TestClientCache(unittest.TestCase):
    def setUp(self):
        self.clients = ClientCache(REGION)

    @patch('cassandras3.aws.clients.boto3')
    def test_s3(self, mock_boto3):
        self.clients.s3()
        mock_boto3.client.assert_called_once_with('s3', REGION)

    @patch('cassandras3.aws.clients.boto3')
    def test_s3_cached(self, mock_boto3):
        self.clients.s3()
        self.clients.s3()
        self.assertEqual(1, mock_boto3.client.call_count)
