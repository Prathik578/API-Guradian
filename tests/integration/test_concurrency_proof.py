"""Phase 20F: Distributed Concurrency Proof."""

import threading
import time
import uuid
from typing import Any, cast

import pytest

from api_guardian.domain.quotas import ResourcePolicy
from api_guardian.domain import TenantContext
from api_guardian.persistence.database import DatabaseManager, db_manager
from api_guardian.persistence.models.base import Base
from api_guardian.platform.llm.resilient_gateway import ResilientLLMGateway
from api_guardian.platform.quotas.manager import QuotaManager

try:
    from testcontainers.postgres import PostgresContainer
    HAS_TESTCONTAINERS = True
except ImportError:
    HAS_TESTCONTAINERS = False


@pytest.fixture(scope="module")
def postgres_db() -> Any:
    if not HAS_TESTCONTAINERS:
        pytest.skip("Testcontainers not available")
        
    with PostgresContainer("postgres:15-alpine") as postgres:
        db_url = postgres.get_connection_url().replace("+psycopg2", "")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        db_manager.engine = create_engine(db_url, pool_size=20, max_overflow=40)
        db_manager.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_manager.engine)
        
        Base.metadata.create_all(db_manager.engine)
        yield db_manager


@pytest.mark.skipif(not HAS_TESTCONTAINERS, reason="Requires testcontainers-python")
def test_circuit_breaker_concurrency(postgres_db: Any) -> None:
    """Proves that multiple concurrent workers correctly transition Circuit Breaker."""
    
    tenant_id = uuid.uuid4()
    ctx = TenantContext(tenant_id=tenant_id)
    
    # We will simulate 10 workers failing simultaneously. 
    # The breaker is configured to OPEN after 3 failures.
    class MockLLMGateway:
        def __init__(self, should_fail: bool = True) -> None:
            self.should_fail = should_fail
            self.calls = 0
            
        def generate_completion(self, role: Any, prompt_envelope: Any, max_tokens: Any = None) -> Any:
            self.calls += 1
            if self.should_fail:
                raise RuntimeError("LLM Failure")
            return "response", 10, 10
            
        def generate_structured(self, role: Any, prompt_envelope: Any, schema_cls: Any, max_tokens: Any = None) -> Any:
            return {}, 10, 10

    gateways = [ResilientLLMGateway(cast(Any, MockLLMGateway(should_fail=True))) for _ in range(10)]
    
    results: list[Any] = [None] * 10
    
    def worker(idx: int) -> None:
        gateway = gateways[idx]
        try:
            gateway.generate_completion(cast(Any, None), "prompt", max_tokens=100)
            results[idx] = "SUCCESS"
        except RuntimeError as e:
            results[idx] = str(e)
        except Exception as e:
            results[idx] = str(e)
            
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    # Due to concurrent execution and retries, exact exception strings can vary between:
    # "LLM Gateway exhausted retries"
    # "LLM circuit opened during retry loop"
    # "LLM Gateway circuit is OPEN"
    # However, the circuit breaker should limit the total number of underlying LLM calls
    # across ALL threads to exactly the failure threshold (5) plus maybe a few concurrent
    # inflight requests before the lock was acquired.
    
    total_calls = sum(cast(Any, g.underlying).calls for g in gateways)
    
    # 10 threads doing up to 4 attempts each would normally be 40 calls.
    # The circuit breaker (threshold=5) should cap this significantly.
    assert total_calls < 15, f"Circuit breaker failed to restrict calls. Total calls: {total_calls}"
    
    # Ensure at least some workers were rejected by the circuit breaker immediately or during retry
    cb_fails = sum(1 for r in results if "circuit open" in str(r).lower() or "is open" in str(r).lower())
    assert cb_fails > 0, f"Expected some fast-failures, got results: {results}"


@pytest.mark.skipif(not HAS_TESTCONTAINERS, reason="Requires testcontainers-python")
def test_quota_manager_concurrency(postgres_db: Any) -> None:
    """Proves that multiple concurrent workers respect quota limits transactionally."""
    
    tenant_id = uuid.uuid4()
    ctx = TenantContext(tenant_id=tenant_id)
    
    # Custom policy: only 2 concurrent migrations allowed (mocked via limit injection)
    # We'll monkeypatch the limit lookup in QuotaManager to use a local variable
    original_getattr = getattr
    import builtins
    def mock_getattr(obj: Any, name: str, default: Any = None) -> Any:
        if name == "max_concurrent_migrations":
            return 2
        return original_getattr(obj, name, default)

    import builtins
    results: list[Any] = [None] * 5
    leases: list[Any] = [None] * 5
    
    def worker(idx: int) -> None:
        try:
            builtins.getattr = mock_getattr
            lease_id = QuotaManager.acquire_tenant_lease(tenant_id, "concurrent_migrations", f"worker-{idx}", duration_sec=5)
            leases[idx] = lease_id
            results[idx] = "ACQUIRED"
        except RuntimeError as e:
            if "Quota exceeded" in str(e):
                results[idx] = "REJECTED"
            else:
                results[idx] = str(e)
        except Exception as e:
            results[idx] = str(e)
        finally:
            builtins.getattr = original_getattr
            
    threads = []
    # Launch 5 workers attempting to acquire lease at the exact same time
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    builtins.getattr = original_getattr
    
    # Exactly 2 should acquire, 3 should reject
    acquired = results.count("ACQUIRED")
    rejected = results.count("REJECTED")
    
    assert acquired == 2, f"Expected 2 successful lease acquisitions, got {acquired}. Results: {results}"
    assert rejected == 3, f"Expected 3 rejections, got {rejected}. Results: {results}"
    
    # Release the acquired leases to clean up
    for lease_id in leases:
        if lease_id:
            QuotaManager.release_lease(tenant_id, lease_id)
            
    # Now wait for expiration behavior on a new lease
    def worker_expire(idx: int, dur: int) -> Any:
        builtins.getattr = mock_getattr
        try:
            return QuotaManager.acquire_tenant_lease(tenant_id, "concurrent_migrations", f"worker-{idx}", duration_sec=dur)
        finally:
            builtins.getattr = original_getattr
            
    l1 = worker_expire(10, 1) # 1 sec TTL
    
    builtins.getattr = mock_getattr
    with pytest.raises(RuntimeError, match="Quota exceeded"):
        # We have 1 active (limit is 2) but let's try to acquire 2 more (total 3)
        QuotaManager.acquire_tenant_lease(tenant_id, "concurrent_migrations", "w1", duration_sec=5) # should succeed (2/2)
        QuotaManager.acquire_tenant_lease(tenant_id, "concurrent_migrations", "w2", duration_sec=5) # should fail (3/2)
    builtins.getattr = original_getattr
        
    time.sleep(1.5)
    
    # The first 1-second lease should be expired logically by QuotaManager when we call acquire
    # Let's try acquiring again
    builtins.getattr = mock_getattr
    try:
        QuotaManager.acquire_tenant_lease(tenant_id, "concurrent_migrations", "w3", duration_sec=5)
    except RuntimeError as e:
        if "Quota exceeded" in str(e):
            pytest.fail("QuotaManager did not logically ignore the expired lease")
    finally:
        builtins.getattr = original_getattr
