import pytest

from tidypolars4sci.io import DATA_LABELS


@pytest.fixture
def labels():
    return DATA_LABELS(
        original=['status', 'age'],
        variables={'status': 'Employment', 'age': 'Age in years'},
        values={'status': {1: 'Working', 2: 'Retired'}},
        types={},
    )


def test_search_both_default(labels, capsys):
    assert labels.search('years|retired', out='dict') == {
        'variables': {'age': 'Age in years'},
        'values': {'status': {2: 'Retired'}},
    }
    assert capsys.readouterr().out == ''
    assert labels.search('years|retired') is None
    printed = capsys.readouterr().out
    assert 'Age in years' in printed
    assert '2: Retired' in printed


@pytest.mark.parametrize('regex', ['^status$', '^employment$'])
def test_search_variable_names_and_labels(labels, regex):
    assert labels.search(regex, include_values=False, out='dict') == {
        'status': 'Employment',
    }
    assert labels.search(regex, out='dict')['values'] == labels.values


@pytest.mark.parametrize('regex', ['^2$', '^retired$'])
def test_search_value_codes_and_labels(labels, regex):
    assert labels.search(regex, out='dict')['values'] == {
        'status': {2: 'Retired'},
    }


def test_search_case_sensitive_and_no_matches(labels):
    assert labels.search('retired', out='dict', case_sensitive=True) == {
        'variables': {}, 'values': {},
    }
    assert labels.search('missing', include_values=False, out='dict') == {}
    assert labels.search('Working', out='dict')['values'] == {
        'status': {1: 'Working'},
    }


@pytest.mark.parametrize('kwargs', [{'include_values': 'invalid'}, {'out': 'invalid'}])
def test_search_rejects_invalid_modes(labels, kwargs):
    with pytest.raises(AssertionError):
        labels.search('anything', **kwargs)


def test_print_groups_values_under_variable(labels, capsys):
    labels.search('status')
    assert capsys.readouterr().out == (
        'status       : Employment\n'
        '               Values:\n'
        '               1: Working\n'
        '               2: Retired\n\n'
    )
    labels.search('status', include_values=False)
    assert capsys.readouterr().out == 'status       : Employment\n\n'
    assert labels.search('Retired', include_values=False, out='dict') == {}


def test_print_value_only_match_has_variable_heading(labels, capsys):
    labels.search('Retired')
    assert capsys.readouterr().out == (
        'status       : Employment\n'
        '               Values:\n'
        '               2: Retired\n\n'
    )


def test_print_wraps_value_labels(labels, capsys):
    labels.values['status'] = {1: 'A long value label'}
    labels.search('status', label_trunc=10)
    assert '               1: A long\n                  value\n                  label\n' in capsys.readouterr().out
    labels.search('status', label_trunc=10, full_label=False)
    assert '               1: A long val\n' in capsys.readouterr().out
