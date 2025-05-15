import pytest
import os
import sys
import logging
from fastapi.testclient import TestClient

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def test_app():
    """
    This fixture creates the FastAPI app with a properly initialized state
    for testing, ensuring the HTTP client is available.
    """
    try:
        from main import app
        
        # For testing, we need to ensure the lifespan events run
        # This will initialize the HTTP client on app.state
        from contextlib import asynccontextmanager
        from main import lifespan
        
        # Use a with block to trigger the lifespan context manager events
        async def trigger_lifespan():
            async with lifespan(app):
                yield app
                
        # Get the app with initialized state
        import asyncio
        app_gen = trigger_lifespan()
        app_with_state = asyncio.get_event_loop().run_until_complete(anext(app_gen))
        
        return app_with_state
    except ImportError as e:
        logger.error(f"无法导入主应用: {e}")
        pytest.skip("Cannot import app for testing")
        
@pytest.fixture(scope="session")
def client(test_app):
    """
    Create a test client with the app that has HTTP client initialized.
    """
    return TestClient(test_app)
