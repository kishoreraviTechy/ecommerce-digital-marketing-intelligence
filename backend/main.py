import os
from datetime import date, datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./marketing.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    channel = Column(String(60), nullable=False)
    status = Column(String(30), default="Active")
    spend = Column(Float, default=0)
    revenue = Column(Float, default=0)
    clicks = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    start_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(200), nullable=False)
    search_volume = Column(Integer, default=0)
    difficulty = Column(Integer, default=0)
    position = Column(Integer, default=0)
    url = Column(String(500), default="")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-commerce Marketing Intelligence API", version="1.0.0")
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

class CampaignIn(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    channel: str = "Google Ads"
    status: str = "Active"
    spend: float = Field(default=0, ge=0)
    revenue: float = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    impressions: int = Field(default=0, ge=0)
    conversions: int = Field(default=0, ge=0)
    start_date: date = Field(default_factory=date.today)

class KeywordIn(BaseModel):
    keyword: str = Field(min_length=2, max_length=200)
    search_volume: int = Field(default=0, ge=0)
    difficulty: int = Field(default=0, ge=0, le=100)
    position: int = Field(default=0, ge=0)
    url: str = ""

def campaign_dict(c):
    ctr = (c.clicks / c.impressions * 100) if c.impressions else 0
    cpc = c.spend / c.clicks if c.clicks else 0
    cpa = c.spend / c.conversions if c.conversions else 0
    roas = c.revenue / c.spend if c.spend else 0
    return {"id": c.id, "name": c.name, "channel": c.channel, "status": c.status, "spend": c.spend, "revenue": c.revenue, "clicks": c.clicks, "impressions": c.impressions, "conversions": c.conversions, "start_date": c.start_date.isoformat() if c.start_date else None, "ctr": round(ctr, 2), "cpc": round(cpc, 2), "cpa": round(cpa, 2), "roas": round(roas, 2)}

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "marketing-intelligence-api"}

@app.get("/api/dashboard")
def dashboard():
    db = SessionLocal()
    try:
        rows = db.query(Campaign).all()
        spend = sum(x.spend or 0 for x in rows)
        revenue = sum(x.revenue or 0 for x in rows)
        clicks = sum(x.clicks or 0 for x in rows)
        impressions = sum(x.impressions or 0 for x in rows)
        conversions = sum(x.conversions or 0 for x in rows)
        return {"campaign_count": len(rows), "total_spend": round(spend, 2), "total_revenue": round(revenue, 2), "total_clicks": clicks, "total_impressions": impressions, "total_conversions": conversions, "average_ctr": round(clicks / impressions * 100, 2) if impressions else 0, "average_roas": round(revenue / spend, 2) if spend else 0, "campaigns": [campaign_dict(x) for x in rows]}
    finally:
        db.close()

@app.get("/api/campaigns")
def list_campaigns():
    db = SessionLocal()
    try:
        return [campaign_dict(x) for x in db.query(Campaign).order_by(Campaign.id.desc()).all()]
    finally:
        db.close()

@app.post("/api/campaigns")
def add_campaign(payload: CampaignIn):
    db = SessionLocal()
    try:
        item = Campaign(**payload.model_dump())
        db.add(item); db.commit(); db.refresh(item)
        return campaign_dict(item)
    finally:
        db.close()

@app.delete("/api/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int):
    db = SessionLocal()
    try:
        item = db.get(Campaign, campaign_id)
        if not item:
            raise HTTPException(status_code=404, detail="Campaign not found")
        db.delete(item); db.commit()
        return {"deleted": True}
    finally:
        db.close()

@app.get("/api/keywords")
def list_keywords():
    db = SessionLocal()
    try:
        return [{"id": x.id, "keyword": x.keyword, "search_volume": x.search_volume, "difficulty": x.difficulty, "position": x.position, "url": x.url} for x in db.query(Keyword).order_by(Keyword.id.desc()).all()]
    finally:
        db.close()

@app.post("/api/keywords")
def add_keyword(payload: KeywordIn):
    db = SessionLocal()
    try:
        item = Keyword(**payload.model_dump())
        db.add(item); db.commit(); db.refresh(item)
        return {"id": item.id, "keyword": item.keyword, "search_volume": item.search_volume, "difficulty": item.difficulty, "position": item.position, "url": item.url}
    finally:
        db.close()

@app.delete("/api/keywords/{keyword_id}")
def delete_keyword(keyword_id: int):
    db = SessionLocal()
    try:
        item = db.get(Keyword, keyword_id)
        if not item:
            raise HTTPException(status_code=404, detail="Keyword not found")
        db.delete(item); db.commit()
        return {"deleted": True}
    finally:
        db.close()
