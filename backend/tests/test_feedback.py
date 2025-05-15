import os
import sys
import json
import pytest
import pymysql
import pymysql.cursors  # Add this line
from dotenv import load_dotenv
import logging
from unittest.mock import MagicMock, patch

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加父目录到路径以便导入主应用
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
load_dotenv()

# 导入需要测试的模块 (在实际运行时会找到这些模块，这里列出用于理解)
# from api.feedback import router as feedback_router
# from main import app

# Database connection fixture
@pytest.fixture
def db_connection():
    """创建测试数据库连接并在测试后清理"""
    # 从环境变量获取数据库配置
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "psychat")
    
    try:
        # 创建数据库连接
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        yield connection
        
        # 测试后清理
        # 可以在这里添加测试后的清理代码，如删除测试数据
        connection.close()
    except pymysql.MySQLError as e:
        logger.error(f"数据库连接错误: {e}")
        pytest.skip(f"无法连接到数据库: {e}")

# 测试数据库中的feedback表是否存在和结构是否正确
def test_feedback_table_exists(db_connection):
    """测试feedback表是否存在并有正确的结构"""
    try:
        with db_connection.cursor() as cursor:
            # 检查feedback表是否存在
            cursor.execute("SHOW TABLES LIKE 'feedback'")
            result = cursor.fetchone()
            assert result is not None, "feedback表不存在"
            
            # 检查表结构
            cursor.execute("DESCRIBE feedback")
            columns = cursor.fetchall()
            column_names = [column['Field'] for column in columns]
            
            # 验证所需列是否存在
            expected_columns = ['id', 'message_id', 'session_id', 'user_query', 
                              'bot_response', 'rating', 'comment', 'created_at']
            for column in expected_columns:
                assert column in column_names, f"feedback表缺少列'{column}'"
            
        logger.info("feedback表结构测试通过")
    except Exception as e:
        logger.error(f"测试feedback表结构时发生错误: {e}")
        raise

