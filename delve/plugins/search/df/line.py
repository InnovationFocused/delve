from argparse import ArgumentParser
import logging

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt



parser = ArgumentParser()
parser.add_argument("-x", "--x-field")
parser.add_argument("-y", "--y-field")
def line(argv: list[str], results: pd.DataFrame):
    log = logging.getLogger(__name__)
    args = parser.parse_args(argv)
    log.debug(f"Found args: {args}")
    fig = plt.figure()
    if args.x_field:
        if args.y_field:
            plt.plot(
                results.loc[:, args.x_field],
                results.loc[:, args.y_field],
            )
        else:
            plt.plot(
                results.loc[:, args.x_field],
            )
    else:
        raise ValueError("Must include x-field before you include a y-field.")
    # plt.plot(results.)
    return fig
