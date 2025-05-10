from fastapi import FastAPI, HTTPException, Query, Depends # 导入构建API所需的FastAPI、HTTPException、Query和Depends
from fastapi.middleware.cors import CORSMiddleware # 导入CORS中间件，用于处理跨域请求
from pydantic import BaseModel # 导入Pydantic的BaseModel，用于定义请求体和响应体的数据模型
from typing import List, Optional, Dict, Any, Annotated # 导入Python类型提示工具
import httpx # 导入httpx库，用于发送HTTP请求
import pymysql # 导入pymysql库，用于连接MySQL数据库
import os # 导入os模块，用于访问环境变量
from dotenv import load_dotenv # 导入load_dotenv函数，用于从.env文件加载环境变量
import logging # Import logging module

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
    global http_client
    app.state.http_client = httpx.AsyncClient(timeout=HTTPX_TIMEOUT)
    logger.info(f"HTTPX Client initialized with timeout: {HTTPX_TIMEOUT}s")

    if not ANYTHINGLLM_BASE_URL:
        logger.error("CRITICAL: ANYTHINGLLM_API_BASE_URL is not configured.")
        # You might want to raise an exception here or prevent app startup
    if not WORKSPACE_SLUG:
        logger.error("CRITICAL: ANYTHINGLLM_WORKSPACE_SLUG is not configured.")
        # You might want to raise an exception here or prevent app startup
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
    if not WORKSPACE_SLUG or not ANYTHINGLLM_BASE_URL: # Double check, though validated at startup
        logger.error("AnythingLLM URL or workspace not configured properly.")
        raise HTTPException(status_code=500, detail="AnythingLLM service not configured")

    anything_llm_url = f"{ANYTHINGLLM_BASE_URL}/api/v1/workspace/{WORKSPACE_SLUG}/chat"

    headers = {"Content-Type": "application/json"}
    if ANYTHINGLLM_API_KEY:
        headers["Authorization"] = f"Bearer {ANYTHINGLLM_API_KEY}"

    payload = {
        "message": request.message,
        "mode": "chat" # Ensure this mode is correct for your AnythingLLM version
    }

    try:
        logger.info(f"Sending request to AnythingLLM: {anything_llm_url} with payload: {{message: '{request.message[:50]}...', mode: 'chat'}}") # Log truncated message
        response = await client.post(anything_llm_url, json=payload, headers=headers)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

        result = response.json()
        logger.debug(f"Raw response from AnythingLLM: {result}") # Use debug level for raw full response

        # --- Refined Response Parsing (Consult AnythingLLM API docs for the exact structure) ---
        # Example: Assuming the main text response is always in 'textResponse'
        # Or, if it's nested like in older versions, you might look for `result.get('textResponse', {}).get('text')`
        # For this example, let's assume a direct key, but you MUST verify this with AnythingLLM's docs.
        reply_content = None
        if "textResponse" in result and result["textResponse"] is not None:
            reply_content = result["textResponse"]
        elif "response" in result and isinstance(result["response"], dict) and "text" in result["response"] and result["response"]["text"] is not None:
            # Fallback for a potentially older or different structure
            reply_content = result["response"]["text"]
        else:
            # If you expect citations or other data, parse them here.
            # For example: sources = result.get("sources", [])
            logger.warning(f"No standard 'textResponse' or 'response.text' found in AnythingLLM response. Full response: {result}")
            reply_content = "抱歉，无法从LLM服务获取到有效的文本回复内容。"

        return ChatResponse(reply=str(reply_content).strip()) # Ensure reply is string

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
        logger.exception(f"Unexpected error in chat endpoint: {e}") # Use logger.exception to include stack trace
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")


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
