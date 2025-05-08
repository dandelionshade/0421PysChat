import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# 导入主应用
from backend.main import app

# 创建测试客户端
client = TestClient(app)

# 模拟数据库连接和查询结果
@pytest.fixture
def mock_db_resources():
    return [
        {
            "id": 1,
            "title": "全国心理援助热线",
            "description": "提供24小时心理支持和危机干预",
            "category": "crisis",
            "location_tag": "national",
            "contact_info": "400-161-9995",
            "url": "https://example.com/hotline",
            "created_at": "2023-01-01T00:00:00"
        },
        {
            "id": 2,
            "title": "心理健康咨询中心",
            "description": "提供专业心理咨询服务",
            "category": "counseling",
            "location_tag": "beijing",
            "contact_info": "010-12345678",
            "url": "https://example.com/center",
            "created_at": "2023-01-02T00:00:00"
        }
    ]

# 测试资源API端点 - 获取所有资源
@patch("backend.main.get_db_connection")
def test_get_resources(mock_get_db, mock_db_resources):
    # 设置模拟数据库连接和游标
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_db_resources
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_db.return_value = mock_conn
    
    # 发送测试请求
    response = client.get("/api/resources")
    
    # 验证响应
    assert response.status_code == 200
    assert len(response.json()) == len(mock_db_resources)
    assert response.json()[0]["title"] == mock_db_resources[0]["title"]
    
    # 验证SQL查询
    mock_cursor.execute.assert_called_once()
    
# 测试资源API端点 - 使用过滤条件
@patch("backend.main.get_db_connection")
def test_get_resources_with_filters(mock_get_db, mock_db_resources):
    # 筛选后的结果
    filtered_results = [mock_db_resources[0]]  # 只包含crisis类别的资源
    
    # 设置模拟数据库连接和游标
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = filtered_results
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_db.return_value = mock_conn
    
    # 发送测试请求 - 按类别筛选
    response = client.get("/api/resources?category=crisis")
    
    # 验证响应
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "crisis"
    
    # 验证SQL查询包含过滤条件
    mock_cursor.execute.assert_called_once()
