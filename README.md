# Database Importer

Database Importer is a Python script that simplifies the process of importing a remote PostgreSQL database into a local PostgreSQL database. It uses the `psycopg2` library to execute SQL commands directly, and can also read configuration from a separate `config.ini` file.

## Features

- Simplifies the process of importing a remote PostgreSQL database into a local PostgreSQL database.
- Supports reading configuration from a separate `config.ini` file.
- Uses the `psycopg2` library to execute SQL commands directly.
- Supports logging using Python's built-in `logging` module.
- Provides error handling for various types of errors, including I/O errors, connection errors, and command execution errors.

## Requirements

- Python 3.6 or later
- `psycopg2-binary` library (version 2.9.1 or later)
- `configparser` library (version 5.0.2 or later)


## Installation

It's recommended to use a virtual environment when installing the required libraries. To create a virtual environment, run the following command:

`python3 -m venv venv`


This will create a new virtual environment named `env`. To activate the virtual environment, run:

`source venv/bin/activate`



After activating the virtual environment, install the required libraries using pip:

`pip install -r requirements.txt`



## Usage

1. Clone the repository:

`git clone https://github.com/<your-username>/database-importer.git
cd database-importer`


2. Create a `config.ini` file in the root directory of the project with the following contents:

```
[DEFAULT]
REMOTE_HOST = <remote_host>
REMOTE_USER = <remote_user>
REMOTE_PASSWORD = <remote_password>
REMOTE_DATABASE = <remote_database>
LOCAL_USER = <local_user>
LOCAL_PASSWORD = <local_password>
LOCAL_DATABASE = <local_database>
```


Replace the values in angle brackets (`<>`) with your own values.

3. Run the script:


`python database_importer.py`


The script will import the remote database into the local database.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Contributions

Contributions are welcome! Please see the `CONTRIBUTING.md` file for guidelines.

