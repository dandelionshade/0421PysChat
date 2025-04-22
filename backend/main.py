from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AnythingLLM configuration
ANYTHINGLLM_BASE_URL = os.getenv("ANYTHINGLLM_API_BASE_URL", "http://localhost:3001")
WORKSPACE_SLUG = os.getenv("ANYTHINGLLM_WORKSPACE_SLUG")
ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY", "")

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "mental_health_db")

app = FastAPI(title="Mental Health Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Database connection helper
def get_db_connection():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

@app.get("/")
async def root():
    return {"status": "API is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not WORKSPACE_SLUG:
        raise HTTPException(status_code=500, detail="AnythingLLM workspace not configured")
    
    # Prepare the request to AnythingLLM API
    anything_llm_url = f"{ANYTHINGLLM_BASE_URL}/api/workspaces/{WORKSPACE_SLUG}/chat/prompt"
    
    headers = {}
    if ANYTHINGLLM_API_KEY:
        headers["Authorization"] = f"Bearer {ANYTHINGLLM_API_KEY}"
    
    payload = {
        "message": request.message,
        "streaming": False  # Set to True if you want to implement streaming responses
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(anything_llm_url, json=payload, headers=headers)
            
            if response.status_code != 200:
                print(f"AnythingLLM API error: {response.status_code}, {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error from LLM service: {response.text}"
                )
            
            data = response.json()
            
            # The actual response structure depends on AnythingLLM's API
            # Adjust this according to the actual response format
            if isinstance(data, dict) and "text" in data:
                return {"response": data["text"]}
            elif isinstance(data, str):
                return {"response": data}
            else:
                return {"response": str(data)}
    
    except httpx.HTTPError as e:
        print(f"HTTP error: {e}")
        raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/api/resources")
async def get_resources(
    category: Optional[str] = Query(None, description="Filter by resource category"),
    location: Optional[str] = Query(None, description="Filter by location tag"),
    limit: int = Query(50, description="Maximum number of records to return")
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
                query += " AND location_tag = %s"
                params.append(location)
                
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            resources = cursor.fetchall()
            
            # Convert decimal types to float for JSON serialization if needed
            for resource in resources:
                for key, value in resource.items():
                    if isinstance(value, bytes):
                        resource[key] = value.decode('utf-8')
            
            return resources
    except Exception as e:
        print(f"Error querying database: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
