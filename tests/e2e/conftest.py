"""
E2E测试的pytest配置文件
提供Playwright相关的fixture
"""
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser_type_launch_args():
    """配置浏览器启动参数"""
    return {
        "headless": True,  # 无头模式，适合CI环境
        "slow_mo": 0,      # 调试时可设置为非零值
    }

@pytest.fixture(scope="session")
def browser_context_args():
    """配置浏览器上下文参数"""
    return {
        "viewport": {
            "width": 1280,
            "height": 720,
        },
        "ignore_https_errors": True,
    }

@pytest.fixture(scope="session")
def playwright():
    """提供playwright实例"""
    with sync_playwright() as playwright:
        yield playwright

@pytest.fixture(scope="session")
def browser(playwright):
    """提供浏览器实例"""
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()

@pytest.fixture
def page(browser):
    """提供页面实例，这是E2E测试的主要fixture"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    page.close()
    context.close()
