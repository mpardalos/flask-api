# coding: utf8
from __future__ import unicode_literals
from flask._compat import text_type
from flask_api import exceptions
from werkzeug.formparser import MultiPartParser as WerkzeugMultiPartParser
from werkzeug.formparser import default_stream_factory
from werkzeug.urls import url_decode_stream
import json


class JSONParser(object):
    media_type = 'application/json'

    def __call__(self, stream, **options):
        data = stream.read().decode('utf-8')
        try:
            return json.loads(data)
        except ValueError as exc:
            msg = 'JSON parse error - %s' % text_type(exc)
            raise exceptions.ParseError(msg)


class MultiPartParser(object):
    media_type = 'multipart/form-data'

    def __call__(self, stream, **options):
        media_type = options['media_type']
        content_length = options['content_length']
        multipart_parser = WerkzeugMultiPartParser(default_stream_factory)

        boundary = media_type.params.get('boundary')
        if boundary is None:
            msg = 'Multipart message missing boundary in Content-Type header'
            raise exceptions.ParseError(msg)
        boundary = boundary.encode('ascii')

        try:
            data, files = multipart_parser.parse(stream, boundary, content_length)
        except ValueError as exc:
            msg = 'Multipart parse error - %s' % text_type(exc)
            raise exceptions.ParseError(msg)

        data.update(files)
        return data


class URLEncodedParser(object):
    media_type = 'application/x-www-form-urlencoded'

    def __call__(self, stream, **options):
        return url_decode_stream(stream)


DEFAULT_PARSERS = (JSONParser(), MultiPartParser(), URLEncodedParser())
