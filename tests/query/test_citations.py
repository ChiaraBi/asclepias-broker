"""Test citation queries."""
import pytest

from asclepias_broker.datastore import Identifier
from collections import OrderedDict

from helpers import generate_payloads


TEST_CASES = [
    (
        'no_citations',
        [
            ['C', 'A', 'IsSupplementTo', 'B', '2018-01-01'],
        ],
        {
            'A': [set(), set()],
            'B': [set(), set()],
        }
    ),
    (
        'one_identity',
        [
            ['C', 'A', 'IsIdenticalTo', 'B', '2018-01-01'],
        ],
        {
            'A': [set(), set()],
            'B': [set(), set()],
        }
    ),
    (
        'two_identities',
        [
            ['C', 'A', 'IsIdenticalTo', 'B', '2018-01-01'],
            ['C', 'B', 'IsIdenticalTo', 'C', '2018-01-01'],
        ],
        {
            'A': [set(), set()],
            'B': [set(), set()],
            'C': [set(), set()],
        }
    ),
    (
        'one_citation',
        [
            ['C', 'A', 'Cites', 'B', '2018-01-01'],
        ],
        {
            'A': [set(), set()],
            'B': [{'A'}, {('A', 'B')}],
        }
    ),
    (
        'two_citations',
        [
            ['C', 'A', 'Cites', 'B', '2018-01-01'],
            ['C', 'C', 'Cites', 'B', '2018-01-01'],
        ],
        {
            'A': [set(), set()],
            'B': [{'A', 'C'}, {('A', 'B'), ('C', 'B')}],
            'C': [set(), set()],
        }
    ),
    (
        'one_indirect_citation',
        [
            ['C', 'A', 'IsIdenticalTo', 'B', '2018-01-01'],
            ['C', 'C', 'Cites', 'B', '2018-01-01'],
        ],
        {
            'A': [{'C'}, {('C', 'B')}],
            'B': [{'C'}, {('C', 'B')}],
            'C': [set(), set()],
        }
    ),
    (
        'two_indirect_citations',
        [
            ['C', 'A', 'IsIdenticalTo', 'B', '2018-01-01'],
            ['C', 'C', 'IsIdenticalTo', 'A', '2018-01-01'],
            ['C', 'X', 'Cites', 'B', '2018-01-01'],
            ['C', 'Y', 'Cites', 'C', '2018-01-01'],
        ],
        {
            'A': [{'X', 'Y'}, {('X', 'B'), ('Y', 'C')}],
            'B': [{'X', 'Y'}, {('X', 'B'), ('Y', 'C')}],
            'C': [{'X', 'Y'}, {('X', 'B'), ('Y', 'C')}],
            'X': [set(), set()],
            'Y': [set(), set()],
        }
    ),
    (
        'two_indirect_identical_citations',
        [
            ['C', 'A', 'IsIdenticalTo', 'B', '2018-01-01'],
            ['C', 'C', 'IsIdenticalTo', 'A', '2018-01-01'],
            ['C', 'X', 'Cites', 'B', '2018-01-01'],
            ['C', 'Y', 'Cites', 'C', '2018-01-01'],
            ['C', 'Y', 'IsIdenticalTo', 'X', '2018-01-01'],
        ],
        # NOTE: Since the `expand_target` is not called, this still counts two
        # unique citations.
        {
            'A': [{'X', 'Y'}, {('X', 'B'), ('Y', 'C')}],
            'B': [{'X', 'Y'}, {('X', 'B'), ('Y', 'C')}],
            'C': [{'X', 'Y'}, {('X', 'B'), ('Y', 'C')}],
            'X': [set(), set()],
            'Y': [set(), set()],
        }
    ),
]


@pytest.mark.parametrize(('test_case_name', 'events', 'results'), TEST_CASES)
def test_simple_citations(broker, test_case_name, events, results):
    """Test simple citation queries."""
    for ev in generate_payloads(events):
        broker.handle_event(ev)
    for cited_id_value, (citation_result, relation_result) in results.items():
        cited_id = (broker.session.query(Identifier)
                    .filter_by(value=cited_id_value).one())
        citations = set()
        relations = set()
        for citing_id, relation in broker.get_citations(cited_id):
            citations |= {i.value for i in citing_id}
            relations |= {(r.source.value, r.target.value) for r in relation}
        assert citations == citation_result
        assert relations == relation_result


TEST_CASES = [
    (
        'one_citation',
        [
            ['C', 'A', 'Cites', 'B', '2018-01-01'],
        ],
        {
            'A': [set(), set()],
            'B': [{'A'}, {('A', 'B')}],
        }
    ),
]
@pytest.mark.parametrize(('test_case_name', 'events', 'results'), TEST_CASES)
def test_grouping_query(broker, test_case_name, events, results):
    for ev in generate_payloads(events):
        broker.handle_event(ev)
    for cited_id_value, _ in results.items():
        ret = broker.get_citations2(cited_id_value)