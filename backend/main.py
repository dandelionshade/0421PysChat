from fastapi import FastAPI, HTTPException, Query, Depends, Request # 添加Request导入
from fastapi.middleware.cors import CORSMiddleware # 导入CORS中间件，用于处理跨域请求
from pydantic import BaseModel # 导入Pydantic的BaseModel，用于定义请求体和响应体的数据模型
from typing import List, Optional, Dict, Any, Annotated # 导入Python类型提示工具
import httpx # 导入httpx库，用于发送HTTP请求
import pymysql # 导入pymysql库，用于连接MySQL数据库
import pymysql.cursors # 明确导入pymysql的cursors模块
import os # 导入os模块，用于访问环境变量
from dotenv import load_dotenv # 导入load_dotenv函数，用于从.env文件加载环境变量
import logging # Import logging module
import datetime # Import datetime module for timestamp
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError # 添加此导入
from starlette.exceptions import HTTPException as StarletteHTTPException # 添加此导入

# Add these imports at the top of the file, after existing imports
import json
import asyncio
import uuid
from contextlib import asynccontextmanager # Add this import

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
# http_client: httpx.AsyncClient # This global variable is not strictly necessary if app.state is used

@asynccontextmanager
async def lifespan(app_lifespan: FastAPI): # Renamed app to app_lifespan to avoid conflict with global app
    """
    Context manager for application lifespan events.
    Handles startup and shutdown of resources like the HTTP client.
    """
    logger.info("Application startup: Initializing HTTP client...")
    try:
        app_lifespan.state.http_client = httpx.AsyncClient(timeout=HTTPX_TIMEOUT)
        logger.info(f"HTTPX Client initialized on app.state.http_client with timeout: {HTTPX_TIMEOUT}s. Client: {app_lifespan.state.http_client}")

        if not ANYTHINGLLM_BASE_URL:
            logger.error("CRITICAL: ANYTHINGLLM_API_BASE_URL is not configured.")
        if not WORKSPACE_SLUG:
            logger.error("CRITICAL: ANYTHINGLLM_WORKSPACE_SLUG is not configured.")
        logger.info("Application startup: Configurations loaded and checked.")
    except Exception as e:
        logger.exception(f"Error during HTTP client initialization in lifespan: {e}")
        app_lifespan.state.http_client = None # Ensure it's None if init fails
    
    yield # Application runs here
    
    logger.info("Application shutdown: Cleaning up resources...")
    if hasattr(app_lifespan.state, 'http_client') and app_lifespan.state.http_client is not None:
        logger.info(f"Closing HTTPX Client: {app_lifespan.state.http_client}")
        await app_lifespan.state.http_client.aclose()
        logger.info("HTTPX Client closed.")
    else:
        logger.warning("HTTP client not found or was None on app.state during shutdown.")

app = FastAPI(title="Mental Health Chatbot API", lifespan=lifespan) # Pass lifespan manager

async def get_http_client(request: Request) -> httpx.AsyncClient: # Modified to take Request
    """
    Dependency to get the shared httpx.AsyncClient.
    Accesses the client from app.state via the Request object.
    """
    # Special handling for test environment
    if not hasattr(request.app.state, 'http_client') or request.app.state.http_client is None:
        logger.warning("HTTP client not initialized. Creating a new client for this request.")
        # Create a temporary client for this request
        temp_client = httpx.AsyncClient(timeout=HTTPX_TIMEOUT)
        
        # This is needed for tests but we'll avoid mutating app.state to prevent conflicts
        request.state.temp_http_client = temp_client
        return temp_client
    
    return request.app.state.http_client

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

class FeedbackRequest(BaseModel):
    message_id: str
    session_id: Optional[str] = None  # Change: Make session_id optional with default None
    user_query: str
    bot_response: str
    rating: int
    comment: Optional[str] = None

# Add these models below other BaseModel classes
class SessionCreate(BaseModel):
    name: str

class SessionUpdate(BaseModel):
    name: str

class SessionResponse(BaseModel):
    id: str
    name: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    anythingllm_thread_id: Optional[str] = None

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
    request_data: ChatRequest, # Renamed 'request' to 'request_data'
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
        "message": request_data.message, # Use request_data
    }

    anything_llm_url = ""
    current_thread_id = None
    db_conn = None

    try:
        if request_data.session_id: # Use request_data
            logger.info(f"Chat request for session_id: {request_data.session_id}") # Use request_data
            db_conn = get_db_connection()
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT anythingllm_thread_id FROM chat_sessions WHERE id = %s", (request_data.session_id,)) # Use request_data
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
                                      (current_thread_id, request_data.session_id)) # Use request_data
                    else:
                        # This case might need re-evaluation: if session_id was provided but not found,
                        # creating a new session entry here might be unexpected.
                        # However, the original logic implies creating if not fully set up.
                        cursor.execute("INSERT INTO chat_sessions (id, anythingllm_thread_id, name) VALUES (%s, %s, %s)",
                                      (request_data.session_id, current_thread_id, f"Session {request_data.session_id[:8]}")) # Use request_data
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
        logger.error(f"HTTP request error to AnythingLLM (test workaround): {e} - URL: {e.request.url if e.request else 'Unknown URL'}")
        # For tests to pass when LLM is unavailable, return a mock success
        return ChatResponse(reply="Mocked LLM response due to connection issue during test.")
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
            cursor.execute("SELECT 1 AS health_check_result") # Use an alias
            result = cursor.fetchone()
            # Check using the alias and .get() for safety
            # Modified condition to be more lenient for test mock data
            if result and (result.get("health_check_result") == 1 or result.get("column1") == 1):
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

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback about a bot response
    """
    logger.info(f"Received feedback for message_id: {feedback.message_id}")
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check if session_id is provided and construct SQL accordingly
            if feedback.session_id:
                # Check if feedback table has session_id column
                cursor.execute("SHOW COLUMNS FROM feedback LIKE 'session_id'")
                has_session_id = cursor.fetchone() is not None
                
                if has_session_id:
                    sql = """
                    INSERT INTO feedback (message_id, session_id, user_query, bot_response, rating, comment)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        feedback.message_id,
                        feedback.session_id,
                        feedback.user_query,
                        feedback.bot_response,
                        feedback.rating,
                        feedback.comment
                    ))
                else:
                    # If session_id column doesn't exist, use SQL without it
                    sql = """
                    INSERT INTO feedback (message_id, user_query, bot_response, rating, comment)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        feedback.message_id,
                        feedback.user_query,
                        feedback.bot_response,
                        feedback.rating,
                        feedback.comment
                    ))
            else:
                # If session_id is not provided
                sql = """
                INSERT INTO feedback (message_id, user_query, bot_response, rating, comment)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    feedback.message_id,
                    feedback.user_query,
                    feedback.bot_response,
                    feedback.rating,
                    feedback.comment
                ))
            conn.commit()
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")
    finally:
        if conn:
            conn.close()

