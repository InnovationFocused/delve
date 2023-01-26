import argparse

parser = argparse.ArgumentParser()
def extracted(argv, results):
    args = parser.parse_args(argv)
    for result in results:
        yield result["extracted_fields"]
