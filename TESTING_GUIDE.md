# PsyChat Testing Guide

This guide outlines the testing strategy and implementation steps for the PsyChat application, covering backend, frontend, and integration testing.

## Testing Progression Strategy

The recommended progression for implementing and running tests is:

1. **Backend Tests** - Test API endpoints and business logic
2. **Integration Tests** - Test communication between frontend and backend
3. **Frontend Tests** - Test UI components and user interactions

## 1. Backend Testing

### Setup and Prerequisites

1. Navigate to the backend directory:
   ```bash
   cd e:\1_work\PersonalProgram\PsyChat\PsyChat0410\0421PysChat\backend
   ```

2. Install testing dependencies:
   ```bash
   pip install pytest pytest-cov httpx
   ```

3. Configure environment for testing (if not already done):
   ```bash
   cp .env.example .env.test
   # Edit .env.test with appropriate test settings
   ```

### Running Backend Tests

#### Option 1: Using run_test.py

The `run_test.py` script is already set up to run pytest tests:

```bash
python run_test.py
```

#### Option 2: Running pytest directly

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_resources.py

# Run with coverage report
pytest --cov=. tests/
```

### Expanding Backend Tests

You already have several test files:
- `test_resources.py` - Tests resource API endpoints
- `test_health_endpoint.py` - Tests health check endpoint
- `test_db_connection.py` - Tests database connection
- `test_chat.py` - Tests chat endpoints

To add new tests:

1. Create a new test file in the `tests/` directory, following the naming convention `test_*.py`
2. Implement test functions using pytest patterns
3. Add mocks for external dependencies (database, AnythingLLM API)

Example new test file for feedback API:

```python
# tests/test_feedback.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import the main application
from main import app

# Create test client
client = TestClient(app)

# Test feedback API endpoint
@patch("main.get_db_connection")
def test_submit_feedback(mock_get_db):
    # Mock database connection
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_db.return_value = mock_conn
    
    # Prepare test data
    feedback_data = {
        "message_id": "test-message-123",
        "session_id": "test-session-456",
        "user_query": "How to manage anxiety?",
        "bot_response": "Here are some tips for managing anxiety...",
        "rating": 1,
        "comment": "This was helpful"
    }
    
    # Send POST request to feedback endpoint
    response = client.post("/api/feedback", json=feedback_data)
    
    # Verify response
    assert response.status_code == 200
    assert "success" in response.json()
    
    # Verify database interaction
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

# Test feedback API with invalid data
def test_submit_feedback_invalid_data():
    # Missing required fields
    feedback_data = {
        "rating": 1
    }
    
    # Send POST request with invalid data
    response = client.post("/api/feedback", json=feedback_data)
    
    # Verify response shows validation error
    assert response.status_code == 422  # Unprocessable Entity
```

## 2. Integration Testing

Integration tests verify that the frontend and backend communicate correctly.

### Setup and Prerequisites

1. Ensure both backend and frontend development servers can run simultaneously
2. Install necessary tools:
   ```bash
   pip install playwright pytest-playwright
   playwright install
   ```

### Creating Integration Tests

Create a new directory for integration tests:

```bash
mkdir e:\1_work\PersonalProgram\PsyChat\PsyChat0410\0421PysChat\tests\integration
```

Example integration test:

```python
# tests/integration/test_chat_flow.py
import pytest
from playwright.sync_api import Page, expect
import time

# Base URLs for testing environments
FRONTEND_URL = "http://localhost:5173"  # Vite dev server
BACKEND_URL = "http://localhost:8000"   # Backend dev server

