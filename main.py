import os
import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="CloudTask Analytics Microservice",
    description="Python FastAPI analytics and insights service for CloudTask Manager",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    is_localhost = db_host in ("127.0.0.1", "localhost")
    sslmode = "disable" if is_localhost else "require"
    
    return psycopg2.connect(
        host=db_host,
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "cloud_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "DevOpsSecure2026!"),
        sslmode=sslmode,
        connect_timeout=5
    )

@app.get("/health")
@app.get("/api/analytics/health")
def health_check():
    db_status = "disconnected"
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "service": "cloudtask-analytics",
        "tier": "Tier 2 (Microservice B - Python FastAPI)",
        "status": "healthy",
        "port": 8000,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "database": {
            "tier": "Tier 3 (Database Layer)",
            "status": db_status
        }
    }

@app.get("/api/analytics/stats")
def get_task_statistics():
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Query task counts and aggregations
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed,
                    COUNT(*) FILTER (WHERE status != 'completed') as pending,
                    COUNT(*) FILTER (WHERE priority = 'high') as high_priority,
                    COUNT(*) FILTER (WHERE priority = 'medium') as medium_priority,
                    COUNT(*) FILTER (WHERE priority = 'low') as low_priority
                FROM tasks;
            """)
            row = cur.fetchone()
        conn.close()

        total = row["total"] or 0
        completed = row["completed"] or 0
        pending = row["pending"] or 0
        completion_rate = round((completed / total * 100), 1) if total > 0 else 0.0

        if completion_rate >= 75:
            score = "Elite 🚀"
        elif completion_rate >= 50:
            score = "Productive ⚡"
        elif completion_rate >= 25:
            score = "In Progress 📈"
        else:
            score = "Getting Started ⏳"

        return {
            "engine": "Python 3.12 + FastAPI",
            "microservice": "Tier 2 (Analytics)",
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "completion_rate": completion_rate,
            "productivity_score": score,
            "priority_breakdown": {
                "high": row["high_priority"] or 0,
                "medium": row["medium_priority"] or 0,
                "low": row["low_priority"] or 0
            },
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database aggregation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
