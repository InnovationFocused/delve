import logging

def lenient_setattrs(item, field, value):
    log = logging.getLogger(__name__)
    log.debug(f"Entering lenient_getattr args: {item}, {field}")
    parts = field.split(".")
    log.debug(f"Found parts: '{parts}'")
    ret = item
    log.debug(f"Found ret: '{ret}'")
    for part in  parts:
        try:
            ret = getattr(ret, part)
            log.debug(f"Found ret attr: '{ret}'")
        except AttributeError:
            try:
                ret = ret[part]
                log.debug(f"Found ret item: '{ret}'")
            except KeyError:
                log.debug(f"Field '{part}' not found in '{ret}'.")
                ret = None
    ret = value
    log.debug(f"Set value for {item}, {field}: '{ret}'")
    return item

def lenient_getattrs(item, field):
    log = logging.getLogger(__name__)
    log.debug(f"Entering lenient_getattr args: {item}, {field}")
    parts = field.split(".")
    log.debug(f"Found parts: '{parts}'")
    ret = item
    log.debug(f"Found ret: '{ret}'")
    for part in  parts:
        try:
            ret = getattr(ret, part)
            log.debug(f"Found ret: '{ret}'")
        except AttributeError:
            try:
                ret = ret[part]
                log.debug(f"Found ret: 'ret'")
            except KeyError:
                log.debug(f"Field '{part}' not found in '{ret}'.")
                ret = None
    log.debug(f"Found final return value: '{ret}'")
    return ret


def get_field_name(field):
    log = logging.getLogger(__name__)
    _field = "e"
    # __field = "Event"
    parts = field.split(".")
    log.debug(f"Found parts: '{parts}'")
    if parts[0] == "extracted_fields":
        # Would be nice to auto-detect JSON fields. but for now,  go with the one we know about
        log.debug(f"Examining extracted_fields: '{parts}'")
        _field += ".extracted_fields"
        # __field += ".extracted_fields"
        for part in parts[1:]:
            log.debug(f"Found part: '{part}'")
            _field += f"['{part}']"
            # __field += f"['{part}']"
    else:
        for part in parts:
            _field += f".{part}"
            # __field += f".{part}"
    log.debug(f"Found field name: '{_field}'")
    return _field