# Test the entire chat flow from UI to API and back
def test_chat_interaction(page: Page):
    # Go to the chat page
    page.goto(f"{FRONTEND_URL}/chat")
    
    # Type a message
    page.fill(".chat-input textarea", "Hello, I'm feeling anxious today")
    
    # Send the message
    page.click(".send-button")
    
    # Wait for response
    # For streaming response, we need to wait a bit longer
    page.wait_for_selector(".message.assistant", timeout=10000)
    
    # Verify response is displayed
    expect(page.locator(".message.assistant").last).to_be_visible()
    
    # Verify message content is non-empty
    message_text = page.locator(".message.assistant .message-content").last.text_content()
    assert message_text, "Bot response should not be empty"
    
    # Test feedback functionality
    page.click(".message.assistant .feedback-button[data-rating='1']")
    
    # Verify feedback confirmation is shown
    expect(page.locator(".feedback-confirmation")).to_be_visible()
```

### Running Integration Tests

```bash
# Run from project root
cd e:\1_work\PersonalProgram\PsyChat\PsyChat0410\0421PysChat
python -m pytest tests/integration/
```

## 3. Frontend Testing

### Setup and Prerequisites

1. Navigate to the frontend directory:
   ```bash
   cd e:\1_work\PersonalProgram\PsyChat\PsyChat0410\0421PysChat\frontend
   ```

2. Install testing dependencies (if not already in package.json):
   ```bash
   npm install --save-dev vitest @vue/test-utils jsdom
   ```

### Running Frontend Tests

You already have a configured Vitest setup and two test files:
- `ChatView.spec.js` - Tests the chat view component
- `ResourcePage.spec.js` - Tests the resource page component

To run tests:

```bash
# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### Expanding Frontend Tests

To add more frontend tests:

1. Create test files in `tests/unit/` following the naming convention `*.spec.js`
2. Test Vue components with Vue Test Utils
3. Mock API calls and external dependencies

Example new test for feedback component:

```javascript
// tests/unit/FeedbackButtons.spec.js
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import FeedbackButtons from '../../src/components/FeedbackButtons.vue'
import { ElMessage } from 'element-plus'

// Mock API service
vi.mock('../../src/services/api', () => ({
  default: {
    submitFeedback: vi.fn()
  }
}))

// Mock Element Plus
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      error: vi.fn()
    }
  }
})

describe('FeedbackButtons.vue', () => {
  let wrapper;
  
  beforeEach(() => {
    wrapper = mount(FeedbackButtons, {
      props: {
        messageId: 'msg-123',
        sessionId: 'session-456',
        userQuery: 'How to manage stress?',
        botResponse: 'Here are some tips...'
      }
    });
  });

  it('renders feedback buttons', () => {
    expect(wrapper.find('.feedback-buttons').exists()).toBe(true);
    expect(wrapper.find('[data-rating="1"]').exists()).toBe(true);
    expect(wrapper.find('[data-rating="0"]').exists()).toBe(true);
  });

  it('submits positive feedback when thumbs up is clicked', async () => {
    const api = require('../../src/services/api').default;
    api.submitFeedback.mockResolvedValue({ data: { success: true } });
    
    await wrapper.find('[data-rating="1"]').trigger('click');
    
    expect(api.submitFeedback).toHaveBeenCalledWith({
      message_id: 'msg-123',
      session_id: 'session-456',
      user_query: 'How to manage stress?',
      bot_response: 'Here are some tips...',
      rating: 1,
      comment: ''
    });
    
    expect(ElMessage.success).toHaveBeenCalled();
  });

  it('submits negative feedback when thumbs down is clicked', async () => {
    const api = require('../../src/services/api').default;
    api.submitFeedback.mockResolvedValue({ data: { success: true } });
    
    await wrapper.find('[data-rating="0"]').trigger('click');
    
    expect(api.submitFeedback).toHaveBeenCalledWith({
      message_id: 'msg-123',
      session_id: 'session-456',
      user_query: 'How to manage stress?',
      bot_response: 'Here are some tips...',
      rating: 0,
      comment: ''
    });
  });

  it('handles API errors gracefully', async () => {
    const api = require('../../src/services/api').default;
    api.submitFeedback.mockRejectedValue(new Error('API error'));
    
    await wrapper.find('[data-rating="1"]').trigger('click');
    
    expect(ElMessage.error).toHaveBeenCalled();
  });
});
```

Example test for streaming service:

