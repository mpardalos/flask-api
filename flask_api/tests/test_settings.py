# coding: utf8
from __future__ import unicode_literals
from flask_api.settings import APISettings
import unittest
import pytest


class SettingsTests(unittest.TestCase):
    def test_bad_import(self):
        settings = APISettings({'DEFAULT_PARSERS': 'foobarz.FailedImport'})
        with pytest.raises(ImportError) as exception:
            settings.DEFAULT_PARSERS
        msg = str(exception.value)
        excepted_py2 = (
            "Could not import 'foobarz.FailedImport' for API setting "
            "'DEFAULT_PARSERS'. No module named foobarz."
        )
        excepted_py3 = (
            "Could not import 'foobarz.FailedImport' for API setting "
            "'DEFAULT_PARSERS'. No module named 'foobarz'."
        )
        assert msg in (excepted_py2, excepted_py3)
