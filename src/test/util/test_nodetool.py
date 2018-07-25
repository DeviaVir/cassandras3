from mock import MagicMock, patch

from botocore.exceptions import ClientError

from cassandras3.util.nodetool import NodeTool
from test.aws import MockedClientTest

KEYSPACE = 'testkeyspace'
TIMESTAMP = '000000001'
BUCKET = 'testbucket'


class TestNodeTool(MockedClientTest):
    def setUp(self):
        super(TestNodeTool, self).setUp()
        self.hostname = 'localhost'
        self.host = '127.0.0.1'
        self.port = 7199
        self.nodetool = NodeTool(self.clients, self.hostname, self.host, self.port)

    @patch('cassandras3.util.nodetool.os.walk')
    def test_backup(self, mock_walk):
        self.nodetool._snapshot = MagicMock()
        self.nodetool._lookup_snapshots = MagicMock(return_value=['test'])
        self.nodetool._upload_file = MagicMock()
        self.nodetool._clearsnapshot = MagicMock()
        mock_walk.return_value = [
            ('/tabletest/filetest/', ('_',), ('filetest',)),
        ]

        self.nodetool.backup(KEYSPACE, BUCKET, TIMESTAMP)

        tag = '%s-%s-%s' % (self.hostname, KEYSPACE, TIMESTAMP)
        self.nodetool._snapshot.assert_called_with(KEYSPACE, tag)
        self.nodetool._lookup_snapshots.assert_called_with(tag)
        self.nodetool._upload_file.assert_called_with(
            '/tabletest/filetest/filetest',
            BUCKET,
            '%s/%s/%s' % (self.hostname, KEYSPACE, TIMESTAMP),
            'tabletest',
            'filetest')
        self.nodetool._clearsnapshot.assert_called_with(KEYSPACE, tag)

    def test_restore(self):
        self.nodetool._folders = MagicMock(return_value=[('/subdirectory/filename')])
        self.nodetool._ensure_dir = MagicMock()
        self.nodetool._download_file = MagicMock()
        self.nodetool._refresh = MagicMock()

        self.nodetool.restore(KEYSPACE, BUCKET, TIMESTAMP)

        s3_path = '%s/%s/%s' % (self.hostname, KEYSPACE, TIMESTAMP)
        self.nodetool._folders.assert_called_with(BUCKET, s3_path)
        self.nodetool._ensure_dir.assert_called_with('subdirectory')
        self.nodetool._download_file.assert_called_with(
            BUCKET, '/subdirectory/filename', KEYSPACE, 'subdirectory')
        self.nodetool._refresh.assert_called_with(KEYSPACE, 'subdirectory')

    def test_view(self):
        mock_item = MagicMock()
        mock_item.get = MagicMock(return_value='testkey/')
        mock_response = MagicMock()
        mock_response.get = MagicMock(side_effect=[mock_item])
        self.s3.list_objects.side_effect = mock_response

        self.nodetool.view(KEYSPACE, BUCKET)

    def test_view_none(self):
        mock_response = MagicMock()
        mock_response.get = MagicMock(side_effect=None)
        self.s3.list_objects.side_effect = mock_response

        self.nodetool.view(KEYSPACE, BUCKET)

    def test_view_exception(self):
        client_error = ClientError({'Error': {'Code': 0}}, 'ListObjects')
        self.s3.list_objects.side_effect = client_error

        self.assertRaises(ClientError, self.nodetool.view, KEYSPACE, BUCKET)

    def test_folders(self):
        mock_item = {
            'Contents': [{
                'Key': 'test'
            }]
        }
        mock_paginate = MagicMock()
        mock_paginate.paginate = MagicMock(return_value=[mock_item])
        self.s3.get_paginator.return_value = mock_paginate

        self.assertEqual(list(self.nodetool._folders(BUCKET, '/')), ['test'])

    def test_upload_file(self):
        self.nodetool._upload_file('local_path', BUCKET, 's3_path', 'table', 'filename')
        self.s3.upload_file.assert_called_with('local_path', BUCKET, '%s/%s/%s' % (
            's3_path', 'table', 'filename'))

    def test_download_file(self):
        self.nodetool._download_file(BUCKET, 'path/to/filename', KEYSPACE, 'table')
        self.s3.download_file.assert_called_with(BUCKET, 'path/to/filename', '%s/%s/%s/%s' % (
            '/var/lib/cassandra/data', KEYSPACE, 'table', 'filename'))

    @patch('cassandras3.util.nodetool.sh')
    def test_ensure_dir(self, mock_sh):
        self.nodetool._ensure_dir('table')
        mock_sh.mkdir.assert_called_with('-p', '%s/%s' % ('/var/lib/cassandra/data', 'table'))

    @patch('cassandras3.util.nodetool.sh')
    def test_ensure_dir_exception(self, mock_sh):
        mock_sh.mkdir.side_effect = Exception('kaboom')
        self.nodetool._ensure_dir('table')

    @patch('cassandras3.util.nodetool.sh')
    def test_lookup_snapshots(self, mock_sh):
        mock_sh.find.return_value = """test1
test2"""
        dirs = self.nodetool._lookup_snapshots('tag')
        mock_sh.find.assert_called_with('/var/lib/cassandra/data', '-name', 'tag')

        self.assertEqual(['test1', 'test2'], dirs)

    @patch('cassandras3.util.nodetool.sh')
    def test_lookup_snapshots_exception(self, mock_sh):
        mock_sh.find.side_effect = Exception(400, 'Error', 'Error', 'Error')
        dirs = self.nodetool._lookup_snapshots('tag')
        self.assertEqual([], dirs)

    @patch('cassandras3.util.nodetool.sh')
    def test_snapshot(self, mock_sh):
        self.nodetool._snapshot(KEYSPACE, 'tag')
        mock_sh.nodetool.assert_called_with(
            '-h', self.host, '-p', self.port, 'snapshot', '-t', 'tag', KEYSPACE)

    @patch('cassandras3.util.nodetool.sh')
    def test_snapshot_exception(self, mock_sh):
        mock_sh.nodetool.side_effect = Exception('kaboom')
        self.assertRaises(Exception, self.nodetool._snapshot, KEYSPACE, 'tag')

    @patch('cassandras3.util.nodetool.sh')
    def test_clearsnapshot(self, mock_sh):
        self.nodetool._clearsnapshot(KEYSPACE, 'tag')
        mock_sh.nodetool.assert_called_with(
            '-h', self.host, '-p', self.port, 'clearsnapshot', '-t', 'tag', KEYSPACE)

    @patch('cassandras3.util.nodetool.sh')
    def test_clearsnapshot_exception(self, mock_sh):
        mock_sh.nodetool.side_effect = Exception('kaboom')
        self.assertRaises(Exception, self.nodetool._clearsnapshot, KEYSPACE, 'tag')

    @patch('cassandras3.util.nodetool.sh')
    def test_refresh(self, mock_sh):
        self.nodetool._refresh(KEYSPACE, 'table')
        mock_sh.nodetool.assert_called_with(
            '-h', self.host, '-p', self.port, 'refresh', KEYSPACE, 'table')

    @patch('cassandras3.util.nodetool.sh')
    def test_refresh_exception(self, mock_sh):
        mock_sh.nodetool.side_effect = Exception('kaboom')
        self.assertRaises(Exception, self.nodetool._refresh, KEYSPACE, 'table')
