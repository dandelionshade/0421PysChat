from fastapi import FastAPI, HTTPException, Query, Depends, Request # 添加Request导入
from fastapi.middleware.cors import CORSMiddleware # 导入CORS中间件，用于处理跨域请求
from pydantic import BaseModel # 导入Pydantic的BaseModel，用于定义请求体和响应体的数据模型
from typing import List, Optional, Dict, Any, Annotated # 导入Python类型提示工具
import httpx # 导入httpx库，用于发送HTTP请求
import pymysql # 导入pymysql库，用于连接MySQL数据库
import os # 导入os模块，用于访问环境变量
from dotenv import load_dotenv # 导入load_dotenv函数，用于从.env文件加载环境变量
import logging # Import logging module
import datetime # Import datetime module for timestamp
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError # 添加此导入
from starlette.exceptions import HTTPException as StarletteHTTPException # 添加此导入

# Configure basic logging # 配置基本日志记录
logging.basicConfig(level=logging.INFO) # 设置日志级别为INFO
logger = logging.getLogger(__name__) # 获取当前模块的logger实例

# Load environment variables # 加载环境变量
load_dotenv() # 调用函数加载环境变量

# --- Configuration Validation ---
ANYTHINGLLM_BASE_URL = os.getenv("ANYTHINGLLM_API_BASE_URL")
WORKSPACE_SLUG = os.getenv("ANYTHINGLLM_WORKSPACE_SLUG")
ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY") # 允许为空，但如果API需要则会报错
HTTPX_TIMEOUT = float(os.getenv("HTTPX_TIMEOUT", "60.0")) # 从环境变量获取超时时间

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "mental_health_db")

# --- Global HTTP Client ---
# Declare a global variable for the httpx client
# This client will be initialized on app startup and closed on shutdown
# to efficiently reuse connections.
http_client: httpx.AsyncClient

async def get_http_client() -> httpx.AsyncClient:
    """
    Dependency to get the shared httpx.AsyncClient.
    This ensures the client is initialized before being used in path operations.
    """
    if not hasattr(app.state, 'http_client'):
        raise HTTPException(status_code=500, detail="HTTP client not initialized.")
    return app.state.http_client

app = FastAPI(title="Mental Health Chatbot API") # 创建FastAPI应用实例，并设置标题

