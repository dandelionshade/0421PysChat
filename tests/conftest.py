"""
Pytest配置和通用fixture
"""
import os
import pytest
from dotenv import load_dotenv

# 自动加载测试环境变量
load_dotenv('.env.test', override=True)

# 这里可以添加各种测试所需的fixtures
@pytest.fixture
def test_client():
    """创建测试用的FastAPI测试客户端"""
    # 导入需在fixture内部进行，避免循环导入
    from fastapi.testclient import TestClient
    from backend.main import app
    
    client = TestClient(app)
    yield client

@pytest.fixture
def mock_anythingllm_api():
    """模拟AnythingLLM API响应的fixture"""
    # 实现模拟逻辑
    pass
