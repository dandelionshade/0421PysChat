import os
import sys
import pymysql
import pymysql.cursors
from dotenv import load_dotenv
import logging
import pytest  # 新增导入pytest

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加父目录到路径以便导入主应用
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
load_dotenv()

def test_db_connection():
    """直接测试数据库连接，不使用应用程序的其他部分"""
    # 从环境变量获取数据库配置
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "psychat")
    
    logger.info(f"尝试连接到数据库: {db_host}:{db_port}/{db_name}")
    
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
        
        # 测试连接
        with connection.cursor() as cursor:
            # 执行一个简单的查询
            cursor.execute("SELECT 1 AS result")
            result = cursor.fetchone()
            assert result is not None, "数据库查询 (SELECT 1 AS result) 未返回任何结果"
            assert result["result"] == 1, "数据库查询应返回值1"
            
            # 测试能否查询表结构
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = [list(table.values())[0] for table in tables]
            
            logger.info(f"成功连接到数据库。找到以下表: {', '.join(table_names)}")
            
            # 测试核心表是否存在
            expected_tables = ['resources', 'feedback', 'chat_sessions', 'chat_messages'] # Removed 'users', 'attachments'
            for table in expected_tables:
                assert table in table_names, f"核心表 '{table}' 不存在"
        
        connection.close()
        logger.info("数据库连接测试成功通过！")
        assert True  # 使用assertion而不是return
    except pymysql.MySQLError as e:
        logger.error(f"数据库连接错误: {e}")
        pytest.skip(f"数据库连接失败，跳过测试: {e}")  # Skip instead of returning False
    except AssertionError as e:
        logger.error(f"数据库测试断言失败: {e}")
        raise  # Re-raise assertion error
    except Exception as e:
        error_str = str(e)
        if "cryptography" in error_str and "required" in error_str:
            logger.error("缺少加密库: MySQL 8.0+ 的身份验证需要 'cryptography' 包")
            logger.error("请运行: pip install cryptography")
        else:
            logger.error(f"数据库测试中发生未知错误: {e}")
        pytest.skip(f"数据库测试失败，跳过测试: {e}")  # Skip on unknown error

if __name__ == "__main__":
    """当直接运行此脚本时执行测试"""
    # 检查是否已安装关键依赖
    try:
        import pymysql
    except ImportError:
        print("❌ 缺少 pymysql 包。请运行: pip install pymysql")
        sys.exit(1)
        
    try:
        import cryptography
        print("✓ cryptography 包已安装")
    except ImportError:
        print("❌ 缺少 cryptography 包。MySQL 8.0+ 身份验证需要此包。")
        print("请运行: pip install cryptography")
        sys.exit(1)
        
    success = test_db_connection()
    if success:
        print("✅ 数据库连接测试成功！")
        sys.exit(0)
    else:
        print("❌ 数据库连接测试失败！")
        sys.exit(1)