# --- Lifespan Events for HTTP Client ---
@app.on_event("startup")
async def startup_event():
    """
    Initialize the httpx.AsyncClient when the application starts.
    Also, validate essential configurations.
    """
    app.state.http_client = httpx.AsyncClient(timeout=HTTPX_TIMEOUT)
    logger.info(f"HTTPX Client initialized with timeout: {HTTPX_TIMEOUT}s")

    if not ANYTHINGLLM_BASE_URL:
        logger.error("CRITICAL: ANYTHINGLLM_API_BASE_URL is not configured.")
    if not WORKSPACE_SLUG:
        logger.error("CRITICAL: ANYTHINGLLM_WORKSPACE_SLUG is not configured.")
    logger.info("Application startup: Configurations loaded.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Close the httpx.AsyncClient when the application shuts down.
    """
    if hasattr(app.state, 'http_client'):
        await app.state.http_client.aclose()
        logger.info("HTTPX Client closed.")

# Configure CORS # 配置CORS（跨域资源共享）
app.add_middleware( # 添加中间件
    CORSMiddleware, # 使用CORSMiddleware
    allow_origins=["*"],  # In production, replace with specific origins # 允许所有来源的请求，在生产环境中应替换为指定的来源
    allow_credentials=True, # 允许发送凭据（cookies, authorization headers）
    allow_methods=["*"], # 允许所有HTTP方法（GET, POST等）
    allow_headers=["*"], # 允许所有HTTP头
)

# Pydantic models # Pydantic模型定义
class ChatRequest(BaseModel): # 定义聊天请求的数据模型
    message: str # 消息内容，类型为字符串
    session_id: Optional[str] = None # Optional session ID for threaded conversations

class ChatResponse(BaseModel): # 定义聊天响应的数据模型
    reply: str # 响应内容，类型为字符串

# Database connection helper # 数据库连接帮助函数
def get_db_connection(): # 定义获取数据库连接的函数
    try: # 尝试连接数据库
        connection = pymysql.connect( # 调用pymysql.connect建立连接
            host=DB_HOST, # 数据库主机名
            port=DB_PORT, # 数据库端口
            user=DB_USER, # 数据库用户名
            password=DB_PASSWORD, # 数据库密码
            database=DB_NAME, # 数据库名称
            cursorclass=pymysql.cursors.DictCursor # 使用字典光标，使查询结果以字典形式返回
        ) # 连接参数结束
        return connection # 返回建立的数据库连接
    except pymysql.MySQLError as e: # 捕获pymysql的数据库错误
        logger.error(f"Error connecting to MySQL: {e}") # 打印错误信息
        raise HTTPException(status_code=500, detail="Database connection error") # 抛出HTTPException，表示数据库连接错误

@app.get("/") # 定义根路径的GET请求处理函数
async def root(): # 异步函数定义
    return {"status": "API is running"} # 返回API运行状态信息

@app.post("/api/chat", response_model=ChatResponse) # 定义/api/chat路径的POST请求处理函数，响应模型为ChatResponse
async def chat(
    request: ChatRequest,
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)] # Use Depends for the client
):
    if not WORKSPACE_SLUG or not ANYTHINGLLM_BASE_URL:
        logger.error("AnythingLLM URL or workspace not configured properly.")
        raise HTTPException(status_code=500, detail="AnythingLLM service not configured")

    # Set up proper headers according to API documentation
    headers = {
        "Content-Type": "application/json",
    }
    if ANYTHINGLLM_API_KEY:
        headers["Authorization"] = f"Bearer {ANYTHINGLLM_API_KEY}"

    # Structure payload according to API docs
    payload = {
        "message": request.message,
    }

    anything_llm_url = ""
    current_thread_id = None
    db_conn = None

    try:
        if request.session_id:
            logger.info(f"Chat request for session_id: {request.session_id}")
            db_conn = get_db_connection()
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT anythingllm_thread_id FROM chat_sessions WHERE id = %s", (request.session_id,))
                session_row = cursor.fetchone()

                if session_row and session_row.get("anythingllm_thread_id"):
                    current_thread_id = session_row["anythingllm_thread_id"]
                    logger.info(f"Found existing thread_id: {current_thread_id}")
                else:
                    # Create a new thread using the proper API endpoint format
                    new_thread_url = f"{ANYTHINGLLM_BASE_URL}/v1/workspace/{WORKSPACE_SLUG}/thread/new"
                    logger.info(f"Creating new thread via: {new_thread_url}")
                    
                    new_thread_response = await client.post(new_thread_url, json={}, headers=headers)
                    new_thread_response.raise_for_status()
                    thread_data = new_thread_response.json()
                    
                    # Extract thread ID/slug from response according to API format
                    current_thread_id = thread_data.get("threadSlug") or thread_data.get("slug")
                    if not current_thread_id:
                        logger.error(f"Failed to get thread ID from response: {thread_data}")
                        raise HTTPException(status_code=500, detail="Failed to create thread")
                    
                    # Save thread ID to database
                    if session_row:
                        cursor.execute("UPDATE chat_sessions SET anythingllm_thread_id = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                                      (current_thread_id, request.session_id))
                    else:
                        cursor.execute("INSERT INTO chat_sessions (id, anythingllm_thread_id, name) VALUES (%s, %s, %s)",
                                      (request.session_id, current_thread_id, f"Session {request.session_id[:8]}"))
                    db_conn.commit()
            
            # Use the thread-specific chat endpoint format
            anything_llm_url = f"{ANYTHINGLLM_BASE_URL}/v1/workspace/{WORKSPACE_SLUG}/thread/{current_thread_id}/chat"
        
        else: # No session_id, use general workspace chat
            logger.info("Using general workspace chat")
            anything_llm_url = f"{ANYTHINGLLM_BASE_URL}/v1/workspace/{WORKSPACE_SLUG}/chat"
            payload["mode"] = "chat"

        logger.info(f"Sending request to: {anything_llm_url}")
        response = await client.post(anything_llm_url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        logger.debug(f"Raw response: {result}")

        # Parse response according to API format
        reply_content = None
        if "textResponse" in result:
            reply_content = result["textResponse"]
        elif "response" in result and "text" in result["response"]:
            reply_content = result["response"]["text"]
        elif result.get("type") == "textResponse" and "text" in result.get("content", {}):
            reply_content = result["content"]["text"]
        else:
            logger.warning(f"Unexpected response format: {result}")
            reply_content = "抱歉，无法获取有效回复内容。"

        return ChatResponse(reply=str(reply_content).strip())

    except httpx.HTTPStatusError as e:
        error_body = e.response.text
        try:
            error_json = e.response.json()
            error_detail = error_json.get("error", {}).get("message") or error_json.get("detail") or error_body
        except ValueError: # If response is not JSON
            error_detail = error_body
        logger.error(f"AnythingLLM API error: {e.response.status_code} - Detail: {error_detail} - URL: {e.request.url}")
        raise HTTPException(
            status_code=e.response.status_code, # Propagate status code from AnythingLLM
            detail=f"LLM服务错误: {error_detail}"
        )
    except httpx.RequestError as e: # Covers ConnectError, TimeoutException, etc.
        logger.error(f"HTTP request error to AnythingLLM: {e} - URL: {e.request.url if e.request else 'Unknown URL'}")
        raise HTTPException(status_code=503, detail=f"无法连接到LLM服务: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")
    finally:
        if db_conn:
            db_conn.close()
            logger.debug("Database connection closed for chat endpoint.")


@app.get("/api/resources")
async def get_resources(
    category: Optional[str] = Query(None, description="Filter by resource category"),
    location: Optional[str] = Query(None, description="Filter by location tag"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of records to return") # Added ge and le for validation
):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM resources WHERE 1=1"
            params = []

            if category:
                query += " AND category = %s"
                params.append(category)

            if location:
                query += " AND location_tag = %s" # Ensure column name is correct
                params.append(location)

            query += " ORDER BY created_at DESC LIMIT %s" # Ensure 'created_at' column exists
            params.append(limit)

            logger.debug(f"Executing DB query: {query} with params: {params}")
            cursor.execute(query, tuple(params)) # Ensure params is a tuple
            resources_data = cursor.fetchall()

            # Convert decimal types to float and bytes to string for JSON serialization
            processed_resources = []
            for resource_row in resources_data:
                processed_row = {}
                for key, value in resource_row.items():
                    if isinstance(value, bytes):
                        try:
                            processed_row[key] = value.decode('utf-8')
                        except UnicodeDecodeError:
                            logger.warning(f"Could not decode bytes to utf-8 for key '{key}'. Storing as repr.")
                            processed_row[key] = repr(value) # Fallback for non-utf8 bytes
                    elif hasattr(value, 'quantize'): # Check for Decimal type
                        processed_row[key] = float(value)
                    else:
                        processed_row[key] = value
                processed_resources.append(processed_row)

            return processed_resources
    except pymysql.MySQLError as e: # More specific exception for DB errors
        logger.error(f"Error querying database: {e}")
        raise HTTPException(status_code=500, detail=f"数据库查询错误: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error in get_resources endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"获取资源时发生内部服务器错误: {str(e)}")
    finally:
        if conn: # Ensure conn is not None before closing
            conn.close()

@app.get("/health")
async def health_check():
    """
    健康检查端点，用于验证API和数据库连接状态
    返回:
        dict: 包含API和数据库状态的字典
    """
    health_status = {
        "status": "ok",
        "api": "healthy",
        "database": "unknown",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0"  # 可以从应用配置或版本文件中获取
    }
    
    # 测试数据库连接
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and 1 in result.values():
                health_status["database"] = "healthy"
            else:
                health_status["database"] = "unhealthy"
                health_status["status"] = "degraded"
        conn.close()
    except Exception as e:
        logger.error(f"Health check - Database connection error: {e}")
        health_status["database"] = "unhealthy"
        health_status["database_error"] = str(e)
        health_status["status"] = "degraded"
    
    # 根据状态设置正确的HTTP响应码
    if health_status["status"] != "ok":
        return JSONResponse(
            content=health_status,
            status_code=503  # Service Unavailable
        )
    
    return health_status

# 添加自定义404处理程序
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    """自定义404处理程序，记录详细的请求信息"""
    path = request.url.path
    method = request.method
    client = f"{request.client.host}:{request.client.port}" if request.client else "Unknown"
    query = str(request.query_params) if request.query_params else ""
    
    # Improved logging for empty path
    log_message = f"404 NOT FOUND: {method} {path if path else '[EMPTY PATH]'}?{query} - 客户端: {client}"
    if not path: # Path is empty string
        log_message += " - 注意: 请求路径为空。这通常表示客户端发送了格式不正确的HTTP请求 (例如，请求行可能是 'GET HTTP/1.1' 而不是 'GET / HTTP/1.1')。"
    logger.warning(log_message)
    
    response_content = {
        "detail": "请求的路径不存在",
        "path": path, # Will be empty string if path was empty
        "method": method,
        "available_endpoints": [
            "/",
            "/health",
            "/api/chat",
            "/api/resources",
            "/docs",  # 添加Swagger文档路径
            "/redoc"  # 添加ReDoc文档路径
        ]
    }
    # Add specific suggestion if path was empty
    if not path:
        response_content["error_suggestion"] = "检测到请求路径为空。请确保客户端发送的HTTP请求包含一个有效的路径，例如 '/' 代表根路径。"

    return JSONResponse(
        status_code=404,
        content=response_content
    )

# 添加验证错误处理程序
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """自定义请求验证错误处理程序"""
    logger.warning(f"请求验证错误: {request.method} {request.url.path} - {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "请求数据验证失败",
            "errors": exc.errors(),
            "body": exc.body
        }
    )

if __name__ == "__main__":
    import uvicorn
    # For production, you might want to set reload=False and adjust workers
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # Changed host to 0.0.0.0 to be accessible externally if needed




# from fastapi import FastAPI, HTTPException, Query # 导入构建API所需的FastAPI、HTTPException和Query
# from fastapi.middleware.cors import CORSMiddleware # 导入CORS中间件，用于处理跨域请求
# from pydantic import BaseModel # 导入Pydantic的BaseModel，用于定义请求体和响应体的数据模型
# from typing import List, Optional, Dict, Any # 导入Python类型提示工具
# import httpx # 导入httpx库，用于发送HTTP请求
# import pymysql # 导入pymysql库，用于连接MySQL数据库
# import os # 导入os模块，用于访问环境变量
# from dotenv import load_dotenv # 导入load_dotenv函数，用于从.env文件加载环境变量
# import logging # Import logging module

# # Configure basic logging # 配置基本日志记录
# logging.basicConfig(level=logging.INFO) # 设置日志级别为INFO
# logger = logging.getLogger(__name__) # 获取当前模块的logger实例

# # Load environment variables # 加载环境变量
# load_dotenv() # 调用函数加载环境变量

# # AnythingLLM configuration # AnythingLLM服务配置
# ANYTHINGLLM_BASE_URL = os.getenv("ANYTHINGLLM_API_BASE_URL", "http://localhost:3001") # 获取AnythingLLM API的基础URL，默认为http://localhost:3001
# WORKSPACE_SLUG = os.getenv("ANYTHINGLLM_WORKSPACE_SLUG") # 获取AnythingLLM工作空间的slug
# ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY", "") # 获取AnythingLLM API密钥，默认为空字符串

# # Database configuration # 数据库配置
# DB_HOST = os.getenv("DB_HOST", "localhost") # 获取数据库主机名，默认为localhost
# DB_PORT = int(os.getenv("DB_PORT", "3306")) # 获取数据库端口，并转换为整数，默认为3306
# DB_USER = os.getenv("DB_USER", "root") # 获取数据库用户名，默认为root
# DB_PASSWORD = os.getenv("DB_PASSWORD", "") # 获取数据库密码，默认为空字符串
# DB_NAME = os.getenv("DB_NAME", "mental_health_db") # 获取数据库名称，默认为mental_health_db

# app = FastAPI(title="Mental Health Chatbot API") # 创建FastAPI应用实例，并设置标题

# # Configure CORS # 配置CORS（跨域资源共享）
# app.add_middleware( # 添加中间件
#     CORSMiddleware, # 使用CORSMiddleware
#     allow_origins=["*"],  # In production, replace with specific origins # 允许所有来源的请求，在生产环境中应替换为指定的来源
#     allow_credentials=True, # 允许发送凭据（cookies, authorization headers）
#     allow_methods=["*"], # 允许所有HTTP方法（GET, POST等）
#     allow_headers=["*"], # 允许所有HTTP头
# )

# # Pydantic models # Pydantic模型定义
# class ChatRequest(BaseModel): # 定义聊天请求的数据模型
#     message: str # 消息内容，类型为字符串

# class ChatResponse(BaseModel): # 定义聊天响应的数据模型
#     reply: str # 响应内容，类型为字符串 (changed from response to reply)

# # Database connection helper # 数据库连接帮助函数
# def get_db_connection(): # 定义获取数据库连接的函数
#     try: # 尝试连接数据库
#         connection = pymysql.connect( # 调用pymysql.connect建立连接
#             host=DB_HOST, # 数据库主机名
#             port=DB_PORT, # 数据库端口
#             user=DB_USER, # 数据库用户名
#             password=DB_PASSWORD, # 数据库密码
#             database=DB_NAME, # 数据库名称
#             cursorclass=pymysql.cursors.DictCursor # 使用字典光标，使查询结果以字典形式返回
#         ) # 连接参数结束
#         return connection # 返回建立的数据库连接
#     except pymysql.MySQLError as e: # 捕获pymysql的数据库错误
#         print(f"Error connecting to MySQL: {e}") # 打印错误信息
#         raise HTTPException(status_code=500, detail="Database connection error") # 抛出HTTPException，表示数据库连接错误

# @app.get("/") # 定义根路径的GET请求处理函数
# async def root(): # 异步函数定义
#     return {"status": "API is running"} # 返回API运行状态信息

# @app.post("/api/chat", response_model=ChatResponse) # 定义/api/chat路径的POST请求处理函数，响应模型为ChatResponse
# async def chat(request: ChatRequest): # 异步函数定义，接收ChatRequest类型的请求体
#     if not WORKSPACE_SLUG: # 检查是否配置了AnythingLLM工作空间slug
#         logger.error("AnythingLLM workspace not configured") # 日志记录错误
#         raise HTTPException(status_code=500, detail="AnythingLLM workspace not configured") # 如果未配置，则抛出HTTPException
    
#     # Prepare the request to AnythingLLM API # 准备发送到AnythingLLM API的请求
#     anything_llm_url = f"{ANYTHINGLLM_BASE_URL}/api/v1/workspace/{WORKSPACE_SLUG}/chat" # Updated URL
    
#     headers = {"Content-Type": "application/json"} # 初始化请求头字典
#     if ANYTHINGLLM_API_KEY: # 如果存在AnythingLLM API密钥
#         headers["Authorization"] = f"Bearer {ANYTHINGLLM_API_KEY}" # 在请求头中添加Authorization字段
    
#     payload = { # 构建请求体payload
#         "message": request.message, # 将用户消息作为请求的消息字段
#         "mode": "chat"  # Updated payload to include mode
#     } # payload定义结束
    
#     try: # 尝试发送HTTP请求
#         async with httpx.AsyncClient(timeout=60.0) as client: # 创建异步HTTP客户端, added timeout
#             logger.info(f"Sending request to AnythingLLM: {anything_llm_url} with payload: {payload}")
#             response = await client.post(anything_llm_url, json=payload, headers=headers) # 发送POST请求到AnythingLLM API
            
#             response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            
#             result = response.json() # 解析AnythingLLM API的JSON响应
#             logger.info(f"Received response from AnythingLLM: {result}")
            
#             # Parse AnythingLLM response
#             reply_content = result.get("textResponse") or result.get("response", {}).get("text")
            
#             if not reply_content:
#                 logger.warning("No valid reply content found in AnythingLLM response.")
#                 reply_content = "抱歉，无法获取有效回复。"
                
#             return ChatResponse(reply=reply_content.strip())
    
#     except httpx.HTTPStatusError as e: # Catch HTTP errors from httpx
#         logger.error(f"AnythingLLM API error: {e.response.status_code} - {e.response.text}")
#         raise HTTPException(
#             status_code=e.response.status_code,
#             detail=f"Error from LLM service: {e.response.text}"
#         )
#     except httpx.RequestError as e: # Catch other request errors like timeout or connection errors
#         logger.error(f"HTTP request error to AnythingLLM: {e}")
#         raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
#     except Exception as e: # 捕获其他未知异常
#         logger.error(f"Unexpected error in chat endpoint: {e}") # 日志记录未知错误
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") # 抛出HTTPException，表示未知错误

# @app.get("/api/resources") # 定义/api/resources路径的GET请求处理函数
# async def get_resources( # 异步函数定义
#     category: Optional[str] = Query(None, description="Filter by resource category"), # 可选的category查询参数，用于按分类过滤
#     location: Optional[str] = Query(None, description="Filter by location tag"), # 可选的location查询参数，用于按位置标签过滤
#     limit: int = Query(50, description="Maximum number of records to return") # 可选的limit查询参数，限制返回记录数，默认为50
# ): # 函数参数结束
#     conn = get_db_connection() # 获取数据库连接
#     try: # 尝试执行数据库操作
#         with conn.cursor() as cursor: # 创建一个数据库游标
#             query = "SELECT * FROM resources WHERE 1=1" # 构建基础SQL查询，WHERE 1=1用于方便后续添加条件
#             params = [] # 初始化查询参数列表
            
#             if category: # 如果提供了category查询参数
#                 query += " AND category = %s" # 在查询中添加按category过滤的条件
#                 params.append(category) # 将category值添加到参数列表
                
#             if location: # 如果提供了location查询参数
#                 query += " AND location_tag = %s" # 在查询中添加按location_tag过滤的条件
#                 params.append(location) # 将location值添加到参数列表
                
#             query += " ORDER BY created_at DESC LIMIT %s" # 在查询中添加按创建时间倒序排序和限制数量的条件
#             params.append(limit) # 将limit值添加到参数列表
            
#             cursor.execute(query, params) # 执行SQL查询，并传入参数
#             resources = cursor.fetchall() # 获取所有查询结果
            
#             # Convert decimal types to float for JSON serialization if needed # 如果需要，将decimal类型转换为float以便JSON序列化
#             for resource in resources: # 遍历查询结果中的每个资源字典
#                 for key, value in resource.items(): # 遍历资源字典中的每个键值对
#                     if isinstance(value, bytes): # 如果值是bytes类型
#                         resource[key] = value.decode('utf-8') # 将bytes类型的值解码为UTF-8字符串
            
#             return resources # 返回查询到的资源列表
#     except Exception as e: # 捕获执行数据库操作时可能发生的异常
#         logger.error(f"Error querying database: {e}") # 使用logger记录错误
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") # 抛出HTTPException，表示数据库错误
#     finally: # 无论是否发生异常，最后都会执行
#         conn.close() # 关闭数据库连接

# if __name__ == "__main__": # 判断当前脚本是否作为主程序运行
#     import uvicorn # 导入uvicorn库
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) # 使用uvicorn运行FastAPI应用，监听127.0.0.1的8000端口，开启热重载
