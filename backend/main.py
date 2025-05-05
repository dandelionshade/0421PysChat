from fastapi import FastAPI, HTTPException, Query # 导入构建API所需的FastAPI、HTTPException和Query
from fastapi.middleware.cors import CORSMiddleware # 导入CORS中间件，用于处理跨域请求
from pydantic import BaseModel # 导入Pydantic的BaseModel，用于定义请求体和响应体的数据模型
from typing import List, Optional, Dict, Any # 导入Python类型提示工具
import httpx # 导入httpx库，用于发送HTTP请求
import pymysql # 导入pymysql库，用于连接MySQL数据库
import os # 导入os模块，用于访问环境变量
from dotenv import load_dotenv # 导入load_dotenv函数，用于从.env文件加载环境变量

# Load environment variables # 加载环境变量
load_dotenv() # 调用函数加载环境变量

# AnythingLLM configuration # AnythingLLM服务配置
ANYTHINGLLM_BASE_URL = os.getenv("ANYTHINGLLM_API_BASE_URL", "http://localhost:3001") # 获取AnythingLLM API的基础URL，默认为http://localhost:3001
WORKSPACE_SLUG = os.getenv("ANYTHINGLLM_WORKSPACE_SLUG") # 获取AnythingLLM工作空间的slug
ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY", "") # 获取AnythingLLM API密钥，默认为空字符串

# Database configuration # 数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost") # 获取数据库主机名，默认为localhost
DB_PORT = int(os.getenv("DB_PORT", "3306")) # 获取数据库端口，并转换为整数，默认为3306
DB_USER = os.getenv("DB_USER", "root") # 获取数据库用户名，默认为root
DB_PASSWORD = os.getenv("DB_PASSWORD", "") # 获取数据库密码，默认为空字符串
DB_NAME = os.getenv("DB_NAME", "mental_health_db") # 获取数据库名称，默认为mental_health_db

app = FastAPI(title="Mental Health Chatbot API") # 创建FastAPI应用实例，并设置标题

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
    response: str # 响应内容，类型为字符串

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
        print(f"Error connecting to MySQL: {e}") # 打印错误信息
        raise HTTPException(status_code=500, detail="Database connection error") # 抛出HTTPException，表示数据库连接错误

@app.get("/") # 定义根路径的GET请求处理函数
async def root(): # 异步函数定义
    return {"status": "API is running"} # 返回API运行状态信息

@app.post("/api/chat", response_model=ChatResponse) # 定义/api/chat路径的POST请求处理函数，响应模型为ChatResponse
async def chat(request: ChatRequest): # 异步函数定义，接收ChatRequest类型的请求体
    if not WORKSPACE_SLUG: # 检查是否配置了AnythingLLM工作空间slug
        raise HTTPException(status_code=500, detail="AnythingLLM workspace not configured") # 如果未配置，则抛出HTTPException
    
    # Prepare the request to AnythingLLM API # 准备发送到AnythingLLM API的请求
    anything_llm_url = f"{ANYTHINGLLM_BASE_URL}/api/workspaces/{WORKSPACE_SLUG}/chat/prompt" # 构建AnythingLLM聊天API的完整URL
    
    headers = {} # 初始化请求头字典
    if ANYTHINGLLM_API_KEY: # 如果存在AnythingLLM API密钥
        headers["Authorization"] = f"Bearer {ANYTHINGLLM_API_KEY}" # 在请求头中添加Authorization字段
    
    payload = { # 构建请求体payload
        "message": request.message, # 将用户消息作为请求的消息字段
        "streaming": False  # Set to True if you want to implement streaming responses # 设置streaming为False，表示不使用流式响应（如需流式响应可设为True）
    } # payload定义结束
    
    try: # 尝试发送HTTP请求
        async with httpx.AsyncClient() as client: # 创建异步HTTP客户端
            response = await client.post(anything_llm_url, json=payload, headers=headers) # 发送POST请求到AnythingLLM API
            
            if response.status_code != 200: # 检查响应状态码是否不是200
                print(f"AnythingLLM API error: {response.status_code}, {response.text}") # 打印AnythingLLM API的错误信息
                raise HTTPException( # 抛出HTTPException
                    status_code=response.status_code, # 使用AnythingLLM API返回的状态码
                    detail=f"Error from LLM service: {response.text}" # 错误详情包含AnythingLLM API的响应文本
                ) # HTTPException结束
            
            data = response.json() # 解析AnythingLLM API的JSON响应
            
            # The actual response structure depends on AnythingLLM's API # 实际的响应结构取决于AnythingLLM的API
            # Adjust this according to the actual response format # 根据实际的响应格式调整此处代码
            if isinstance(data, dict) and "text" in data: # 如果响应是字典且包含'text'键
                return {"response": data["text"]} # 返回包含'text'值的字典作为响应
            elif isinstance(data, str): # 如果响应是字符串
                return {"response": data} # 返回包含该字符串的字典作为响应
            else: # 如果响应是其他格式
                return {"response": str(data)} # 将整个响应数据转换为字符串后返回
    
    except httpx.HTTPError as e: # 捕获httpx的HTTP错误
        print(f"HTTP error: {e}") # 打印HTTP错误信息
        raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}") # 抛出HTTPException，表示HTTP错误
    except Exception as e: # 捕获其他未知异常
        print(f"Unexpected error: {e}") # 打印未知错误信息
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}") # 抛出HTTPException，表示未知错误

