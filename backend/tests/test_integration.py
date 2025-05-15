import os
import sys
import json
import pytest
import httpx  # Add httpx import
from unittest.mock import MagicMock, patch
import logging
from dotenv import load_dotenv

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加父目录到路径以便导入主应用
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
load_dotenv()

# 集成测试标记
pytestmark = pytest.mark.integration

# Setup test client with proper lifespan handling
@pytest.fixture
def test_client():
    """Create a test client that properly handles the lifespan context."""
    from fastapi.testclient import TestClient
    from main import app
    
    # Create the test client
    with TestClient(app) as client:
        # Manually initialize http_client for tests
        import httpx
        app.state.http_client = httpx.AsyncClient()
        yield client
        # Clean up the http_client after tests
        # In a real application, we'd use an async fixture, but for simplicity in tests:
        import asyncio
        if hasattr(app.state, 'http_client') and app.state.http_client is not None:
            try:
                asyncio.run(app.state.http_client.aclose())
            except:
                pass

# Redefine client variable to use the fixture in regular tests
try:
    from fastapi.testclient import TestClient
    from main import app
    # Create a global client for simpler tests
    client = TestClient(app)
    # Initialize http_client directly for simple tests
    import httpx
    app.state.http_client = httpx.AsyncClient()
    CAN_TEST_API = True
except ImportError:
    CAN_TEST_API = False
    logger.warning("无法导入测试所需模块，部分测试可能会被跳过")

# 会话管理集成测试
@pytest.mark.skipif(not CAN_TEST_API, reason="需要FastAPI TestClient")
def test_session_management_flow():
    """测试完整的会话管理流程：创建、列出、更新、删除会话"""
    
    logger.info("开始测试会话管理流程")
    
    # 1. 创建新会话
    create_response = client.post("/api/sessions", json={"name": "测试集成会话"})
    assert create_response.status_code == 200, f"创建会话失败: {create_response.text}"
    session_data = create_response.json()
    assert "id" in session_data, "返回的会话数据中缺少ID"
    session_id = session_data["id"]
    
    logger.info(f"成功创建会话，ID: {session_id}")
    
    # 2. 获取会话列表并验证新会话存在
    list_response = client.get("/api/sessions")
    assert list_response.status_code == 200, "获取会话列表失败"
    sessions = list_response.json()
    assert isinstance(sessions, list), "会话列表应该是一个数组"
    
    # 检查新创建的会话是否在列表中
    found = False
    for session in sessions:
        if session.get("id") == session_id:
            found = True
            break
    assert found, f"在会话列表中未找到新创建的会话 {session_id}"
    
    logger.info("成功验证会话存在于会话列表中")
    
    # 3. 更新会话名称
    update_response = client.put(f"/api/sessions/{session_id}", 
                                json={"name": "已更新的集成测试会话"})
    assert update_response.status_code == 200, f"更新会话失败: {update_response.text}"
    
    # 再次获取会话列表并验证名称已更新
    list_response = client.get("/api/sessions")
    sessions = list_response.json()
    updated_session = None
    for session in sessions:
        if session.get("id") == session_id:
            updated_session = session
            break
    
    assert updated_session is not None, "无法找到更新后的会话"
    assert updated_session.get("name") == "已更新的集成测试会话", "会话名称未正确更新"
    
    logger.info("成功验证会话名称已更新")
    
    # 4. 在会话中进行聊天
    chat_response = client.post("/api/chat", 
                              json={"message": "这是集成测试消息", "session_id": session_id})
    assert chat_response.status_code == 200, f"发送聊天消息失败: {chat_response.text}"
    assert "reply" in chat_response.json(), "聊天响应中缺少回复字段"
    
    logger.info("成功在会话中发送聊天消息")
    
    # 5. 删除会话
    delete_response = client.delete(f"/api/sessions/{session_id}")
    assert delete_response.status_code == 200, f"删除会话失败: {delete_response.text}"
    
    # 验证会话已被删除
    list_response = client.get("/api/sessions")
    sessions = list_response.json()
    for session in sessions:
        assert session.get("id") != session_id, "会话删除后仍然存在于列表中"
    
    logger.info("成功验证会话已被删除")
    
    logger.info("会话管理流程测试完成并通过")

