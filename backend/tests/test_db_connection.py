import os
import sys
import pymysql
from dotenv import load_dotenv
import logging

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
            assert result["result"] == 1, "数据库查询应返回值1"
            
            # 测试能否查询表结构
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = [list(table.values())[0] for table in tables]
            
            logger.info(f"成功连接到数据库。找到以下表: {', '.join(table_names)}")
            
            # 测试核心表是否存在
            expected_tables = ['resources', 'feedback', 'chat_sessions', 'chat_messages']
            for table in expected_tables:
                assert table in table_names, f"核心表 '{table}' 不存在"
        
        connection.close()
        logger.info("数据库连接测试成功通过！")
        return True
    
    except pymysql.MySQLError as e:
        logger.error(f"数据库连接错误: {e}")
        return False
    except AssertionError as e:
        logger.error(f"数据库测试断言失败: {e}")
        return False
    except Exception as e:
        logger.error(f"数据库测试中发生未知错误: {e}")
        return False

if __name__ == "__main__":
    """当直接运行此脚本时执行测试"""
    success = test_db_connection()
    if success:
        print("✅ 数据库连接测试成功！")
        sys.exit(0)
    else:
        print("❌ 数据库连接测试失败！")
        sys.exit(1)
