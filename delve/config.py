from pathlib import Path
import os.path
from importlib import import_module
import logging
from string import Template

import toml

STANDARD_INPUT_CONFIGURATION_FIELDS = (
    "index",
    "host",
    "source",
    "sourcetype",
    "extractions",
    "transformations",
    "tags",
)

# def recursively_expand_env_vars(data):
#     if isinstance(data, dict):
#         return {key: recursively_expand_env_vars(value) for key, value in data.items()}
#     elif isinstance(data, (list, tuple)):
#         return [recursively_expand_env_vars(item) for item in data]
#     elif isinstance(data, str):
#         return os.path.expandvars(data)
#     elif isinstance(data, int):
#         return data
#     elif isinstance(data, bool):
#         return data
#     return data

def recursively_expand_python_vars(namespace, data=None):
    log = logging.getLogger(__name__)
    log.debug(f"Found namespace: {type(namespace)}('{namespace}')")
    if data is None:
        data = namespace.copy()
        namespace.update(os.environ)
    if isinstance(data, dict):
        return {key: recursively_expand_python_vars(namespace, value) for key, value in data.items()}
    elif isinstance(data, (list, tuple)):
        return [recursively_expand_python_vars(namespace, item) for item in data]
    elif isinstance(data, str):
        return Template(data).safe_substitute(namespace)
    elif isinstance(data, int):
        return data
    elif isinstance(data, bool):
        return data
    return data

def load_config(name: str, installation_directory: Path):
    log = logging.getLogger(__name__)
    config_directory =  installation_directory.joinpath("config")
    log.debug(f"Found config_directory: '{config_directory}'")
    config = config_directory.joinpath(f"{name}.toml")
    log.debug(f"Found config: '{config}'")
    ret = toml.loads(config.read_text())
    ret = recursively_expand_python_vars(ret)
    # ret = recursively_expand_env_vars(ret)
    log.debug(f"Found parsed config: '{ret}'")
    return ret

def get_obj_from_name(name: str):
    log = logging.getLogger(__name__)
    parts = name.split(".")
    log.debug(f"Class name split on '.': '{parts}'.")
    module = import_module('.'.join(parts[:-1]))
    log.debug(F"Module found: '{module}'.")
    cls  = getattr(module, parts[-1])
    log.debug(f"Class found: '{cls}'")
    return cls

def get_module_from_name(name: str):
    log = logging.getLogger(__name__)
    parts = name.split(".")
    log.debug(f"Class name split on '.': '{parts}'.")
    module = import_module('.'.join(parts))
    return module