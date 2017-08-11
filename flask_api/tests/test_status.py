# coding: utf8
from __future__ import unicode_literals
from flask_api import status
import unittest


class TestStatus(unittest.TestCase):
    def test_status_categories(self):
        assert not status.is_informational(99)
        assert status.is_informational(100)
        assert status.is_informational(199)
        assert not status.is_informational(200)

        assert not status.is_success(199)
        assert status.is_success(200)
        assert status.is_success(299)
        assert not status.is_success(300)

        assert not status.is_redirect(299)
        assert status.is_redirect(300)
        assert status.is_redirect(399)
        assert not status.is_redirect(400)

        assert not status.is_client_error(399)
        assert status.is_client_error(400)
        assert status.is_client_error(499)
        assert not status.is_client_error(500)

        assert not status.is_server_error(499)
        assert status.is_server_error(500)
        assert status.is_server_error(599)
        assert not status.is_server_error(600)
