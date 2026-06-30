import os
import json
import logging
import httpx
from datetime import date, timedelta
from typing import Any

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

import anthropic
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_KEY"],
)
 
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

META_ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
META_AD_ACCOUNT_ID = os.environ["META_AD_ACCOUNT_ID"] 
META_API_VERSION = "v19.0"
META_BASE = f"https://graph.facebook.com/{META_API_VERSION}"

SUPABASE_AD_ACCOUNT_UUID = os.environ["SUPABASE_AD_ACCOUNT_UUID"]

TOOLS = [
       {
        "name": "fetch_meta_campaigns",
        "description": (
            "Fetch all active campaigns from the Meta Marketing API "
            "for the configured ad account. Returns a list of campaigns "
            "with their IDs, names, objectives, and statuses."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "fetch_meta_insights",
        "description": (
            "Fetch daily performance metrics from the Meta Marketing API "
            "for a specific campaign, ad set, or ad on a given date. "
            "Returns impressions, reach, clicks, conversions, spend, and derived metrics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "The Meta ID of the campaign, ad set, or ad.",
                },
                "level": {
                    "type": "string",
                    "enum": ["campaign", "ad_set", "ad"],
                    "description": "The level of the entity to fetch insights for.",
                },
                "target_date": {
                    "type": "string",
                    "description": "Date to fetch metrics for in YYYY-MM-DD format.",
                },
            },
            "required": ["entity_id", "level", "target_date"],
        },
    },
    {
        "name": "upsert_to_supabase",
        "description": (
            "Insert or update a daily metrics row in the Supabase database. "
            "If a row already exists for this date + level + ref_id, it will be updated."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "level": {"type": "string", "enum": ["campaign", "ad_set", "ad"]},
                "ref_id": {"type": "string", "description": "UUID of the campaign, ad set, or ad in Supabase."},
                "impressions": {"type": "integer"},
                "reach": {"type": "integer"},
                "clicks": {"type": "integer"},
                "conversions": {"type": "integer"},
                "spend": {"type": "number"},
                "cpm": {"type": "number"},
                "ctr": {"type": "number"},
                "cpc": {"type": "number"},
                "cost_per_conversion": {"type": "number"},
                "frequency": {"type": "number"},
            },
            "required": ["date", "level", "ref_id", "impressions", "reach", "spend"],
        },
    },
     {
        "name": "flag_anomaly",
        "description": (
            "Log and persist an anomaly when something unusual is detected in the metrics, "
            "such as a spend spike, zero impressions on an active campaign, "
            "or a dramatic drop in conversions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Meta ID of the affected entity."},
                "level": {"type": "string", "enum": ["campaign", "ad_set", "ad"]},
                "anomaly_type": {
                    "type": "string",
                    "enum": ["spend_spike", "zero_impressions", "conversion_drop", "reach_drop", "other"],
                },
                "description": {"type": "string", "description": "Human-readable description of the anomaly."},
                "metric_value": {"type": "number", "description": "The metric value that triggered the flag."},
                "date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["entity_id", "level", "anomaly_type", "description", "date"],
        },
    },
]

