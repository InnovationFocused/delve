import os
import sys
from pathlib import Path
import logging
import logging.config
from argparse import ArgumentParser

import typer
import streamlit as st

from delve.defaults import default_installation_directory
from delve.search import handle_search_query
from delve.config import load_config, get_module_from_name
from delve.models import (
    # Event,
    # Tag,
    db,
    # bind_db,
)


parser = ArgumentParser()
parser.add_argument("-i", "--installation-directory", default=default_installation_directory)
args = parser.parse_args()

# installation_directory = os.environ.get("DELVE_INSTALLATION_DIRECTORY", )
installation_directory = Path(args.installation_directory)

os.environ["DELVE_INSTALLATION_DIRECTORY"] = str(installation_directory)

logging_config =  load_config("logging", installation_directory)
logging.config.dictConfig(logging_config)
log = logging.getLogger(__name__)
log.debug(f"Found argv: '{sys.argv}'")
log.debug(f"Found args: '{args}'")
app_dir = installation_directory.joinpath("apps")
sys.path.insert(0, str(app_dir))
log.debug(f"Found PATH: '{sys.path}'")

@st.experimental_memo
def to_csv(df):
    return df.to_csv(index=False).encode('utf-8')


st.set_page_config(
    page_title="Delve",
    layout="wide",
    initial_sidebar_state="expanded",
    # menu_items={
    #     'Get Help': 'https://www.extremelycoolapp.com/help',
    #     'Report a bug': "https://www.extremelycoolapp.com/bug",
    #     'About': "# This is a header. This is an *extremely* cool app!"
    # }
)

plugins_config = load_config("plugins", installation_directory)
installed_apps = plugins_config["installed_apps"]
installed_apps = {
    name: Path(get_module_from_name(name).__file__).parent
    for name in installed_apps
}
dashboards = []
for app_name, directory in installed_apps.items():
    log.debug(f"Found directory: {directory}")
    for path in directory.joinpath("dashboards").glob("*.py"):
        log.debug(f"Found path: {path}")
        if path.name.startswith("_"):
            continue
        log.debug(f"Found dashboard: {path}")
        _name = path.name.replace(".py", "")
        dashboards.append(".".join((app_name, "dashboards", _name)))

# default_dashboard = plugins_config["default_dashboard"]
# default_dashboard_index = dashboards.index(default_dashboard)
# default_dashboard = dashboards[default_dashboard_index]

with st.sidebar:
    selected_dashboard = st.selectbox(
        "Select Dashboard",
        dashboards,
    )
if selected_dashboard in sys.modules:
    del sys.modules[selected_dashboard]
# st.write(selected_dashboard)
# st.write(sys.modules)

get_module_from_name(selected_dashboard)