@app.get("/api/resources") # 定义/api/resources路径的GET请求处理函数
async def get_resources( # 异步函数定义
    category: Optional[str] = Query(None, description="Filter by resource category"), # 可选的category查询参数，用于按分类过滤
    location: Optional[str] = Query(None, description="Filter by location tag"), # 可选的location查询参数，用于按位置标签过滤
    limit: int = Query(50, description="Maximum number of records to return") # 可选的limit查询参数，限制返回记录数，默认为50
): # 函数参数结束
    conn = get_db_connection() # 获取数据库连接
    try: # 尝试执行数据库操作
        with conn.cursor() as cursor: # 创建一个数据库游标
            query = "SELECT * FROM resources WHERE 1=1" # 构建基础SQL查询，WHERE 1=1用于方便后续添加条件
            params = [] # 初始化查询参数列表
            
            if category: # 如果提供了category查询参数
                query += " AND category = %s" # 在查询中添加按category过滤的条件
                params.append(category) # 将category值添加到参数列表
                
            if location: # 如果提供了location查询参数
                query += " AND location_tag = %s" # 在查询中添加按location_tag过滤的条件
                params.append(location) # 将location值添加到参数列表
                
            query += " ORDER BY created_at DESC LIMIT %s" # 在查询中添加按创建时间倒序排序和限制数量的条件
            params.append(limit) # 将limit值添加到参数列表
            
            cursor.execute(query, params) # 执行SQL查询，并传入参数
            resources = cursor.fetchall() # 获取所有查询结果
            
            # Convert decimal types to float for JSON serialization if needed # 如果需要，将decimal类型转换为float以便JSON序列化
            for resource in resources: # 遍历查询结果中的每个资源字典
                for key, value in resource.items(): # 遍历资源字典中的每个键值对
                    if isinstance(value, bytes): # 如果值是bytes类型
                        resource[key] = value.decode('utf-8') # 将bytes类型的值解码为UTF-8字符串
            
            return resources # 返回查询到的资源列表
    except Exception as e: # 捕获执行数据库操作时可能发生的异常
        print(f"Error querying database: {e}") # 打印数据库查询错误信息
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") # 抛出HTTPException，表示数据库错误
    finally: # 无论是否发生异常，最后都会执行
        conn.close() # 关闭数据库连接

if __name__ == "__main__": # 判断当前脚本是否作为主程序运行
    import uvicorn # 导入uvicorn库
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) # 使用uvicorn运行FastAPI应用，监听127.0.0.1的8000端口，开启热重载
