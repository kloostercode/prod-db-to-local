import os
import re
import subprocess
import time


class DatabaseImporter:
    def __init__(
        self,
        remote_host,
        remote_user,
        remote_password,
        remote_database,
        local_user,
        local_password,
        local_database,
        proxy_host,
        proxy_user,
    ):
        self.remote_host = remote_host
        self.remote_user = remote_user
        self.remote_password = remote_password
        self.remote_database = remote_database
        self.local_user = local_user
        self.local_password = local_password
        self.local_database = local_database
        self.proxy_host = proxy_host
        self.proxy_user = proxy_user
        self.remote_dump_file = "dump.sql"
        self.local_dump_file = os.path.join(os.getcwd(), "dump.sql")

    def _execute_command(self, command, input_data=None):
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, error = process.communicate(
            input_data.encode() if input_data else None
        )
        if error:
            raise Exception(f"Error executing command: {error}")
        return output.decode("utf-8").strip(), process.returncode

    def _get_ssh_credentials(self):
        ssh_config_file = os.path.expanduser("~/.ssh/config")
        with open(ssh_config_file) as f:
            ssh_config = f.read()

        patterns = {
            "ssh_host": r"Host\s+"
            + re.escape(self.remote_host)
            + r"(\n\s+.+\n)*\s+HostName\s+([^\s\n]+)",
            "ssh_user": r"Host\s+"
            + re.escape(self.remote_host)
            + r"(\n\s+.+\n)*\s+User\s+([^\s\n]+)",
            "ssh_password": r"Host\s+"
            + re.escape(self.remote_host)
            + r"(\n\s+.+\n)*\s+Password\s+([^\s\n]+)",
        }

        return {
            key: re.search(pattern, ssh_config).group(2)
            if (match := re.search(pattern, ssh_config))
            else None
            for key, pattern in patterns.items()
        }

    def import_database(self):
        # Create an SSH tunnel to the proxy host
        ssh_tunnel_command = f'ssh -L 5432:{self.remote_host}:5432 {self.proxy_user}@{self.proxy_host} -N'
        ssh_tunnel_process = subprocess.Popen(
            ssh_tunnel_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("Creating SSH tunnel to proxy host %s..." % self.proxy_host)

        # Wait for the SSH tunnel to be established
        time.sleep(3)

        # Execute the pg_dump command on the remote database server through the SSH tunnel
        pg_dump_command = f'pg_dump -h {self.remote_host} -U {self.remote_user} -W -F p {self.remote_database}'
        ssh_command = f'ssh -L 5432:{self.remote_host}:5432 {self.proxy_user}@{self.proxy_host} "{pg_dump_command}"'
        ssh_process = subprocess.Popen(
            ssh_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("Exporting database %s from %s..." % (self.remote_database, self.remote_host))

        # Wait for the pg_dump command to complete and capture its output
        pg_dump_output, pg_dump_error = ssh_process.communicate()
        if pg_dump_error:
            raise Exception(
                f"Error exporting database {self.remote_database} from {self.remote_host}: {pg_dump_error.decode('utf-8')}")

        # Write the pg_dump output to a local file
        with open(self.remote_dump_file, "wb") as f:
            f.write(pg_dump_output)

        # Drop and create the local database
        drop_database_command = f'psql -U {self.local_user} -W -c "DROP DATABASE IF EXISTS {self.local_database}"'
        create_database_command = f'psql -U {self.local_user} -W -c "CREATE DATABASE {self.local_database}"'
        self._execute_command(drop_database_command)
        self._execute_command(create_database_command)

        # Import the database dump file into the local database
        import_command = f'psql -U {self.local_user} -W -d {self.local_database} < {self.local_dump_file}'
        self._execute_command(import_command)

        # Delete the local and remote dump files
        os.remove(self.remote_dump_file)
        os.remove(self.local_dump_file)

        print("Successfully imported database %s from %s into %s on localhost." % (
            self.remote_database,
            self.remote_host,
            self.local_database,
        ))
        print("You may want to remove the dump file now.")

        # Terminate the SSH tunnel to the proxy host
        ssh_tunnel_process.terminate()

