import argparse
import logging

from .utils import (
    lenient_getattrs,
    lenient_setattrs,
)

parser = argparse.ArgumentParser()
parser.add_argument("field")
parser.add_argument("type", choices=("int", "str"))
def cast(argv, results):
    ret = []
    log = logging.getLogger(__name__)
    args = parser.parse_args(argv)
    log.debug(f"Found args: {args}")
    _type = None
    if _type == "int":
        _type = int
    elif _type == "str":
        _type = str
    log.debug(f"Found _type: {_type}")
    log.debug(f"Found fieldname: {args.field}")
    for result in results:
        ret.append(result)
        value = lenient_getattrs(result, args.field)
        log.debug(f"Found value: {value}")
        value = _type(value)
        log.debug(f"Casted value as {_type}: {value}")
        result = lenient_setattrs(result, args.field, value)
    return ret