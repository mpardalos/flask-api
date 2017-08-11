# coding: utf8
from __future__ import unicode_literals
from flask_api import renderers, status, FlaskAPI
from flask_api.decorators import set_renderers
from flask_api.mediatypes import MediaType
import unittest
import pytest


class RendererTests(unittest.TestCase):
    def test_render_json(self):
        renderer = renderers.JSONRenderer()
        content = renderer.render({'example': 'example'}, MediaType('application/json'))
        expected = '{"example": "example"}'
        assert content == expected

    def test_render_json_with_indent(self):
        renderer = renderers.JSONRenderer()
        content = renderer.render({'example': 'example'}, MediaType('application/json; indent=4'))
        expected = '{\n    "example": "example"\n}'
        assert content == expected

    def test_render_browsable_encoding(self):
        app = FlaskAPI(__name__)

        @app.route('/_love', methods=['GET'])
        def love():
            return {"test": "I <3 Python"}

        with app.test_client() as client:
            response = client.get('/_love',
                                  headers={"Accept": "text/html"})
            html = str(response.get_data())
            assert 'I &lt;3 Python' in html
            assert '<h1>Love</h1>' in html
            assert '/_love' in html

    def test_render_browsable_linking(self):
        app = FlaskAPI(__name__)

        @app.route('/_happiness', methods=['GET'])
        def happiness():
            return {"url": "http://example.org",
                    "a tag": "<br />"}

        with app.test_client() as client:
            response = client.get('/_happiness',
                                  headers={"Accept": "text/html"})
            html = str(response.get_data())
            assert '<a href="http://example.org">http://example.org</a>' in html
            assert '&lt;br /&gt;'in html
            assert '<h1>Happiness</h1>' in html
            assert '/_happiness' in html

    def test_renderer_negotiation_not_implemented(self):
        renderer = renderers.BaseRenderer()
        with pytest.raises(NotImplementedError) as exception:
            renderer.render(None, None)
        msg = str(exception.value)
        expected = '`render()` method must be implemented for class "BaseRenderer"'
        assert msg == expected


class OverrideParserSettings(unittest.TestCase):
    def setUp(self):
        class CustomRenderer1(renderers.BaseRenderer):
            media_type = 'application/example1'

            def render(self, data, media_type, **options):
                return 'custom renderer 1'

        class CustomRenderer2(renderers.BaseRenderer):
            media_type = 'application/example2'

            def render(self, data, media_type, **options):
                return 'custom renderer 2'

        app = FlaskAPI(__name__)
        app.config['DEFAULT_RENDERERS'] = [CustomRenderer1]
        app.config['PROPAGATE_EXCEPTIONS'] = True

        @app.route('/custom_renderer_1/', methods=['GET'])
        def custom_renderer_1():
            return {'data': 'example'}

        @app.route('/custom_renderer_2/', methods=['GET'])
        @set_renderers([CustomRenderer2])
        def custom_renderer_2():
            return {'data': 'example'}

        @app.route('/custom_renderer_2_as_args/', methods=['GET'])
        @set_renderers(CustomRenderer2)
        def custom_renderer_2_as_args():
            return {'data': 'example'}

        self.app = app

    def test_overridden_parsers_with_settings(self):
        with self.app.test_client() as client:
            response = client.get('/custom_renderer_1/')
            assert response.status_code == status.HTTP_200_OK
            assert response.headers['Content-Type'] == 'application/example1'
            data = response.get_data().decode('utf8')
            assert data == "custom renderer 1"

    def test_overridden_parsers_with_decorator(self):
        with self.app.test_client() as client:
            data = {'example': 'example'}
            response = client.get('/custom_renderer_2/', data=data)
            assert response.status_code == status.HTTP_200_OK
            assert response.headers['Content-Type'] == 'application/example2'
            data = response.get_data().decode('utf8')
            assert data == "custom renderer 2"

    def test_overridden_parsers_with_decorator_as_args(self):
        with self.app.test_client() as client:
            data = {'example': 'example'}
            response = client.get('/custom_renderer_2_as_args/', data=data)
            assert response.status_code == status.HTTP_200_OK
            assert response.headers['Content-Type'] == 'application/example2'
            data = response.get_data().decode('utf8')
            assert data == "custom renderer 2"
