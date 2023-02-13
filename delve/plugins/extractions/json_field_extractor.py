import json

def JSONFieldExtractor(event: str):
    return json.loads(event)
