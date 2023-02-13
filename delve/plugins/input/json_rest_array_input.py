from typing import Optional
from urllib.parse import urlparse
import logging
import json

from pydantic import BaseModel
import requests

log = logging.getLogger(__name__)

class JSONRestArrayInputSchema(BaseModel):
    url: str
    method: str="GET"
    data: Optional[dict]=None
    key: Optional[str]=None

class JSONRestArrayInput():
    def __init__(self, **configuration: JSONRestArrayInputSchema):
        self.configuration = configuration
        log.debug(f"Found configuration: {self.configuration}")
        self.parsed_settings = JSONRestArrayInputSchema(**self.configuration)
        log.debug(f"Found parsed_settings: {self.parsed_settings}")
        self.session = requests.Session()
        log.debug("Created HTTP Session: {self.session}")

        self._data = None

    def __iter__(self):
        log.debug(f"Inside __iter__")
        return self
    
    def __next__(self):
        if self._data:
            log.debug(f"results already exist: {self._data}")
            result = json.dumps(next(self._data))
            log.debug(f"Found result: {result}")
            return result
        else:
            log.debug(f"Results not present, building HTTP request to retrieve data")
            request = requests.Request(
                self.parsed_settings.method,
                self.parsed_settings.url,
                data=self.parsed_settings.data,
                # headers=self.headers,
            )
            log.debug(f"request: {request}")
            prepped_request = request.prepare()
            log.debug(f"prepped_request: {prepped_request}")

            # prepped.body = 'No, I want exactly this as the body.'
            # del prepped.headers['Content-Type']
            response = self.session.send(
                prepped_request,
                # verify=self.verify,
                # cert=(self.client_cert, self.client_key),
                # timeout=self.timeout,
            )
            log.debug(f"Received response: {response}")
            self._data = response.json()
            if self.parsed_settings.key:
                log.debug(f"Found key in parsed_settings, pulling out the array from key: {self.parsed_settings.key}")
                self._data = self._data[self.parsed_settings.key]
            log.debug(f"Caching data to return as events: {self._data}")
            self._data = iter(self._data)
            first_result = json.dumps(next(self._data))
            log.debug(f"Found first_result: {first_result}")
            return first_result

