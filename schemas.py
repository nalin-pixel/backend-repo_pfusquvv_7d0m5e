"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# Core domain schemas for Government Hospital Information app

class Hospital(BaseModel):
    """
    Hospitals collection schema
    Collection name: "hospital"
    """
    name: str = Field(..., description="Hospital name")
    level: Optional[str] = Field(None, description="Ownership level: district/state/central")
    state: Optional[str] = Field(None, description="State/UT")
    district: Optional[str] = Field(None, description="District")
    address: Optional[str] = Field(None, description="Full address")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    phone: Optional[str] = Field(None, description="Primary contact number")
    email: Optional[str] = Field(None, description="Official email")
    emergency_contact: Optional[str] = Field(None, description="Emergency helpline/ambulance number")
    facilities: Optional[List[str]] = Field(default_factory=list, description="Facility tags e.g. ICU, MRI, 24x7")
    departments: Optional[List[str]] = Field(default_factory=list, description="Available departments")

class Department(BaseModel):
    """
    Departments collection schema
    Collection name: "department"
    """
    name: str = Field(..., description="Department name e.g., Cardiology")
    description: Optional[str] = Field(None, description="Short description")
    hospital_id: Optional[str] = Field(None, description="Reference to hospital _id as string")

class Doctor(BaseModel):
    """
    Doctors collection schema
    Collection name: "doctor"
    """
    name: str = Field(..., description="Doctor's full name")
    specialization: Optional[str] = Field(None, description="Specialization")
    qualifications: Optional[List[str]] = Field(default_factory=list)
    opd_days: Optional[List[str]] = Field(default_factory=list, description="OPD days e.g., Mon, Wed, Fri")
    opd_timings: Optional[str] = Field(None, description="OPD timing window e.g., 10:00-13:00")
    photo_url: Optional[str] = Field(None)
    hospital_id: Optional[str] = Field(None, description="Reference to hospital _id as string")
    department: Optional[str] = Field(None, description="Department name")

class Procedure(BaseModel):
    """
    Medical procedures collection schema
    Collection name: "procedure"
    """
    code: Optional[str] = Field(None, description="Procedure code if available")
    name: str = Field(..., description="Procedure name")
    slug: Optional[str] = Field(None, description="URL-friendly identifier")
    steps: Optional[List[str]] = Field(default_factory=list, description="High-level steps")
    pre_op_instructions: Optional[List[str]] = Field(default_factory=list)
    recovery_tips: Optional[List[str]] = Field(default_factory=list)
    estimated_cost_min: Optional[float] = Field(None, ge=0)
    estimated_cost_max: Optional[float] = Field(None, ge=0)

class DocumentRequirement(BaseModel):
    """
    Documents required for procedures/admission
    Collection name: "documentrequirement"
    """
    procedure_slug: Optional[str] = Field(None, description="Related procedure slug")
    title: str = Field(..., description="Document title e.g., Government ID")
    description: Optional[str] = Field(None)
    mandatory: bool = Field(True)

class Fee(BaseModel):
    """
    Official fee structure records
    Collection name: "fee"
    """
    hospital_id: Optional[str] = Field(None, description="Hospital reference as string")
    department: Optional[str] = Field(None)
    service_name: str = Field(..., description="Service or consultation name")
    amount: float = Field(..., ge=0)
    currency: str = Field("INR")
    effective_from: Optional[date] = Field(None)

# Example generic schemas kept for reference (not used by app directly)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
