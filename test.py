import os
import unittest
from unittest.mock import patch, Mock

from database_importer import DatabaseImporter


class TestDatabaseImporter(unittest.TestCase):
    @patch("subprocess.Popen")
    def test_execute_command_success(self, mock_popen):
        # Arrange
        mock_process = Mock()
        mock_process.communicate.return_value = ("Output", None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Act
        output, code = DatabaseImporter()._execute_command("command")

        # Assert
        self.assertEqual(output, "Output")
        self.assertEqual(code, 0)
        mock_popen.assert_called_with(
            "command",
            shell=True,
            stdin=-1,
            stdout=-1,
            stderr=-1,
        )
        mock_process.communicate.assert_called_once_with(None)

    @patch("subprocess.Popen")
    def test_execute_command_error(self, mock_popen):
        # Arrange
        mock_process = Mock()
        mock_process.communicate.return_value = (None, "Error")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        # Act/Assert
        with self.assertRaises(Exception) as cm:
            DatabaseImporter()._execute_command("command")
            self.assertEqual(str(cm.exception), "Error executing command: Error")
        mock_popen.assert_called_with(
            "command",
            shell=True,
            stdin=-1,
            stdout=-1,
            stderr=-1,
        )
        mock_process.communicate.assert_called_once_with(None)

    @patch("subprocess.Popen")
    def test_import_database_success(self, mock_popen):
        # Arrange
        mock_tunnel_process = Mock()
        mock_dump_process = Mock()
        mock_dump_process.communicate.return_value = ("Output", None)
        mock_dump_process.returncode = 0
        mock_popen.side_effect = [mock_tunnel_process, mock_dump_process]

        # Act
        importer = DatabaseImporter(
            "remote_host",
            "remote_user",
            "remote_password",
            "remote_database",
            "local_user",
            "local_password",
            "local_database",
            "proxy_host",
            "proxy_user",
        )
        importer.import_database()

        # Assert
        self.assertEqual(len(mock_popen.mock_calls), 3)
        mock_popen.assert_any_call(
            'ssh -L 5432:remote_host:5432 proxy_user@proxy_host -N',
            shell=True,
            stdout=-1,
            stderr=-1,
        )
        mock_popen.assert_any_call(
            'ssh -L 5432:remote_host:5432 proxy_user@proxy_host "pg_dump -h remote_host -U remote_user -W -F p remote_database"',
            shell=True,
            stdout=-1,
            stderr=-1,
        )
        mock_popen.assert_any_call(
            'psql -U local_user -W -c "CREATE DATABASE local_database"',
            shell=True,
            stdin=-1,
            stdout=-1,
            stderr=-1,
        )
        mock_popen.assert_any_call(
            'psql -U local_user -W -d local_database < %s' % os.path.join(os.getcwd(), "dump.sql"),
            shell=True,
            stdin=-1,
            stdout=-1,
            stderr=-1,
        )
        mock_tunnel_process.terminate.assert_called_once_with()

    @patch("subprocess.Popen")
    def test_import_database_error(self, mock_popen):
        # Arrange
        mock_tunnel_process = Mock()
        mock_dump_process = Mock()
        mock_dump_process.communicate.return_value = (None, "Error")
        mock_dump_process.returncode = 1
        mock_popen.side_effect = [mock_tunnel_process, mock_dump_process]

        # Act/Assert
        importer = DatabaseImporter(
            "remote_host",
            "remote_user",
            "remote_password",
            "remote_database",
            "local_user",
            "local_password",
            "local_database",
            "proxy_host",
            "proxy_user",
        )
        with self.assertRaises(Exception) as cm:
            importer.import_database()
            self.assertEqual(str(cm.exception), "Error exporting database remote_database from remote_host: Error")
        mock_popen.assert_any_call(
            'ssh -L 5432:remote_host:5432 proxy_user@proxy_host -N',
            shell=True,
            stdout=-1,
            stderr=-1,
        )
        mock_popen.assert_any_call(
            'ssh -L 5432:remote_host:5432 proxy_user@proxy_host "pg_dump -h remote_host -U remote_user -W -F p remote_database"',
            shell=True,
            stdout=-1,
            stderr=-1,
        )
        mock_tunnel_process.terminate.assert_called_once_with()
        self.assertFalse(os.path.exists("dump.sql"))


if __name__ == "__main__":
    unittest.main()


