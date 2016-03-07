# coding: utf8
from __future__ import unicode_literals
from coreapi.codecs import CoreJSONCodec
from flask.json import JSONEncoder
import json
import tablib


class JSONRenderer(object):
    media_type = 'application/json'
    charset = None
    format = 'json'

    def __call__(self, data, **options):
        return json.dumps(data, cls=JSONEncoder, ensure_ascii=False)


class CoreJSONRenderer(object):
    media_type = 'application/vnd.coreapi+json'
    charset = None
    format = 'coreapi'

    def __call__(self, data, **options):
        return CoreJSONCodec().dump(data)


class TextRenderer(object):
    media_type = 'text/plain'
    charset = 'utf-8'
    format = 'txt'

    def __call__(self, data, **options):
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            data = [list(item) for item in data.items()]
        dataset = tablib.Dataset()
        dataset.dict = data
        return str(dataset)


class CSVRenderer(object):
    media_type = 'application/csv'
    charset = 'utf-8'
    format = 'csv'

    def __call__(self, data, **options):
        if isinstance(data, dict):
            data = [list(item) for item in data.items()]
        dataset = tablib.Dataset()
        dataset.dict = data
        return dataset.csv


class HTMLRenderer(object):
    media_type = 'text/html'
    charset = 'utf-8'
    format = 'html'

    def __call__(self, data, **options):
        return data


DEFAULT_RENDERERS = (JSONRenderer(), TextRenderer(), CSVRenderer())