# 聊天流程集成测试
@pytest.mark.skipif(not CAN_TEST_API, reason="需要FastAPI TestClient")
def test_chat_flow():
    """测试完整的聊天流程，包括流式响应"""
    
    logger.info("开始测试聊天流程")
    
    # 1. 无会话聊天 (单次对话)
    single_chat_response = client.post("/api/chat", 
                                     json={"message": "你好，这是一条测试消息"})
    assert single_chat_response.status_code == 200, "无会话聊天请求失败"
    assert "reply" in single_chat_response.json(), "聊天响应中缺少回复"
    
    logger.info("无会话聊天测试通过")
    
    # 2. 带会话的连续对话
    # 创建新会话
    session_response = client.post("/api/sessions", json={"name": "聊天流程测试会话"})
    session_id = session_response.json()["id"]
    
    # 第一条消息
    first_msg_response = client.post("/api/chat", 
                                   json={"message": "我想了解一下焦虑症", "session_id": session_id})
    assert first_msg_response.status_code == 200, "带会话的第一条消息请求失败"
    first_reply = first_msg_response.json().get("reply", "")
    assert first_reply, "第一条消息没有收到回复"
    
    # 第二条消息 (应该保持上下文)
    second_msg_response = client.post("/api/chat", 
                                    json={"message": "有哪些缓解方法？", "session_id": session_id})
    assert second_msg_response.status_code == 200, "带会话的第二条消息请求失败"
    second_reply = second_msg_response.json().get("reply", "")
    assert second_reply, "第二条消息没有收到回复"
    
    logger.info("带会话的连续对话测试通过")
    
    # 3. 测试发送反馈
    feedback_response = client.post("/api/feedback", json={
        "message_id": "test_chat_" + str(hash(first_reply))[:8],
        "session_id": session_id,
        "user_query": "我想了解一下焦虑症",
        "bot_response": first_reply,
        "rating": 1,
        "comment": "聊天流程测试反馈"
    })
    assert feedback_response.status_code == 200, "发送反馈请求失败"
    assert feedback_response.json().get("success") is True, "反馈请求未成功处理"
    
    logger.info("反馈功能测试通过")
    
    # 清理 - 删除测试会话
    client.delete(f"/api/sessions/{session_id}")
    
    logger.info("聊天流程测试完成并通过")

# 流式响应测试 - 这部分在实际服务器环境中效果更好，这里做基本测试
@pytest.mark.skipif(not CAN_TEST_API, reason="需要FastAPI TestClient")
def test_streaming_response():
    """测试流式响应API"""
    
    logger.info("开始测试流式响应")
    
    stream_data_received = False
    try:
        # TestClient doesn't support 'stream' parameter, so remove it
        response = client.post("/api/chat/stream", 
                             json={"message": "测试流式响应", "session_id": None},
                             headers={"Accept": "text/event-stream"})
        
        assert response.status_code == 200, f"流式响应请求失败: {response.status_code}"
        
        # Test client response already contains the full response
        content = response.content
        if content:
            stream_data_received = True
            decoded_content = content.decode('utf-8')
            assert "data:" in decoded_content, "流式响应内容格式不符合预期 (缺少 'data:')"
            assert '"type": "start"' in decoded_content, "流式响应缺少 'start' 事件"
            assert '"type": "end"' in decoded_content, "流式响应缺少 'end' 事件"
            
        assert stream_data_received, "流式响应未接收到任何数据"
        logger.info("流式响应测试通过，并成功接收和验证了流数据")

    except Exception as e:
        logger.error(f"流式响应测试中发生意外错误: {e}")
        pytest.fail(f"流式响应测试失败: {e}")

# 资源API集成测试
@pytest.mark.skipif(not CAN_TEST_API, reason="需要FastAPI TestClient")
def test_resources_api():
    """测试心理健康资源API"""
    
    logger.info("开始测试资源API")
    
    # 获取所有资源
    all_resources_response = client.get("/api/resources")
    assert all_resources_response.status_code == 200, "获取所有资源请求失败"
    resources = all_resources_response.json()
    assert isinstance(resources, list), "资源数据应该是一个列表"
    
    # 如果有资源，测试过滤功能
    if resources:
        # 获取第一个资源的分类
        category = resources[0].get("category", "")
        if category:
            # 按分类过滤
            filtered_response = client.get(f"/api/resources?category={category}")
            assert filtered_response.status_code == 200, "按分类过滤资源请求失败"
            filtered_resources = filtered_response.json()
            assert all(r.get("category") == category for r in filtered_resources), \
                "过滤后的资源包含不符合分类条件的项目"
    
    # 测试分页功能
    paged_response = client.get("/api/resources?limit=2")
    assert paged_response.status_code == 200, "分页请求失败"
    paged_resources = paged_response.json()
    assert len(paged_resources) <= 2, "返回的资源数量超过了limit参数指定的值"
    
    logger.info("资源API测试通过")

