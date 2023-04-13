import configparser


def get_config():
    config = configparser.ConfigParser()
    config.read("config.ini")

    remote_host = config["DEFAULT"]["REMOTE_HOST"]
    remote_user = config["DEFAULT"]["REMOTE_USER"]
    remote_password = config["DEFAULT"]["REMOTE_PASSWORD"]
    remote_database = config["DEFAULT"]["REMOTE_DATABASE"]
    local_user = config["DEFAULT"]["LOCAL_USER"]
    local_password = config["DEFAULT"]["LOCAL_PASSWORD"]
    local_database = config["DEFAULT"]["LOCAL_DATABASE"]
    proxy_host = config["DEFAULT"]["PROXY_HOST"]
    proxy_user = config["DEFAULT"]["PROXY_USER"]

    missing_vars = []
    for var in [remote_host, remote_user, remote_password, remote_database, local_user, local_password, local_database,
                proxy_host, proxy_user, ]:
        if var is None:
            missing_vars.append(var)
    if missing_vars:
        raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

    return (
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
