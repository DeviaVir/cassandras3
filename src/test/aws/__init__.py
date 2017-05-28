import unittest

from mock import MagicMock
from cassandras3.aws import ClientCache


class MockedClientTest(unittest.TestCase):
    def setUp(self):
        self.s3 = MagicMock()
        self.clients = MagicMock(spec=ClientCache)
        self.clients.s3.return_value = self.s3
