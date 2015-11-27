import requests
import json
import datetime
import logging

from exception import MambuAPIException


class AbstractAPI(object):
    def __init__(self, api_):
        self.api = api_
        self.base_url = 'https://' + api_.config.domain + '/api/'
        self.json_encoder = RequestJSONEncoder()

    def _request(self, method, url, params=None, data=None):
        headers = {'Content-Type': 'application/json'} if data else {}
        dataStr = self.json_encoder.encode(data)
        logging.debug("Body: " + dataStr)
        response = getattr(requests, method)(self.base_url + url, headers=headers, params=params, data=dataStr,
                                             auth=(self.api.config.username, self.api.config.password))
        if response.status_code != 200 and response.status_code != 201:
            raise MambuAPIException("Error performing the request", response.status_code, response.json())
        return response.json()

    @staticmethod
    def _filter_params(kw, allowed):
        for key in kw:
            if key not in allowed:
                raise ValueError(key + " is not allowed parameter")

    def _build_url_params(self, kw, allowed):
        self._filter_params(kw, allowed)


class AbstractDataObject(object):
    def __init__(self, **kw):
        for key, val in kw.items():
            self.__setattr__(key, val)

    def __setattr__(self, key, val):
        if key not in type(self).fields:
            raise ValueError(key + " is not an allowed field")
        self.__dict__[key] = val

    def __getattr__(self, key):
        return self.__dict__[key]


class RequestJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, AbstractDataObject):
            return o.__dict__
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return o
