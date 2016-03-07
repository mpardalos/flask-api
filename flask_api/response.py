# coding: utf8
from __future__ import unicode_literals
from coreapi import Document
from flask import request, Response
from flask._compat import string_types


class APIResponse(Response):
    def __init__(self, content=None, *args, **kwargs):
        super(APIResponse, self).__init__(None, *args, **kwargs)

        media_type = None
        if isinstance(content, (Document, list, dict, string_types)):
            renderer = request.renderer
            if content != '':
                context = {'request': request, 'response': self}
                content = renderer(content, **context)

        if isinstance(content, (string_types, bytes, bytearray)):
            self.set_data(content)
        else:
            self.response = content

        if renderer and renderer.media_type:
            self.headers['Content-Type'] = str(renderer.media_type)