```javascript
// tests/unit/streamingService.spec.js
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchEventSource } from '../../src/services/streamingService'

// Mock fetch API
global.fetch = vi.fn();
global.AbortController = vi.fn(() => ({
  signal: {},
  abort: vi.fn()
}));

describe('streamingService', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('calls fetch with correct parameters', async () => {
    // Setup mock implementation
    const mockReader = {
      read: vi.fn()
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: {"chunk":"Hello"}\n\n') })
        .mockResolvedValueOnce({ done: true })
    };
    
    global.fetch.mockResolvedValue({
      ok: true,
      body: {
        getReader: () => mockReader
      }
    });
    
    const url = '/api/chat/stream';
    const options = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'Hello' })
    };
    const callbacks = {
      onChunk: vi.fn(),
      onDone: vi.fn(),
      onError: vi.fn()
    };
    
    // Call the function
    await fetchEventSource(url, options, callbacks);
    
    // Verify fetch was called correctly
    expect(global.fetch).toHaveBeenCalledWith(url, {
      ...options,
      signal: expect.anything()
    });
    
    // Verify callback was called with chunk data
    expect(callbacks.onChunk).toHaveBeenCalledWith('Hello');
    expect(callbacks.onDone).toHaveBeenCalled();
  });

  it('handles fetch errors', async () => {
    global.fetch.mockRejectedValue(new Error('Network error'));
    
    const callbacks = {
      onChunk: vi.fn(),
      onDone: vi.fn(),
      onError: vi.fn()
    };
    
    await fetchEventSource('/api/chat/stream', {}, callbacks);
    
    expect(callbacks.onError).toHaveBeenCalledWith(expect.any(Error));
  });
});
```

## 4. Creating a Complete Test Script

To run all tests in sequence, create a master test script:

```bash
#!/bin/bash
# test_all.sh

echo "=== RUNNING BACKEND TESTS ==="
cd backend
python -m pytest tests/

echo "=== RUNNING FRONTEND TESTS ==="
cd ../frontend
npm test

echo "=== RUNNING INTEGRATION TESTS ==="
cd ..
python -m pytest tests/integration/

echo "All tests completed."
```

Make it executable:
```bash
chmod +x test_all.sh
```

## 5. Continuous Integration Setup

For GitHub Actions CI, create a workflow file:

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          cd backend
          pytest tests/

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm test

  integration-tests:
    needs: [backend-tests, frontend-tests]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python and Node.js
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install Playwright
        run: |
          pip install playwright pytest-playwright
          playwright install
      - name: Start backend and frontend
        run: |
          # Start backend and frontend services
          # This would need to be customized based on your project setup
      - name: Run integration tests
        run: |
          python -m pytest tests/integration/
```

## Best Practices

1. **Isolate Tests**: Each test should be independent and not rely on the state of other tests.
2. **Mock External Dependencies**: Use mocks for databases, APIs, and any external services.
3. **Test Critical Paths First**: Focus on the core functionality before testing edge cases.
4. **Regular Test Runs**: Run tests frequently during development, not just before deployment.
5. **Coverage Monitoring**: Track code coverage to identify untested areas.
6. **Test Real User Flows**: Integration tests should simulate actual user behaviors.
7. **Keep Tests Fast**: Slow tests discourage frequent running.

## Troubleshooting Common Issues

### Backend Tests
- **Database Connection Issues**: Ensure test database is configured correctly in `.env.test`
- **Import Errors**: Check your Python path and make sure imports use the correct paths
- **Mock Configuration**: Verify that mocks are properly set up for external dependencies

### Frontend Tests
- **Component Mounting Errors**: Make sure all required props are provided
- **Event Handling**: Await event triggers when testing asynchronous behavior
- **API Mocking**: Ensure API mocks return data in the expected format

### Integration Tests
- **Timing Issues**: Use appropriate waits and expect conditions rather than fixed timeouts
- **Environment Setup**: Verify both frontend and backend services are running correctly
- **Selector Changes**: Update selectors in tests when UI elements change
