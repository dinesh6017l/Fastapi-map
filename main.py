from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "aws-1-ap-south-1.pooler.supabase.com")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "postgres.htotuqmvdbxwzfbrhjwc")
DB_PASS = os.getenv("DB_PASS", "DINBHAN#2024")
DB_NAME = os.getenv("DB_NAME", "postgres")

@app.get("/")
async def serve_html():
    return FileResponse("index.html")

@app.get("/collections")
async def get_collections():
    conn = await asyncpg.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS, database=DB_NAME
    )
    rows = await conn.fetch("""
        SELECT f_table_name AS name, f_geometry_column AS geom_col, type
        FROM geometry_columns
        WHERE f_table_schema = 'public'
    """)
    await conn.close()
    return [dict(r) for r in rows]

@app.get("/collections/{table}/items")
async def get_features(table: str, limit: int = 1000):
    conn = await asyncpg.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS, database=DB_NAME
    )
    rows = await conn.fetch(f"""
        SELECT ST_AsGeoJSON(t.*)::text AS feature
        FROM (SELECT * FROM public.{table} LIMIT $1) t
    """, limit)
    await conn.close()
    features = [json.loads(row["feature"]) for row in rows]
    return {
        "type": "FeatureCollection",
        "features": features
    }