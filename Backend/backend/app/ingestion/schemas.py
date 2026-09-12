from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class ProvenanceMixin(BaseModel):
    """
    Base provenance requirements for all canonical records.
    Strictly enforced as per TraceX rules.
    """
    Synthetic_Flag: bool = Field(..., description="Must be true for synthetic MVP data.")
    Source_Dataset: Optional[str] = Field(None, description="Dataset name.")
    source_record_reference: Optional[str] = Field(None, description="External source system reference.")
    Generation_Batch_ID: Optional[str] = Field(None, description="Mapped from scenario_id.")
    Audit_Reference: str = Field(..., description="Deterministic unique provenance reference.")
    Provenance_Mode: str = Field(..., description="e.g. direct, validated-join, synthetic-design")


class CanonicalNode(ProvenanceMixin):
    """Base model for all nodes."""
    canonical_label: str


class Person(CanonicalNode):
    canonical_label: Literal["Person"] = "Person"
    person_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    organization_id: Optional[str] = None


class Phone(CanonicalNode):
    canonical_label: Literal["Phone"] = "Phone"
    phone_id: str
    phone_number: Optional[str] = None


class Account(CanonicalNode):
    canonical_label: Literal["Account"] = "Account"
    account_id: str
    account_number: Optional[str] = None
    bank_name: Optional[str] = None


class Location(CanonicalNode):
    canonical_label: Literal["Location"] = "Location"
    location_id: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Organisation(CanonicalNode):
    canonical_label: Literal["Organisation"] = "Organisation"
    organization_id: str
    name: Optional[str] = None


class Vehicle(CanonicalNode):
    canonical_label: Literal["Vehicle"] = "Vehicle"
    vehicle_id: str
    license_plate: Optional[str] = None


class Device(CanonicalNode):
    canonical_label: Literal["Device"] = "Device"
    device_id: str
    mac_address: Optional[str] = None


class Document(CanonicalNode):
    canonical_label: Literal["Document"] = "Document"
    document_id: str
    title: Optional[str] = None
    content: Optional[str] = None


class Case(CanonicalNode):
    canonical_label: Literal["Case"] = "Case"
    case_id: str
    description: Optional[str] = None


class Event(CanonicalNode):
    canonical_label: Literal["Event"] = "Event"
    event_type: str
    timestamp: Optional[datetime] = None


class Transaction(Event):
    event_type: Literal["Transaction"] = "Transaction"
    transaction_id: str
    amount: Optional[float] = None
    sender_account_id: Optional[str] = None
    receiver_account_id: Optional[str] = None
    person_id: Optional[str] = None


class CommunicationEvent(Event):
    event_type: Literal["CommunicationEvent"] = "CommunicationEvent"
    communication_id: str
    # Nullable communication fields as per constraints
    source_phone_id: Optional[str] = None
    target_phone_id: Optional[str] = None
    person_id: Optional[str] = None


class NetworkEvent(Event):
    event_type: Literal["NetworkEvent"] = "NetworkEvent"
    network_event_id: str
    person_id: Optional[str] = None


class PhysicalAccessEvent(Event):
    event_type: Literal["PhysicalAccessEvent"] = "PhysicalAccessEvent"
    physical_event_id: str
    person_id: Optional[str] = None
    location_id: Optional[str] = None


class Incident(Event):
    event_type: Literal["Incident"] = "Incident"
    incident_id: str
    person_id: Optional[str] = None
    location_id: Optional[str] = None


class CrimeStatistic(CanonicalNode):
    canonical_label: Literal["CrimeStatistic"] = "CrimeStatistic"
    context_id: str
    year: Optional[int] = None
    state_ut: Optional[str] = None
    city: Optional[str] = None
    crime_category: Optional[str] = None
    crime_count: Optional[int] = None
    measure_type: Optional[str] = None
    data_origin: Optional[str] = None
    source_dataset: Optional[str] = None
    Confidence_Level: Optional[str] = None


class CanonicalRelationship(ProvenanceMixin):
    relationship_type: str
    source_id: str
    target_id: str
    # Nullable timestamps for static relationships
    timestamp: Optional[datetime] = None
