import argparse
import logging
from datetime import datetime

from .utils import (
    lenient_getattrs,
    lenient_setattrs,
)

parser = argparse.ArgumentParser()
parser.add_argument("field")
def to_epoch(argv, results):
    ret = []
    log = logging.getLogger(__name__)
    args = parser.parse_args(argv)
    log.debug(f"Found args: {args}")
    for result in results:
        value = lenient_getattrs(result, args.field)
        log.debug(f"Found value: {value}")
        if not isinstance(value, datetime):
            log.debug(f"value '{value}' is not datetime object, skipping")
            ret.append(result)
            continue
        value = value.timestamp()
        log.debug(f"value after conversion: {type(value)}({value})")
        lenient_setattrs(result, args.field, value)
        ret.append(result)
    return ret