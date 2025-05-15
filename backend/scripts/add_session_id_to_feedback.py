'''
Author: zhen doniajohary2677@gmail.com
Date: 2023-05-15 19:22:24
LastEditors: zhen doniajohary2677@gmail.com
LastEditTime: 2023-05-15 19:25:15
FilePath: \0421PysChat\backend\scripts\add_session_id_to_feedback.py
Description: 向feedback表添加session_id字段的数据库迁移脚本
'''
import os
import sys
import pymysql
import pymysql.cursors
from dotenv import load_dotenv
import logging

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加父目录到路径以便导入主应用
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
load_dotenv()

def add_session_id_to_feedback():
    """为feedback表添加session_id列"""
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
        
        with connection.cursor() as cursor:
            # 检查feedback表是否存在
            cursor.execute("SHOW TABLES LIKE 'feedback'")
            if not cursor.fetchone():
                logger.error("feedback表不存在，请先创建表")
                return False
                
            # 检查session_id列是否已存在
            cursor.execute("DESCRIBE feedback")
            columns = cursor.fetchall()
            column_names = [column['Field'] for column in columns]
            
            if 'session_id' in column_names:
                logger.info("session_id列已存在，无需添加")
                return True
                
            # 添加session_id列
            logger.info("正在添加session_id列...")
            cursor.execute(
                "ALTER TABLE feedback ADD COLUMN session_id VARCHAR(255) AFTER message_id"
            )
            connection.commit()
            logger.info("session_id列添加成功")
            
            # 更新现有记录的session_id（如有必要）
            cursor.execute("UPDATE feedback SET session_id = 'migration_default' WHERE session_id IS NULL")
            connection.commit()
            logger.info("现有记录已更新默认session_id值")
            
            return True
            
    except pymysql.MySQLError as e:
        logger.error(f"数据库操作错误: {e}")
        return False
    except Exception as e:
        logger.error(f"执行迁移时发生未知错误: {e}")
        return False

if __name__ == "__main__":
    success = add_session_id_to_feedback()
    if success:
        print("✅ 成功添加session_id列到feedback表")
        sys.exit(0)
    else:
        print("❌ 添加session_id列失败，请检查日志")
        sys.exit(1)
