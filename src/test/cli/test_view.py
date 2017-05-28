from mock import MagicMock, patch
import unittest

from cassandras3.cli.view import do_view
from cassandras3.util.nodetool import NodeTool


class TestviewClient(unittest.TestCase):
    @patch('cassandras3.cli.view.ClientCache')
    @patch('cassandras3.cli.view.NodeTool')
    def test_view(self, nodetool_constructor, _):
        self._setup_mocks(nodetool_constructor)

        do_view(
            'us-east-1', 'system', 'localhost', 'test')

        self.mock_nodetool.view.assert_called_with('system', 'test')

    @patch('cassandras3.cli.view.ClientCache')
    @patch('cassandras3.cli.view.NodeTool')
    def test_view_no_hostname(self, nodetool_constructor, _):
        self._setup_mocks(nodetool_constructor)

        do_view(
            'us-east-1', 'system', '', 'test')

        self.mock_nodetool.view.assert_called_with('system', 'test')

    def _setup_mocks(self, nodetool_constructor):
        self.mock_nodetool = MagicMock(spec=NodeTool)
        nodetool_constructor.return_value = self.mock_nodetool
