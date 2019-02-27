from pylaut.language.phonology import featureset


def test_load_from_package():
    f = featureset.FeatureModel('monophone')
    assert f.features == [
        'syllabic', 'consonantal', 'continuant', 'sonorant', 'nasal', 'labial',
        'dental', 'apical', 'coronal', 'dorsal', 'voice', 'trill', 'flap',
        'lateral', 'pharyngeal', 'glottal', 'front', 'back', 'high', 'low',
        'round', 'tense', 'breathy', 'aspirated', 'long', 'sibilant'
    ]


def test_load_from_folder():
    f = featureset.FeatureModel('monophone', 'pylaut/data')
    assert f.features == [
        'syllabic', 'consonantal', 'continuant', 'sonorant', 'nasal', 'labial',
        'dental', 'apical', 'coronal', 'dorsal', 'voice', 'trill', 'flap',
        'lateral', 'pharyngeal', 'glottal', 'front', 'back', 'high', 'low',
        'round', 'tense', 'breathy', 'aspirated', 'long', 'sibilant'
    ]


def test_features_from_ipa_string():
    f = featureset.FeatureModel('monophone')
    esh = f.get_features_from_ipa('ʃ')
    esh_ph = f.get_features_from_ipa('ʃˤ')
    assert esh == [
        '-', '+', '+', '-', '-', '-', '-', '-', '+', '-', '-', '-', '-', '-',
        '-', '-', '-', '+', '0', '0', '-', '0', '-', '0', '-', '+'
    ]
    assert esh_ph == [
        '-', '+', '+', '-', '-', '-', '-', '-', '+', '-', '-', '-', '-', '-',
        '+', '-', '-', '+', '0', '0', '-', '0', '-', '0', '-', '+'
    ]


def test_ipa_from_features():

    f = featureset.FeatureModel('monophone')
    esh_f = [
        '-', '+', '+', '-', '-', '-', '-', '+', '-', '-', '-', '-', '-', '-',
        '-', '-', '-', '-', '0', '0', '-', '0', '-', '0', '-', '+'
    ]
    esh_ph_f = [
        '-', '+', '+', '-', '-', '-', '-', '+', '-', '-', '-', '-', '-', '-',
        '+', '-', '-', '-', '0', '0', '-', '0', '-', '0', '-', '+'
    ]
    esh = f.get_ipa_from_features(esh_f)
    esh_ph = f.get_ipa_from_features(esh_ph_f)

    assert esh == 'ʂ'
    assert esh_ph == 'ʂˤ'
