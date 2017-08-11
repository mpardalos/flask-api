# coding: utf8
from __future__ import unicode_literals
from flask_api.mediatypes import MediaType, parse_accept_header
import unittest


class MediaTypeParsingTests(unittest.TestCase):
    def test_media_type_with_params(self):
        media = MediaType('application/xml; schema=foobar, q=0.5')
        assert str(media) == 'application/xml; q="0.5", schema="foobar"'
        assert media.main_type == 'application'
        assert media.sub_type == 'xml'
        assert media.full_type == 'application/xml'
        assert media.params == {'schema': 'foobar', 'q': '0.5'}
        assert media.precedence == 3
        assert repr(media) == '<MediaType \'application/xml; q="0.5", schema="foobar"\'>'

    def test_media_type_with_q_params(self):
        media = MediaType('application/xml; q=0.5')
        assert str(media) == 'application/xml; q="0.5"'
        assert media.main_type == 'application'
        assert media.sub_type == 'xml'
        assert media.full_type == 'application/xml'
        assert media.params == {'q': '0.5'}
        assert media.precedence == 2

    def test_media_type_without_params(self):
        media = MediaType('application/xml')
        assert str(media) == 'application/xml'
        assert media.main_type == 'application'
        assert media.sub_type == 'xml'
        assert media.full_type == 'application/xml'
        assert media.params == {}
        assert media.precedence == 2

    def test_media_type_with_wildcard_sub_type(self):
        media = MediaType('application/*')
        assert str(media) == 'application/*'
        assert media.main_type == 'application'
        assert media.sub_type == '*'
        assert media.full_type == 'application/*'
        assert media.params == {}
        assert media.precedence == 1

    def test_media_type_with_wildcard_main_type(self):
        media = MediaType('*/*')
        assert str(media) == '*/*'
        assert media.main_type == '*'
        assert media.sub_type == '*'
        assert media.full_type == '*/*'
        assert media.params == {}
        assert media.precedence == 0


class MediaTypeMatchingTests(unittest.TestCase):
    def test_media_type_includes_params(self):
        media_type = MediaType('application/json')
        other = MediaType('application/json; version=1.0')
        assert media_type.satisfies(other)

    def test_media_type_missing_params(self):
        media_type = MediaType('application/json; version=1.0')
        other = MediaType('application/json')
        assert not media_type.satisfies(other)

    def test_media_type_matching_params(self):
        media_type = MediaType('application/json; version=1.0')
        other = MediaType('application/json; version=1.0')
        assert media_type.satisfies(other)

    def test_media_type_non_matching_params(self):
        media_type = MediaType('application/json; version=1.0')
        other = MediaType('application/json; version=2.0')
        assert not media_type.satisfies(other)

    def test_media_type_main_type_match(self):
        media_type = MediaType('image/*')
        other = MediaType('image/png')
        assert media_type.satisfies(other)

    def test_media_type_sub_type_mismatch(self):
        media_type = MediaType('image/jpeg')
        other = MediaType('image/png')
        assert not media_type.satisfies(other)

    def test_media_type_wildcard_match(self):
        media_type = MediaType('*/*')
        other = MediaType('image/png')
        assert media_type.satisfies(other)

    def test_media_type_wildcard_mismatch(self):
        media_type = MediaType('image/*')
        other = MediaType('audio/*')
        assert not media_type.satisfies(other)


class AcceptHeaderTests(unittest.TestCase):
    def test_parse_simple_accept_header(self):
        parsed = parse_accept_header('*/*, application/json')
        assert parsed == [
            set([MediaType('application/json')]),
            set([MediaType('*/*')])
        ]

    def test_parse_complex_accept_header(self):
        """
        The accept header should be parsed into a list of sets of MediaType.
        The list is an ordering of precedence.

        Note that we disregard 'q' values when determining precedence, and
        instead differentiate equal values by using the server preference.
        """
        header = 'application/xml; schema=foo, application/json; q=0.9, application/xml, */*'
        parsed = parse_accept_header(header)
        assert parsed == [
            set([MediaType('application/xml; schema=foo')]),
            set([MediaType('application/json; q=0.9'), MediaType('application/xml')]),
            set([MediaType('*/*')]),
        ]
