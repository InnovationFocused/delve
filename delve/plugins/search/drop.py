import logging
import argparse
import functools

parser = argparse.ArgumentParser()
parser.add_argument(
    "fieldnames",
    type=str,
    nargs="+",
    help="The name of the field to remove from the events",
)
def drop(argv, results):
    log = logging.getLogger(__name__)
    args = parser.parse_args(argv)
    fieldnames = args.fieldnames
    for result in results:
        for fieldname in fieldnames:
            # This might need special handling, or we could continue to
            # just support a list of dicts for a results argument
            parts = fieldname.split(".")
            item = result
            final_item = parts.pop()
            item = functools.reduce(
                lambda a, b: a[b],
                parts,
                result,
            )

            try:
                del item[final_item]
            except KeyError:
                log.debug(f"Did not find {final_item} in {item}")
                yield result
                continue
        yield result
