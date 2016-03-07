# coding: utf8
from __future__ import unicode_literals
from flask import request, Flask, Blueprint
from flask._compat import reraise, string_types, text_type
from flask_api.exceptions import APIException
from flask_api.request import APIRequest
from flask_api.response import APIResponse
from flask_api.settings import APISettings
from itertools import chain
from werkzeug.exceptions import HTTPException
from werkzeug.routing import parse_rule
import coreapi
import re
import sys


api_resources = Blueprint(
    'flask-api', __name__,
    url_prefix='/flask-api',
    template_folder='templates', static_folder='static'
)


def dedent(content):
    """
    Remove leading indent from a block of text.
    Used when generating descriptions from docstrings.

    Note that python's `textwrap.dedent` doesn't quite cut it,
    as it fails to dedent multiline docstrings that include
    unindented text on the initial line.
    """
    #content = force_text(content)
    whitespace_counts = [len(line) - len(line.lstrip(' '))
                         for line in content.splitlines()[1:] if line.lstrip()]

    # unindent the content if needed
    if whitespace_counts:
        whitespace_pattern = '^' + (' ' * min(whitespace_counts))
        content = re.sub(re.compile(whitespace_pattern, re.MULTILINE), '', content)

    return content.strip()


def get_link(rule, method, func):
    """
    """
    url = ''
    path_params = set()
    for (converter, arguments, variable) in parse_rule(rule):
        if converter is None:
            url += variable
        else:
            url += '{' + variable + '}'
            path_params.add(variable)

    names = func.__code__.co_varnames[:func.__code__.co_argcount]

    num_optional = len(func.__defaults__ or [])
    num_required = len(names) - num_optional
    required_list = [
        True for idx in range(num_required)
    ] + [
        False for idx in range(num_optional)
    ]

    default_location = 'query' if method in ('GET', 'DELETE') else 'form'
    locations = [
        'path' if (name in path_params) else default_location
        for name in names
    ]

    link_description = ''
    field_descriptions = ['' for name in names]
    for line in dedent(func.__doc__).splitlines():
        if line.startswith('* '):
            name, desc = line.split('-', 1)
            field_descriptions.append(desc.strip())
        else:
            link_description += line + '\n'
    link_description = link_description.strip()

    fields = [
        coreapi.Field(name=name, required=required, location=location, description=description)
        for name, required, location, description
        in zip(names, required_list, locations, field_descriptions)
    ]
    return coreapi.Link(url, action=method, fields=fields, description=link_description)


class App(Flask):
    request_class = APIRequest
    response_class = APIResponse

    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.api_settings = APISettings(self.config)
        self.register_blueprint(api_resources)
        self.schema = {}

    def preprocess_request(self):
        request.parser_classes = self.api_settings.DEFAULT_PARSERS
        request.renderer_classes = self.api_settings.DEFAULT_RENDERERS
        return super(App, self).preprocess_request()

    def make_response(self, rv):
        """
        We override this so that we can additionally handle
        list and dict types by default.
        """
        status_or_headers = headers = None
        if isinstance(rv, tuple):
            rv, status_or_headers, headers = rv + (None,) * (3 - len(rv))

        if rv is None and status_or_headers:
            raise ValueError('View function did not return a response')

        if isinstance(status_or_headers, (dict, list)):
            headers, status_or_headers = status_or_headers, None

        if not isinstance(rv, self.response_class):
            if isinstance(rv, (text_type, bytes, bytearray, list, dict, coreapi.Document)):
                rv = self.response_class(rv, headers=headers, status=status_or_headers)
                headers = status_or_headers = None
            else:
                rv = self.response_class.force_type(rv, request.environ)

        if status_or_headers is not None:
            if isinstance(status_or_headers, string_types):
                rv.status = status_or_headers
            else:
                rv.status_code = status_or_headers
        if headers:
            rv.headers.extend(headers)

        return rv

    def handle_user_exception(self, e):
        """
        We override the default behavior in order to deal with APIException.
        """
        exc_type, exc_value, tb = sys.exc_info()
        assert exc_value is e

        if isinstance(e, HTTPException) and not self.trap_http_exception(e):
            return self.handle_http_exception(e)

        if isinstance(e, APIException):
            return self.handle_api_exception(e)

        blueprint_handlers = ()
        handlers = self.error_handler_spec.get(request.blueprint)
        if handlers is not None:
            blueprint_handlers = handlers.get(None, ())
        app_handlers = self.error_handler_spec[None].get(None, ())
        for typecheck, handler in chain(blueprint_handlers, app_handlers):
            if isinstance(e, typecheck):
                return handler(e)

        reraise(exc_type, exc_value, tb)

    def handle_api_exception(self, exc):
        return APIResponse({'message': exc.detail}, status=exc.status_code)

    def get(self, url, **options):
        return self.app_route(url, 'GET', **options)

    def post(self, url, **options):
        return self.app_route(url, 'POST', **options)

    def put(self, url, **options):
        return self.app_route(url, 'PUT', **options)

    def patch(self, url, **options):
        return self.app_route(url, 'PATCH', **options)

    def delete(self, url, **options):
        return self.app_route(url, 'DELETE', **options)

    def app_route(self, rule, method, **options):
        options['methods'] = [method]
        tag = options.pop('tag', None)
        def decorator(func):
            endpoint = options.pop('endpoint', func.__name__)
            link = get_link(rule, method, func)
            if tag:
                if tag not in self.schema:
                    self.schema[tag] = {}
                self.schema[tag][endpoint] = link
            else:
                self.schema[endpoint] = link

            def wrapper(*args, **kwargs):
                for field in link.fields:
                    if field.location == 'form':
                        if field.name in request.data:
                            kwargs[field.name] = request.data[field.name]
                    elif field.location == 'query':
                        if field.name in request.args:
                            kwargs[field.name] = request.args[field.name]
                return func(*args, **kwargs)

            self.add_url_rule(rule, endpoint, wrapper, **options)
            return func
        return decorator

    def run(self, *args, **kwargs):
        @self.route('/', methods=['GET'])
        def schema():
            from flask import request
            from flask_api.renderers import CoreJSONRenderer
            request.renderers = [CoreJSONRenderer()]
            return coreapi.Document(content=self.schema)
        super(App, self).run(*args, **kwargs)