async def fetch_meta_campaigns() -> dict:
    url = f"{META_BASE}/{META_AD_ACCOUNT_ID}/campaigns"
    params = {
        "fields": "id,name,objective,status,created_time,updated_time",
        "filtering": '[{"field":"effective_status","operator":"IN","value":["ACTIVE","PAUSED"]}]',
        "access_token": META_ACCESS_TOKEN,
        "limit": 100,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
 
    campaigns = data.get("data", [])
    log.info(f"Fetched {len(campaigns)} campaigns from Meta")
 
    # Upsert into Supabase so ref_ids stay current
    for c in campaigns:
        supabase.table("campaigns").upsert({
            "campaign_id": c["id"],
            "name": c["name"],
            "objective": c.get("objective"),
            "status": c.get("status", "UNKNOWN"),
            "account_id": SUPABASE_AD_ACCOUNT_UUID,
        }, on_conflict="campaign_id").execute()
 
    return {"campaigns": campaigns}
 
 
async def fetch_meta_insights(entity_id: str, level: str, target_date: str) -> dict:
    level_map = {"campaign": "campaign", "ad_set": "adset", "ad": "ad"}
    url = f"{META_BASE}/{entity_id}/insights"
    params = {
        "fields": "impressions,reach,clicks,conversions,spend,cpm,ctr,cpc,cost_per_conversion,frequency",
        "time_range": json.dumps({"since": target_date, "until": target_date}),
        "level": level_map[level],
        "access_token": META_ACCESS_TOKEN,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
 
    rows = data.get("data", [])
    if not rows:
        log.warning(f"No insights returned for {level} {entity_id} on {target_date}")
        return {"insights": None}
 
    row = rows[0]
    return {
        "insights": {
            "impressions": int(row.get("impressions", 0)),
            "reach": int(row.get("reach", 0)),
            "clicks": int(row.get("clicks", 0)),
            "conversions": int(row.get("conversions", 0)),
            "spend": float(row.get("spend", 0)),
            "cpm": float(row.get("cpm", 0)) if row.get("cpm") else None,
            "ctr": float(row.get("ctr", 0)) if row.get("ctr") else None,
            "cpc": float(row.get("cpc", 0)) if row.get("cpc") else None,
            "cost_per_conversion": float(row.get("cost_per_conversion", 0)) if row.get("cost_per_conversion") else None,
            "frequency": float(row.get("frequency", 0)) if row.get("frequency") else None,
        }
    }
 
 
async def upsert_to_supabase(payload: dict) -> dict:
    # Resolve ref_id from Meta entity ID via Supabase
    level = payload["level"]
    table_map = {"campaign": "campaigns", "ad_set": "ad_sets", "ad": "ads"}
    id_col_map = {"campaign": "campaign_id", "ad_set": "ad_set_id", "ad": "ad_id"}
 
    result = (
        supabase.table(table_map[level])
        .select("id")
        .eq(id_col_map[level], payload["ref_id"])
        .single()
        .execute()
    )
 
    if not result.data:
        log.error(f"Could not find {level} with Meta ID {payload['ref_id']} in Supabase")
        return {"success": False, "error": "ref_id not found in DB"}
 
    supabase_uuid = result.data["id"]
 
    row = {
        "date": payload["date"],
        "level": level,
        "ref_id": supabase_uuid,
        "impressions": payload.get("impressions", 0),
        "reach": payload.get("reach", 0),
        "clicks": payload.get("clicks", 0),
        "conversions": payload.get("conversions", 0),
        "spend": payload.get("spend", 0),
        "cpm": payload.get("cpm"),
        "ctr": payload.get("ctr"),
        "cpc": payload.get("cpc"),
        "cost_per_conversion": payload.get("cost_per_conversion"),
        "frequency": payload.get("frequency"),
    }
 
    supabase.table("daily_metrics").upsert(row, on_conflict="date,level,ref_id").execute()
    log.info(f"Upserted {level} metrics for {payload['date']}")
    return {"success": True}
 
 
async def flag_anomaly(payload: dict) -> dict:
    log.warning(
        f"[ANOMALY] {payload['anomaly_type'].upper()} | "
        f"{payload['level']} {payload['entity_id']} | "
        f"{payload['date']} | {payload['description']}"
    )
    supabase.table("anomalies").insert({
        "entity_id": payload["entity_id"],
        "level": payload["level"],
        "anomaly_type": payload["anomaly_type"],
        "description": payload["description"],
        "metric_value": payload.get("metric_value"),
        "date": payload["date"],
    }).execute()
    return {"flagged": True}
 
 
# ============================================
# Tool dispatcher
# ============================================
 
async def run_tool(name: str, inputs: dict) -> Any:
    if name == "fetch_meta_campaigns":
        return await fetch_meta_campaigns()
    elif name == "fetch_meta_insights":
        return await fetch_meta_insights(**inputs)
    elif name == "upsert_to_supabase":
        return await upsert_to_supabase(inputs)
    elif name == "flag_anomaly":
        return await flag_anomaly(inputs)
    else:
        return {"error": f"Unknown tool: {name}"}
 
 
# ============================================
# Agent loop
# ============================================
 
async def run_ingestion_agent(target_date: str | None = None):
    if not target_date:
        target_date = (date.today() - timedelta(days=1)).isoformat()  # yesterday
 
    log.info(f"Starting Meta ads ingestion agent for {target_date}")
 
    system_prompt = f"""You are a Meta Ads data ingestion agent. Your job is to:
 
1. Fetch all active and paused campaigns from the Meta Marketing API
2. For each campaign, fetch daily performance metrics for {target_date}
3. Upsert all metrics into the Supabase database
4. Flag any anomalies you detect, such as:
   - Active campaigns with 0 impressions
   - Spend that is unusually high (over $1000 in a single day for a single campaign)
   - Conversions that dropped to 0 when the campaign was previously performing
   - Frequency above 5 (ad fatigue risk)
 
Be thorough. Process every campaign returned. After upserting metrics, always check
the values for anomalies before moving on to the next campaign.
 
Today's ingestion date: {target_date}
"""
 
    messages = [{"role": "user", "content": f"Run the daily ingestion for {target_date}."}]
 
    # Agentic loop — keep going until Claude stops calling tools
    while True:
        response = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )
 
        log.info(f"Agent stop reason: {response.stop_reason}")
 
        # Add Claude's response to message history
        messages.append({"role": "assistant", "content": response.content})
 
        # If Claude is done, exit loop
        if response.stop_reason == "end_turn":
            final_text = next(
                (b.text for b in response.content if hasattr(b, "text")), ""
            )
            log.info(f"Agent finished: {final_text}")
            break
 
        # If Claude wants to use tools, run them and feed results back
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    log.info(f"Agent calling tool: {block.name} with {block.input}")
                    result = await run_tool(block.name, block.input)
                    log.info(f"Tool result: {result}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    })
 
            messages.append({"role": "user", "content": tool_results})
 
    log.info("Ingestion agent run complete")
 
 
# ============================================
# Scheduler (plug into your FastAPI app)
# ============================================
 
def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_ingestion_agent,
        trigger="cron",
        hour=6,          # runs at 6am daily
        minute=0,
        timezone="America/Los_Angeles",
        id="meta_ingestion_agent",
        replace_existing=True,
    )
    return scheduler