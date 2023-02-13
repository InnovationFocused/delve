from argparse import ArgumentParser
import logging

import pandas as pd
import streamlit as st


parser = ArgumentParser()
parser.add_argument("-x", "--x-field")
parser.add_argument("-y", "--y-field")
parser.add_argument("-d", "--detail")
def describe(argv: list[str], results: pd.DataFrame):
    log = logging.getLogger(__name__)
    args = parser.parse_args(argv)
    log.debug(f"Found args: {args}")

    return results.describe()
