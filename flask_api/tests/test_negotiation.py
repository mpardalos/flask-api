# coding: utf8
from __future__ import unicode_literals
import unittest
import flask_api
from flask_api import exceptions
from flask_api.negotiation import BaseNegotiation, DefaultNegotiation
import pytest


app = flask_api.FlaskAPI(__name__)


class JSON(object):
    media_type = 'application/json'


class HTML(object):
    media_type = 'application/html'


class URLEncodedForm(object):
    media_type = 'application/x-www-form-urlencoded'


class TestRendererNegotiation(unittest.TestCase):
    def test_select_renderer_client_preference(self):
        negotiation = DefaultNegotiation()
        renderers = [JSON, HTML]
        headers = {'Accept': 'application/html'}
        with app.test_request_context(headers=headers):
            renderer, media_type = negotiation.select_renderer(renderers)
            assert renderer == HTML
            assert str(media_type) == 'application/html'

    def test_select_renderer_no_accept_header(self):
        negotiation = DefaultNegotiation()
        renderers = [JSON, HTML]
        with app.test_request_context():
            renderer, media_type = negotiation.select_renderer(renderers)
            assert renderer == JSON
            assert str(media_type) == 'application/json'

    def test_select_renderer_server_preference(self):
        negotiation = DefaultNegotiation()
        renderers = [JSON, HTML]
        headers = {'Accept': '*/*'}
        with app.test_request_context(headers=headers):
            renderer, media_type = negotiation.select_renderer(renderers)
            assert renderer == JSON
            assert str(media_type) == 'application/json'

    def test_select_renderer_failed(self):
        negotiation = DefaultNegotiation()
        renderers = [JSON, HTML]
        headers = {'Accept': 'application/xml'}
        with app.test_request_context(headers=headers):
            with pytest.raises(exceptions.NotAcceptable):
                renderer, media_type = negotiation.select_renderer(renderers)

    def test_renderer_negotiation_not_implemented(self):
        negotiation = BaseNegotiation()
        with pytest.raises(NotImplementedError) as exception:
            negotiation.select_renderer([])
        msg = str(exception.value)
        expected = '`select_renderer()` method must be implemented for class "BaseNegotiation"'
        assert msg == expected


class TestParserNegotiation(unittest.TestCase):
    def test_select_parser(self):
        negotiation = DefaultNegotiation()
        parsers = [JSON, URLEncodedForm]
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        with app.test_request_context(headers=headers):
            renderer, media_type = negotiation.select_parser(parsers)
            assert renderer == URLEncodedForm
            assert str(media_type) == 'application/x-www-form-urlencoded'

    def test_select_parser_failed(self):
        negotiation = DefaultNegotiation()
        parsers = [JSON, URLEncodedForm]
        headers = {'Content-Type': 'application/xml'}
        with app.test_request_context(headers=headers):
            with pytest.raises(exceptions.UnsupportedMediaType):
                renderer, media_type = negotiation.select_parser(parsers)

    def test_parser_negotiation_not_implemented(self):
        negotiation = BaseNegotiation()
        with pytest.raises(NotImplementedError) as exception:
            negotiation.select_parser([])
        msg = str(exception.value)
        expected = '`select_parser()` method must be implemented for class "BaseNegotiation"'
        assert msg == expected