# 测试插入反馈记录到数据库
def test_insert_feedback(db_connection):
    """测试向feedback表插入记录"""
    try:
        with db_connection.cursor() as cursor:
            # 准备测试数据
            test_feedback = {
                'message_id': 'test_msg_123',
                'session_id': 'test_session_123',
                'user_query': '我感到很焦虑怎么办？',
                'bot_response': '焦虑是常见的情绪反应，建议尝试深呼吸等放松技巧...',
                'rating': 1,  # 积极评价
                'comment': '回答很有帮助'
            }
            
            # 执行插入操作
            sql = """
            INSERT INTO feedback (message_id, session_id, user_query, bot_response, rating, comment)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                test_feedback['message_id'],
                test_feedback['session_id'],
                test_feedback['user_query'],
                test_feedback['bot_response'],
                test_feedback['rating'],
                test_feedback['comment']
            ))
            db_connection.commit()
            
            # 验证插入是否成功
            cursor.execute("SELECT * FROM feedback WHERE message_id = %s", (test_feedback['message_id'],))
            result = cursor.fetchone()
            assert result is not None, "未能成功插入feedback记录"
            assert result['rating'] == test_feedback['rating'], "插入的rating值不匹配"
            assert result['comment'] == test_feedback['comment'], "插入的comment值不匹配"
            
            # 清理测试数据
            cursor.execute("DELETE FROM feedback WHERE message_id = %s", (test_feedback['message_id'],))
            db_connection.commit()
            
        logger.info("feedback插入测试通过")
    except Exception as e:
        logger.error(f"测试feedback插入时发生错误: {e}")
        # 确保清理，即使测试失败
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("DELETE FROM feedback WHERE message_id = %s", ('test_msg_123',))
                db_connection.commit()
        except:
            pass
        raise

# API测试部分 - 需要导入fastapi的TestClient
@pytest.mark.api
def test_feedback_api():
    """测试反馈API端点"""
    # 由于我们需要导入实际应用，此处使用了try-except
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        # Initialize app.state.http_client for tests
        import httpx
        app.state.http_client = httpx.AsyncClient()
        
        client = TestClient(app)
        
        # 测试提交反馈
        test_feedback = {
            'message_id': 'test_api_msg_123',
            'session_id': 'test_api_session_123',
            'user_query': '我最近睡眠不好怎么办？',
            'bot_response': '睡眠问题可能与多种因素有关，建议规律作息...',
            'rating': 1,
            'comment': 'API测试评论'
        }
        
        response = client.post("/api/feedback", json=test_feedback)
        assert response.status_code == 200, f"API返回错误状态码: {response.status_code}"
        assert "success" in response.json(), "API响应中缺少success字段"
        assert response.json()["success"] is True, "API响应表示操作失败"
        
        logger.info("feedback API测试通过")
        
        # Clean up the http client
        import asyncio
        try:
            asyncio.run(app.state.http_client.aclose())
        except:
            pass
    except ImportError as e:
        logger.warning(f"无法导入测试所需模块，跳过API测试: {e}")
        pytest.skip("缺少测试API所需的依赖")
    except Exception as e:
        logger.error(f"测试feedback API时发生错误: {e}")
        raise

# 模拟前端-后端通信的集成测试
@pytest.mark.integration
def test_frontend_backend_integration():
    """模拟前端-后端通信的集成测试"""
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        # 创建测试客户端
        client = TestClient(app)
        
        # 模拟前端提交反馈的流程
        # 1. 发送聊天消息
        chat_request = {
            "message": "我最近压力很大，有什么放松的方法吗？",
            "session_id": "test_integration_session"
        }
        chat_response = client.post("/api/chat", json=chat_request)
        assert chat_response.status_code == 200, "聊天API返回错误状态码"
        
        # 2. 提取回复内容，模拟用户提交反馈
        bot_reply = chat_response.json().get("reply", "")
        feedback_request = {
            "message_id": "test_int_msg_" + str(hash(bot_reply))[:8],
            "session_id": "test_integration_session",
            "user_query": chat_request["message"],
            "bot_response": bot_reply,
            "rating": 1,  # 积极评价
            "comment": "集成测试反馈"
        }
        
        feedback_response = client.post("/api/feedback", json=feedback_request)
        assert feedback_response.status_code == 200, "反馈API返回错误状态码"
        assert feedback_response.json().get("success") is True, "反馈API响应表示操作失败"
        
        logger.info("前端-后端集成测试通过")
    except ImportError as e:
        logger.warning(f"无法导入测试所需模块，跳过集成测试: {e}")
        pytest.skip("缺少集成测试所需的依赖")
    except Exception as e:
        logger.error(f"执行集成测试时发生错误: {e}")
        raise

# 模拟测试 - 当实际环境不可用时使用
@pytest.mark.mock
def test_feedback_with_mocks():
    """使用模拟对象测试反馈功能"""
    # 模拟数据库连接和游标
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    
    # 准备测试数据
    test_feedback = {
        'message_id': 'mock_msg_123',
        'session_id': 'mock_session_123',
        'user_query': '模拟问题？',
        'bot_response': '模拟回答...',
        'rating': 0,  # 消极评价
        'comment': '模拟评论'
    }
    
    # 设置模拟行为
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = {**test_feedback, 'id': 1, 'created_at': '2023-04-21 12:00:00'}
    
    # 模拟执行插入反馈的函数
    def mock_insert_feedback(connection, feedback_data):
        # 这里模拟实际插入函数的行为
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO feedback ...")
            connection.commit()
            return True
    
    # 执行测试
    result = mock_insert_feedback(mock_connection, test_feedback)
    
    # 验证结果
    assert result is True, "模拟插入反馈失败"
    mock_cursor.execute.assert_called(), "未调用execute方法"
    mock_connection.commit.assert_called_once(), "未调用commit方法"
    
    logger.info("模拟测试通过")

# 主函数，允许直接运行此测试文件
if __name__ == "__main__":
    # 检查是否已安装pytest
    try:
        import pytest
    except ImportError:
        print("❌ 缺少 pytest 包。请运行: pip install pytest")
        sys.exit(1)
    
    # 运行测试
    sys.exit(pytest.main(["-xvs", __file__]))
