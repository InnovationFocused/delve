import shlex
import logging
from pathlib import Path
from inspect import isgenerator

from .config import get_obj_from_name
from .encoders import UUIDEncoder

def handle_search_query(
        query: str,
        installation_directory: Path,
        plugins_config: dict,
    ):
    log = logging.getLogger(__name__)
    query_parts = query.split("|")
    log.debug(f"Found query_parts: '{query_parts}'")
    results = None
    for query_part in query_parts:
        argv = shlex.split(query_part)
        log.debug(f"Found argv: '{argv}'")
        plugin_name = argv[0]
        log.debug(f"Found plugin_name: '{plugin_name}'")
        plugin_cls_name = plugins_config.get("search").get(plugin_name)
        log.debug(f"Found plugin_cls_name: '{plugin_cls_name}'")
        plugin = get_obj_from_name(plugin_cls_name)
        log.debug(f"Found plugin: '{plugin}'")
        results = plugin(argv[1:], results)
        log.debug(f"Found results: '{results}'")
    if isgenerator(results):
        log.debug(f"results is a generator, coercing to list")
        return list(result for result in results) 
    return results
