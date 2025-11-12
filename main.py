import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents

app = FastAPI(title="Gov Hospital Info & Patient Records API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateHospital(BaseModel):
    name: str
    level: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    emergency_contact: Optional[str] = None
    facilities: Optional[List[str]] = []
    departments: Optional[List[str]] = []

class CreateDoctor(BaseModel):
    name: str
    specialization: Optional[str] = None
    qualifications: Optional[List[str]] = []
    opd_days: Optional[List[str]] = []
    opd_timings: Optional[str] = None
    photo_url: Optional[str] = None
    hospital_id: Optional[str] = None
    department: Optional[str] = None

class CreateProcedure(BaseModel):
    code: Optional[str] = None
    name: str
    slug: Optional[str] = None
    steps: Optional[List[str]] = []
    pre_op_instructions: Optional[List[str]] = []
    recovery_tips: Optional[List[str]] = []
    estimated_cost_min: Optional[float] = None
    estimated_cost_max: Optional[float] = None

class CreateDocumentRequirement(BaseModel):
    procedure_slug: Optional[str] = None
    title: str
    description: Optional[str] = None
    mandatory: bool = True

@app.get("/")
def read_root():
    return {"message": "Gov Hospital API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

@app.get("/api/hospitals")
async def list_hospitals(state: Optional[str] = None, district: Optional[str] = None):
    filter_dict = {}
    if state:
        filter_dict["state"] = state
    if district:
        filter_dict["district"] = district
    try:
        docs = get_documents("hospital", filter_dict)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/hospitals")
async def create_hospital(payload: CreateHospital):
    try:
        new_id = create_document("hospital", payload.model_dump())
        return {"_id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/doctors")
async def list_doctors(hospital_id: Optional[str] = None, department: Optional[str] = None):
    filter_dict = {}
    if hospital_id:
        filter_dict["hospital_id"] = hospital_id
    if department:
        filter_dict["department"] = department
    try:
        docs = get_documents("doctor", filter_dict)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/doctors")
async def create_doctor(payload: CreateDoctor):
    try:
        new_id = create_document("doctor", payload.model_dump())
        return {"_id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/procedures")
async def list_procedures(q: Optional[str] = None):
    filter_dict = {}
    if q:
        # naive text search across name and slug using regex
        filter_dict = {"$or": [
            {"name": {"$regex": q, "$options": "i"}},
            {"slug": {"$regex": q, "$options": "i"}}
        ]}
    try:
        docs = get_documents("procedure", filter_dict)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/procedures")
async def create_procedure(payload: CreateProcedure):
    try:
        new_id = create_document("procedure", payload.model_dump())
        return {"_id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/procedures/{slug}/documents")
async def list_procedure_documents(slug: str):
    try:
        docs = get_documents("documentrequirement", {"procedure_slug": slug})
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CreateDocumentReq(BaseModel):
    procedure_slug: Optional[str] = None
    title: str
    description: Optional[str] = None
    mandatory: bool = True

@app.post("/api/procedures/{slug}/documents")
async def create_procedure_document(slug: str, payload: CreateDocumentReq):
    try:
        data = payload.model_dump()
        data["procedure_slug"] = slug
        new_id = create_document("documentrequirement", data)
        return {"_id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