# 模拟前端-后端通信测试
def test_mock_frontend_backend():
    """使用mock测试前端和后端之间的通信"""
    
    logger.info("开始模拟前端-后端通信测试")
    
    # 模拟API客户端
    class MockApiClient:
        def sendChat(self, message, session_id=None):
            """模拟前端发送聊天请求的方法"""
            # 这会在实际环境中调用 /api/chat
            # 这里我们直接返回模拟响应
            return {
                "reply": "这是模拟的回复内容，用于测试前端-后端通信。"
            }
        
        def sendFeedback(self, feedback_data):
            """模拟前端发送反馈的方法"""
            # 检查必要字段是否存在
            required_fields = ['message_id', 'session_id', 'user_query', 
                              'bot_response', 'rating']
            for field in required_fields:
                if field not in feedback_data:
                    return {"success": False, "error": f"缺少必要字段: {field}"}
            
            # 在实际环境中这会调用 /api/feedback
            return {"success": True}
        
        def getSessions(self):
            """模拟获取会话列表"""
            return [
                {"id": "mock-session-1", "name": "模拟会话1", "created_at": "2023-04-21T10:00:00Z"},
                {"id": "mock-session-2", "name": "模拟会话2", "created_at": "2023-04-21T11:00:00Z"}
            ]
    
    # 模拟前端组件
    class MockChatComponent:
        def __init__(self, api_client):
            self.api_client = api_client
            self.current_session_id = None
            self.messages = []
        
        def startNewSession(self, name="新会话"):
            """开始新会话"""
            # 实际会调用创建会话API
            self.current_session_id = f"mock-session-{hash(name)}"
            return self.current_session_id
        
        def sendMessage(self, text):
            """发送消息并处理回复"""
            # 调用API发送消息
            response = self.api_client.sendChat(text, self.current_session_id)
            
            # 记录消息和回复
            self.messages.append({"role": "user", "content": text})
            self.messages.append({"role": "assistant", "content": response["reply"]})
            
            # 返回助手的回复
            return response["reply"]
        
        def rateBotResponse(self, message_index, rating, comment=None):
            """对机器人回复进行评分"""
            if message_index >= len(self.messages) or self.messages[message_index]["role"] != "assistant":
                return False
            
            # 准备反馈数据
            bot_msg = self.messages[message_index]
            user_msg = self.messages[message_index-1] if message_index > 0 else {"content": ""}
            
            feedback_data = {
                "message_id": f"mock-msg-{message_index}",
                "session_id": self.current_session_id,
                "user_query": user_msg["content"],
                "bot_response": bot_msg["content"],
                "rating": rating,
                "comment": comment
            }
            
            # 发送反馈
            result = self.api_client.sendFeedback(feedback_data)
            return result["success"]
    
    # 执行模拟测试
    api_client = MockApiClient()
    chat_component = MockChatComponent(api_client)
    
    # 测试流程
    # 1. 开始新会话
    session_id = chat_component.startNewSession("模拟集成测试会话")
    assert session_id is not None, "创建会话失败"
    
    # 2. 发送消息并获取回复
    question = "这是一个模拟的问题，用于测试集成？"
    reply = chat_component.sendMessage(question)
    assert reply, "没有收到回复"
    
    # 3. 对回复进行评分
    rating_success = chat_component.rateBotResponse(1, 1, "很有帮助的模拟回复")
    assert rating_success, "提交反馈失败"
    
    logger.info("模拟前端-后端通信测试通过")

# 主函数
if __name__ == "__main__":
    # 检查是否已安装pytest
    try:
        import pytest
    except ImportError:
        print("❌ 缺少 pytest 包。请运行: pip install pytest")
        sys.exit(1)
    
    # 运行测试
    sys.exit(pytest.main(["-xvs", __file__]))
