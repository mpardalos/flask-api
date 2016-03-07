# coding: utf8
from __future__ import unicode_literals
from flask import Request
from flask_api.parsers import DEFAULT_PARSERS
from flask_api.renderers import DEFAULT_RENDERERS
from werkzeug.datastructures import MultiDict
from werkzeug.urls import url_decode_stream
from werkzeug.wsgi import get_content_length
from werkzeug._compat import to_unicode
import io


def _negotiate_parser(content_type, parsers):
    """
    Given the value of a 'Content-Type' header, return the appropriate
    parser registered to decode the request content.
    """
    if content_type is None:
        return parsers[0]

    content_type = content_type.split(';')[0].strip().lower()

    for parser in parsers:
        if parser.media_type == content_type:
            return parser

    raise UnsupportedContentType()


def _negotiate_renderer(accept, renderers):
    """
    Given the value of a 'Accept' header, return a two tuple of the appropriate
    content type and codec registered to encode the response content.
    """
    if accept is None:
        return renderers[0]

    acceptable = set([
        item.split(';')[0].strip().lower()
        for item in accept.split(',')
    ])

    for renderer in renderers:
        if renderer.media_type in acceptable:
            return renderer

    for renderer in renderers:
        if renderer.media_type.split('/')[0] + '/*' in acceptable:
            return renderer

    if '*/*' in acceptable:
        return renderers[0]

    raise NotAcceptable()


class APIRequest(Request):
    parsers = DEFAULT_PARSERS
    renderers = DEFAULT_RENDERERS

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._parse()
        return self._data

    @property
    def parser(self):
        if not hasattr(self, '_parser'):
            self._parse()
        return self._parser

    @property
    def renderer(self):
        if not hasattr(self, '_renderer'):
            self._renderer = self._determine_renderer()
        return self._renderer

    @property
    def form(self):
        msg = 'Accessing `request.form` is incorrect, use `request.data` instead.'
        raise NotImplementedError(msg)

    @property
    def files(self):
        msg = 'Accessing `request.files` is incorrect, use `request.data` instead.'
        raise NotImplementedError(msg)

    def _parse(self):
        """
        Parse the body of the request, using whichever parser satifies the
        client 'Content-Type' header.
        """
        if not self.content_type or not self.content_length:
            self._data = MultiDict()
            return

        self._parser = _negotiate_parser(self.content_type, self.parsers)
        context = {'request': self}
        try:
            self._data = self._parser(self.stream, **context)
        except:
            # Ensure that accessing `request.data` again does not reraise
            # the exception, so that eg exceptions can handle properly.
            self._data = MultiDict()
            raise

    def _determine_renderer(self):
        """
        Determine which of the available renderers should be used for
        rendering the response content, based on the client 'Accept' header.
        """
        accept = self.headers.get('Accept', '*/*')
        return _negotiate_renderer(accept, self.renderers)
