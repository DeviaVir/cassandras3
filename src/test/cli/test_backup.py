from mock import MagicMock, patch, ANY
import unittest

from cassandras3.cli.backup import do_backup
from cassandras3.util.nodetool import NodeTool


class TestBackupClient(unittest.TestCase):
    @patch('cassandras3.cli.backup.ClientCache')
    @patch('cassandras3.cli.backup.NodeTool')
    def test_backup(self, nodetool_constructor, _):
        self._setup_mocks(nodetool_constructor)

        do_backup('us-east-1', 'localhost', 7119, 'system', 'test', '/var/lib/cassandra/data')

        self.mock_nodetool.backup.assert_called_with('system', 'test', ANY)

    def _setup_mocks(self, nodetool_constructor):
        self.mock_nodetool = MagicMock(spec=NodeTool)
        nodetool_constructor.return_value = self.mock_nodetool
