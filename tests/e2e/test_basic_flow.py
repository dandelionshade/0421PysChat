import pytest
from playwright.sync_api import Page, expect

# Base URLs for testing
FRONTEND_URL = "http://localhost:5173"  # Default for Vite
BACKEND_URL = "http://localhost:8000"   # Your backend

def test_homepage_loads(page: Page):
    """Test that the homepage loads successfully"""
    page.goto(FRONTEND_URL)
    
    # Verify the page title is present
    expect(page).to_have_title(/PsyChat|Mental Health|Psychology/)
    
    # Verify the chat interface is visible
    chat_interface = page.locator(".chat-container")
    expect(chat_interface).to_be_visible()

def test_send_message_and_get_response(page: Page):
    """Test sending a message and receiving a response"""
    # Go to the chat page
    page.goto(f"{FRONTEND_URL}/chat")
    
    # Wait for page to be fully loaded
    page.wait_for_selector(".chat-input")
    
    # Type a message and send it
    page.fill(".chat-input textarea", "Hello, I'm feeling anxious today")
    page.click(".send-button")
    
    # Wait for the bot's response
    page.wait_for_selector(".message.assistant", timeout=15000)
    
    # Verify bot response is received
    bot_message = page.locator(".message.assistant").last
    expect(bot_message).to_be_visible()
    
    # Verify the response is not empty
    message_text = page.locator(".message.assistant .message-content").last
    expect(message_text).not_to_be_empty()

def test_feedback_functionality(page: Page):
    """Test the feedback functionality"""
    # First send a message to get a response
    page.goto(f"{FRONTEND_URL}/chat")
    page.fill(".chat-input textarea", "What are some relaxation techniques?")
    page.click(".send-button")
    page.wait_for_selector(".message.assistant", timeout=15000)
    
    # Click the positive feedback button
    feedback_button = page.locator(".message.assistant .feedback-buttons [data-rating='1']").last
    feedback_button.click()
    
    # Verify feedback confirmation message appears
    page.wait_for_selector(".feedback-confirmation")
    expect(page.locator(".feedback-confirmation")).to_be_visible()

def test_session_management(page: Page):
    """Test session creation and management"""
    page.goto(f"{FRONTEND_URL}/chat")
    
    # Open session manager
    page.click(".session-manager-button")
    
    # Create a new session
    page.click(".create-session-button")
    page.fill(".session-name-input", "Test Automation Session")
    page.click(".confirm-create-button")
    
    # Verify the new session appears in the list
    session_item = page.locator(".session-list-item:has-text('Test Automation Session')")
    expect(session_item).to_be_visible()
    
    # Select the session
    session_item.click()
    
    # Send a message in this session
    page.fill(".chat-input textarea", "This is a message in my new session")
    page.click(".send-button")
    
    # Verify response is received
    page.wait_for_selector(".message.assistant", timeout=15000)
    expect(page.locator(".message.assistant").last).to_be_visible()
