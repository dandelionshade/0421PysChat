import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import patch, MagicMock

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从main导入FastAPI应用
from main import app

# 创建测试客户端
client = TestClient(app)

# 测试健康检查端点 - 正常情况
@patch("main.get_db_connection")
def test_health_check_success(mock_get_db):
    # 设置模拟数据库连接
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"column1": 1}  # 假设查询结果包含1
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_db.return_value = mock_conn
    
    # 发送请求到健康检查端点
    response = client.get("/health")
    
    # 验证响应
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["api"] == "healthy"
    assert response.json()["database"] == "healthy"
    
    # 验证数据库连接被正确调用
    mock_get_db.assert_called_once()

# 测试健康检查端点 - 数据库连接失败
@patch("main.get_db_connection")
def test_health_check_db_failure(mock_get_db):
    # 设置模拟数据库连接失败
    mock_get_db.side_effect = Exception("Database connection failed")
    
    # 发送请求到健康检查端点
    response = client.get("/health")
    
    # 验证响应
    assert response.status_code == 503  # Service Unavailable
    assert response.json()["status"] == "degraded"
    assert response.json()["api"] == "healthy"
    assert response.json()["database"] == "unhealthy"
    assert "Database connection failed" in response.json()["database_error"]
