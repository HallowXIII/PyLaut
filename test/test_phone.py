"""
Test of Phone module.
This mostly checks for compliance with the
old interface at the moment.
"""


import pytest
from pylaut.language.phonology import phone as ph, featureset


@pytest.fixture
def phone():
    fm = featureset.FeatureModel('monophone')
    return ph.Phone(fm, 'e')


def test_clear_features(phone):
    phone.clear_features()


def test_copy(phone):
    phone.copy()


def test_feature_is(phone):
    phone.feature_is('consonantal', '0')


def test_feature_is_false(phone):
    phone.feature_is_false('consonantal')


def test_feature_is_null(phone):
    phone.feature_is_null('consonantal')


def test_feature_is_true(phone):
    phone.feature_is_true('consonantal')


def test_get_feature_list(phone):
    phone.get_feature_list()


def test_is_symbol(phone):
    phone.is_symbol('a')


def test_print_feature_list(phone):
    phone.print_feature_list()


def test_set_feature(phone):
    phone.set_feature('consonantal', '+')


def test_set_features_bool(phone):
    phone.set_features_bool('consonantal', '-')


def test_set_features_false(phone):
    phone.set_features_false('voice')


def test_set_features_from_ipa(phone):
    phone.set_features_from_ipa('a')


def test_set_features_null(phone):
    phone.set_features_null('consonantal')


def test_set_features_true(phone):
    phone.set_features_true('voice')


def test_set_symbol_from_features(phone):
    phone.set_symbol_from_features()
