#!/usr/bin/env python
"""
PsyChat Backend Test Environment
This script initializes a test environment for the PsyChat backend.
"""
import os
import sys
import uvicorn
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test-environment")

def validate_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        "ANYTHINGLLM_API_BASE_URL",
        "ANYTHINGLLM_WORKSPACE_SLUG",
        "DB_HOST",
        "DB_PORT",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
        "SERVER_PORT"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please check your .env file and make sure all required variables are set")
        return False
    
    return True

def check_database():
    """Simple test to check database connectivity"""
    try:
        # Import necessary modules
        import pymysql
        
        # Get database configuration from environment
        db_host = os.getenv("DB_HOST")
        db_port = int(os.getenv("DB_PORT", "3306"))
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")
        
        # Try to connect
        logger.info(f"Testing connection to MySQL database {db_name} at {db_host}:{db_port}")
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Execute a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        connection.close()
        logger.info("✅ Database connection successful")
        return True
    
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False

def start_test_server():
    """Start the backend server in test mode"""
    # 配置Uvicorn日志记录
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s - %(message)s",
                "use_colors": True
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(levelprefix)s %(asctime)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
                "use_colors": True
            }
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr"
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False}
        }
    }
    
    server_port = int(os.getenv("SERVER_PORT", "8000"))
    logger.info(f"Starting test server on port {server_port}")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=server_port, 
        reload=True,
        log_config=log_config
    )

if __name__ == "__main__":
    # Load environment variables
    logger.info("Loading environment variables from .env file")
    load_dotenv()
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Check database connection
    if not check_database():
        logger.warning("Continuing despite database connection issues...")
    
    # Start test server
    start_test_server()
