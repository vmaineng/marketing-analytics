
import os
import logging
from datetime import date, timedelta
from contextlib import asynccontextmanager
 
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv
 
from agent import create_scheduler, run_ingestion_agent

load_dotenv()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
 
supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_KEY"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()
    log.info("Scheduler started — agent will run daily at 6am PT")
    yield
    scheduler.shutdown()
    log.info("Scheduler stopped")

app = FastAPI(title="Meta Ads Dashboard API", lifespan=lifespan)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # update to your Next.js URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def date_range_bounds(days: int = 7) -> tuple[str, str]:
    """Returns (start_date, end_date) as ISO strings for the last N days."""
    end = date.today() - timedelta(days=1)      # yesterday (most recent ingested)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()

@app.get("/")
def root():
    return {"status": "ok"}

app.get("/api/overview")
def get_overview(days: int = Query(default=7, ge=1, le=90)):
    start, end = date_range_bounds(days)
 
    result = (
        supabase.table("daily_metrics")
        .select("impressions, reach, clicks, conversions, spend")
        .eq("level", "campaign")
        .gte("date", start)
        .lte("date", end)
        .execute()
    )
 
    if not result.data:
        return {
            "date_range": {"start": start, "end": end},
            "totals": {
                "impressions": 0,
                "reach": 0,
                "clicks": 0,
                "conversions": 0,
                "spend": 0.0,
            }
        }
 
    rows = result.data
    totals = {
        "impressions": sum(r["impressions"] for r in rows),
        "reach": sum(r["reach"] for r in rows),
        "clicks": sum(r["clicks"] for r in rows),
        "conversions": sum(r["conversions"] for r in rows),
        "spend": round(sum(r["spend"] for r in rows), 2),
    }
 
    return {
        "date_range": {"start": start, "end": end},
        "totals": totals,
    }

@app.post("/api/agent/run")
async def trigger_agent(target_date: str = Query(default=None)):
    log.info(f"Manual agent trigger for date: {target_date or 'yesterday'}")
    await run_ingestion_agent(target_date)
    return {"status": "completed", "date": target_date or (date.today() - timedelta(days=1)).isoformat()}