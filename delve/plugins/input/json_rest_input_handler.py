from typing import Optional
from urllib.parse import urlparse
from dataclasses import dataclass

import requests

from delve.config import STANDARD_INPUT_CONFIGURATION_FIELDS

@dataclass
class JSONRestInputHandlerConfigurationSchema():
    url: str
    method: str="GET"
    data: Optional[dict]=None

class JSONRestInputHandler():
    def __init__(self, parsed_name: urlparse, conf: dict):
        self.conf = conf
        settings = {
            key: value for key, value in conf.items()
            if key not in STANDARD_INPUT_CONFIGURATION_FIELDS
        }
        self.settings = JSONRestInputHandlerConfigurationSchema(**settings)
        self.session = requests.Session()

    def __iter__(self):
        return self
    
    def __next__(self):
        # return next(self.obj)
        request = requests.Request(
            self.settings["method"],
            self.settings["url"],
            data=self.settings["data"],
            # headers=self.headers,
        )
        prepped_request = request.prepare()

        # prepped.body = 'No, I want exactly this as the body.'
        # del prepped.headers['Content-Type']
        resp = self.session.send(
            prepped_request,
            verify=self.verify,
            # cert=(self.client_cert, self.client_key),
            # timeout=self.timeout,
        )
        for item in resp.json():
            yield item


