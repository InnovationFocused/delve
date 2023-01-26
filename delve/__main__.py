import os
from pathlib import Path
import logging.config
import sys

from typer import Typer
import toml
from pony.orm import (
    Database,
    Required,
    db_session,
)

from  .defaults import (
    default_installation_directory,
    get_defaults,
)
from  .models import (
    Event,
    Tag,
    db,
)
from .config import load_config, get_module_from_name
from .inputs import handle_inputs
from .search import handle_search_query
from .apps import load_apps

cli = Typer()

@cli.command()
def startapp(
    name: str,
    installation_directory: Path=default_installation_directory,
):
    installation_directory = installation_directory.resolve()
    base_app_directory = installation_directory.joinpath("apps")
    app_directory = base_app_directory.joinpath(name)
    app_directory.mkdir()
    app_directory.joinpath("__init__.py").touch()
    app_directory.joinpath("inputs.py").write_text(
        "from delve import inputs\n"
        "\n"
        "# Put your input plugins below"
    )
    app_directory.joinpath("search.py").write_text(
        "from delve import search\n"
        "from argparse import ArgumentParser"
        "\n"
        "parser = ArgumentParser()"
        "\n"
        "# Put your search plugins below"
    )


@cli.command()
def install(
    installation_directory: Path=default_installation_directory,
):
    installation_directory = installation_directory.resolve()
    installation_directory.mkdir(parents=True, exist_ok=True)
    defaults = get_defaults(installation_directory=installation_directory)
    config_directory  = installation_directory.joinpath("config")
    config_directory.mkdir(parents=True, exist_ok=True)

    config_directory.joinpath("inputs.toml").write_text(toml.dumps(defaults["default_inputs_config"]))
    config_directory.joinpath("plugins.toml").write_text(toml.dumps(defaults["default_plugins_config"]))
    config_directory.joinpath("database.toml").write_text(toml.dumps(defaults["default_database_config"]))
    config_directory.joinpath("logging.toml").write_text(toml.dumps(defaults["default_logging_config"]))

    log_directory = installation_directory.joinpath("logs")
    log_directory.mkdir(parents=True, exist_ok=True)

    apps_directory = installation_directory.joinpath("apps")
    apps_directory.mkdir(parents=True, exist_ok=True)
    # apps_directory.joinpath("__init__.py").touch()
    
@cli.command()
def index(
    installation_directory: Path=default_installation_directory,
):
    installation_directory = installation_directory.resolve()
    logging_config =  load_config("logging", installation_directory)
    logging.config.dictConfig(logging_config)
    log = logging.getLogger(__name__)

    apps_directory = installation_directory.joinpath("apps")
    apps_directory = apps_directory
    sys.path.insert(0, str(apps_directory))
    log.debug(f"Found PATH: '{sys.path}'")
    log.debug(f"Found apps_directory: '{apps_directory}'")
    plugins_config = load_config("plugins", installation_directory)
    log.debug(f"Found plugins_config: '{plugins_config}'")
    inputs_config = load_config("inputs", installation_directory)
    log.debug(f"Found inputs_config: '{inputs_config}'")
    database_config = load_config("database", installation_directory)
    log.debug(f"Found database_config")

    db.bind(**database_config["bind"])
    db.generate_mapping(create_tables=True)

    handler_map = plugins_config["input"]["handler_map"]
    log.debug(f"Found handler_map: '{handler_map}'")

    handle_inputs(inputs_config, handler_map)

    return 0

@cli.command()
def search(
    query: str,
    installation_directory: Path=default_installation_directory,
):
    installation_directory = installation_directory.resolve()
    apps_directory = installation_directory.joinpath("apps")
    sys.path.insert(0, apps_directory)
    logging_config =  load_config("logging", installation_directory)
    logging.config.dictConfig(logging_config)
    plugins_config = load_config("plugins", installation_directory)
    database_config = load_config("database", installation_directory)
    
    db.bind(**database_config["bind"])
    db.generate_mapping(create_tables=True)

    results = handle_search_query(
        query=query,
        installation_directory=installation_directory,
        plugins_config=plugins_config,
    )
    for result in results:
        print(result)
    return 0

@cli.command()
def serve(
    installation_directory: Path=default_installation_directory,
):
    installation_directory = installation_directory.resolve()
    from subprocess import run
    # apps_directory = installation_directory.joinpath("apps")
    # sys.path.insert(0, str(apps_directory))
    logging_config =  load_config("logging", installation_directory)
    logging.config.dictConfig(logging_config)
    # plugins_config = load_config("plugins", installation_directory)
    # database_config = load_config("database", installation_directory)

    log = logging.getLogger(__name__)

    # os.environ["DELVE_INSTALLATION_DIRECTORY"] = str(installation_directory.resolve())

    run(
        [
            "streamlit",
            "run",
            Path(__file__).parent.joinpath("shim.py"),
            "--browser.gatherUsageStats",
            "false",
            "--foo",
            "--",
            "--installation-directory",
            str(installation_directory.resolve())
        ]
    )


if __name__ == "__main__":
    sys.exit(cli())