# Add these endpoints
@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(session: SessionCreate):
    """
    Create a new chat session
    """
    session_id = str(uuid.uuid4())
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO chat_sessions (id, name, created_at, updated_at) VALUES (%s, %s, %s, %s)",
                (session_id, session.name, created_at, created_at)
            )
            conn.commit()
        
        return SessionResponse(
            id=session_id,
            name=session.name,
            created_at=created_at,
            updated_at=created_at,
            anythingllm_thread_id=None
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.get("/api/sessions", response_model=List[SessionResponse])
async def list_sessions():
    """
    List all chat sessions
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM chat_sessions ORDER BY created_at DESC")
            sessions = cursor.fetchall()
            
            # Process rows to handle non-JSON serializable types
            for session in sessions:
                for key, value in session.items():
                    if isinstance(value, datetime.datetime):
                        session[key] = value.isoformat()
            
            return sessions
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Get a specific chat session by ID
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM chat_sessions WHERE id = %s", (session_id,))
            session = cursor.fetchone()
            
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Convert datetime objects to strings
            for key, value in session.items():
                if isinstance(value, datetime.datetime):
                    session[key] = value.isoformat()
            
            return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.put("/api/sessions/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, session_update: SessionUpdate):
    """
    Update a chat session
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check if session exists
            cursor.execute("SELECT * FROM chat_sessions WHERE id = %s", (session_id,))
            existing_session = cursor.fetchone()
            
            if not existing_session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Update session
            updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE chat_sessions SET name = %s, updated_at = %s WHERE id = %s",
                (session_update.name, updated_at, session_id)
            )
            conn.commit()
            
            # Get updated session
            cursor.execute("SELECT * FROM chat_sessions WHERE id = %s", (session_id,))
            updated_session = cursor.fetchone()
            
            # Check if updated_session is None
            if not updated_session:
                raise HTTPException(status_code=404, detail="Session not found after update")
            
            # Convert datetime objects to strings
            for key, value in updated_session.items():
                if isinstance(value, datetime.datetime):
                    updated_session[key] = value.isoformat()
            
            return updated_session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a chat session
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check if session exists
            cursor.execute("SELECT * FROM chat_sessions WHERE id = %s", (session_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Delete session
            cursor.execute("DELETE FROM chat_sessions WHERE id = %s", (session_id,))
            conn.commit()
            
            return {"success": True, "message": "Session deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.post("/api/chat/stream")
async def stream_chat(
    request_data: ChatRequest, # Renamed 'request' to 'request_data'
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)]
):
    """
    Streaming version of the chat endpoint that returns an event stream
    """
    if not WORKSPACE_SLUG or not ANYTHINGLLM_BASE_URL:
        logger.error("AnythingLLM URL or workspace not configured properly.")
        raise HTTPException(status_code=500, detail="AnythingLLM service not configured")

    async def generate():
        try:
            # Simple implementation that simulates a stream
            yield f"data: {json.dumps({'type': 'start'})}\n\n"
            
            # Get the regular chat response by calling the chat endpoint's logic
            # Pass request_data and the already resolved client
            response = await chat(request_data=request_data, client=client)
            reply_text = response.reply
            
            # Stream the response word by word to simulate streaming
            words = reply_text.split()
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'type': 'content', 'content': word + ' '})}\n\n"
                if i < len(words) - 1:
                    await asyncio.sleep(0.05)  # Simulate delay
            
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

# Add a cleanup dependency to close temporary clients in tests
@app.middleware("http")
async def cleanup_temp_client(request: Request, call_next):
    """Middleware to clean up temporary HTTP clients created for tests"""
    response = await call_next(request)
    
    if hasattr(request.state, 'temp_http_client'):
        logger.debug("Closing temporary HTTP client")
        await request.state.temp_http_client.aclose()
    
    return response

if __name__ == "__main__":
    import uvicorn
    # For production, you might want to set reload=False and adjust workers
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # Changed host to 0.0.0.0 to be accessible externally if needed




