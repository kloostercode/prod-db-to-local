import logging

from config import get_config
from database_importer import DatabaseImporter


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[logging.StreamHandler()],
    )

    config = get_config()
    (
        remote_host,
        remote_user,
        remote_password,
        remote_database,
        local_user,
        local_password,
        local_database,
        proxy_host,
        proxy_user,
    ) = config

    importer = DatabaseImporter(
        remote_host,
        remote_user,
        remote_password,
        remote_database,
        local_user,
        local_password,
        local_database,
        proxy_host,
        proxy_user,
    )
    importer.import_database()


if __name__ == "__main__":
    main()

