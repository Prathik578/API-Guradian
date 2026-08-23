"""Unit tests for Stripe provider."""

import json
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from api_guardian.domain.provider_change import ChangeClassification, EvidenceSource
from api_guardian.providers.stripe.adapter import StripeOpenAPIAdapter
from api_guardian.providers.stripe.detector import StripeChangeDetector
from api_guardian.providers.stripe.errors import StripeRateLimitError
from api_guardian.providers.stripe.interpreter import StripeChangeInterpreter


@pytest.fixture
def baseline_spec():
    path = Path("tests/fixtures/providers/stripe/raw/spec3_baseline.json")
    return json.loads(path.read_text())


@pytest.fixture
def changed_spec():
    path = Path("tests/fixtures/providers/stripe/raw/spec3_changed.json")
    return json.loads(path.read_text())


def test_source_acquisition_success():
    adapter = StripeOpenAPIAdapter()
    
    # Mock httpx.Client.stream
    class MockResponse:
        status_code: int = 200
        
        def __init__(self):
            self.headers = {"content-type": "application/json", "ETag": "w/1234"}
            
        def iter_bytes(self):
            yield b'{"openapi": "3.0.0"}'
            
        def __enter__(self):
            return self
            
        def __exit__(self, *args):
            pass

    class MockClient:
        def stream(self, *args, **kwargs):
            return MockResponse()
            
        def __enter__(self):
            return self
            
        def __exit__(self, *args):
            pass

    with patch("httpx.Client", return_value=MockClient()):
        source = adapter.acquire_source()
        
    assert source.content == b'{"openapi": "3.0.0"}'
    assert source.source_key == "openapi/spec3"
    assert source.content_type == "application/json"
    assert source.source_revision == "w/1234"


def test_source_acquisition_429():
    adapter = StripeOpenAPIAdapter()
    
    class MockResponse:
        status_code: int = 429
        
        def __init__(self):
            self.headers = {"Retry-After": "45"}
            
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
            
    class MockClient:
        def stream(self, *args, **kwargs):
            return MockResponse()
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    with patch("httpx.Client", return_value=MockClient()):
        with pytest.raises(StripeRateLimitError) as exc:
            adapter.acquire_source()
        assert exc.value.retry_after == 45


def test_change_detection_no_previous(baseline_spec):
    detector = StripeChangeDetector()
    changes = detector.detect_changes(baseline_spec, None, uuid.uuid4(), None)
    assert changes == []  # Baseline


def test_change_detection_endpoint_removed_and_deprecated(baseline_spec, changed_spec):
    detector = StripeChangeDetector()
    curr_id = uuid.uuid4()
    prev_id = uuid.uuid4()
    
    changes = detector.detect_changes(changed_spec, baseline_spec, curr_id, prev_id)
    
    # Expected: /v1/tokens removed, POST /v1/charges/{charge}/capture deprecated, Charge.source deprecated
    assert len(changes) == 3
    
    change_types = {c.change_type for c in changes}
    assert "endpoint_removed" in change_types
    assert "endpoint_deprecated" in change_types
    assert "field_deprecated" in change_types
    
    for change in changes:
        assert change.evidence_source == EvidenceSource.OBSERVED_SCHEMA_CHANGE


def test_change_detection_no_changes(baseline_spec):
    detector = StripeChangeDetector()
    curr_id = uuid.uuid4()
    prev_id = uuid.uuid4()
    changes = detector.detect_changes(baseline_spec, baseline_spec, curr_id, prev_id)
    assert len(changes) == 0


def test_interpreter_classification(baseline_spec, changed_spec):
    detector = StripeChangeDetector()
    curr_id = uuid.uuid4()
    prev_id = uuid.uuid4()
    
    changes = detector.detect_changes(changed_spec, baseline_spec, curr_id, prev_id)
    interpreter = StripeChangeInterpreter()
    
    prov_changes = [interpreter.interpret_change(c) for c in changes]
    assert len(prov_changes) == 3
    
    classes = {p.classification for p in prov_changes}
    assert ChangeClassification.BREAKING_BEHAVIOR in classes
    assert ChangeClassification.DEPRECATION in classes
    
    # Dates should not be invented
    for pc in prov_changes:
        assert pc.effective_date is None
        assert pc.sunset_date is None
        assert pc.provider_native_id is not None


def test_canonical_identity_determinism():
    interpreter = StripeChangeInterpreter()
    id1 = interpreter.compute_canonical_change_id("stripe", "endpoint_removed", "/v1/tokens")
    id2 = interpreter.compute_canonical_change_id("stripe", "endpoint_removed", "/v1/tokens")
    assert id1 == id2
    
    id3 = interpreter.compute_canonical_change_id("stripe", "endpoint_removed", "/v1/charges")
    assert id1 != id3
