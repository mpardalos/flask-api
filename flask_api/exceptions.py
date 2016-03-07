from __future__ import unicode_literals
from flask_api import status


class APIException(Exception):
    status_code = 500
    detail = ''

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = detail

    def __str__(self):
        return self.detail


class ParseError(APIException):
    status_code = 400
    detail = 'Malformed request.'


class AuthenticationFailed(APIException):
    status_code = 401
    detail = 'Incorrect authentication credentials.'


class NotAuthenticated(APIException):
    status_code = 401
    detail = 'Authentication credentials were not provided.'


class PermissionDenied(APIException):
    status_code = 403
    detail = 'You do not have permission to perform this action.'


class NotFound(APIException):
    status_code = 404
    detail = 'This resource does not exist.'


class MethodNotAllowed(APIException):
    status_code = 405
    detail = 'Request method not allowed.'


class NotAcceptable(APIException):
    status_code = 406
    detail = 'Could not satisfy the request Accept header.'


class UnsupportedMediaType(APIException):
    status_code = 415
    detail = 'Unsupported media type in the request Content-Type header.'


class Throttled(APIException):
    status_code = 429
    detail = 'Request was throttled.'
