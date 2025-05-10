import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

# 导入主应用
from backend.main import app

# 创建测试客户端
client = TestClient(app)

# 模拟AnythingLLM API响应
@pytest.fixture
def mock_anythingllm_response():
    return {
        "text": "这是一个模拟的回复，用于测试聊天API。"
    }
    
    
    

# 测试聊天API端点
@patch("httpx.AsyncClient.post")
async def test_chat_endpoint(mock_post, mock_anythingllm_response):
    # 设置模拟响应
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_anythingllm_response
    mock_post.return_value = mock_response
    
    # 发送测试请求
    response = client.post(
        "/api/chat",
        json={"message": "你好，这是一个测试消息"}
    )
    
    # 验证响应
    assert response.status_code == 200
    assert "response" in response.json()
    assert response.json()["response"] == mock_anythingllm_response["text"]
    
    # 验证是否正确调用了AnythingLLM API
    mock_post.assert_called_once()

# 测试聊天API错误处理
@patch("httpx.AsyncClient.post")
async def test_chat_endpoint_error(mock_post):
    # 设置模拟错误响应
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response
    
    # 发送测试请求
    response = client.post(
        "/api/chat",
        json={"message": "这是一个会导致错误的消息"}
    )
    
    # 验证错误响应
    assert response.status_code == 500
    assert "detail" in response.json()
