from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class ActionState(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    ACCEPTED = "ACCEPTED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"


class ActionRecord(BaseModel):
    action_id: str = Field(..., description="Unique UUID for this corrective action")
    domain: str = Field(..., description="e.g., CMC, MANUFACTURING, CLINICAL, REGULATORY")
    state: ActionState = Field(default=ActionState.PROPOSED)
    title: str
    description: str
    assigned_human_owner: str = Field(..., description="Accountable human owner ID/email")
    executing_partner_id: str = Field(..., description="Entity executing the task")
    evidence_hashes: List[str] = Field(default_factory=list, description="SHA-256 cryptographic proof hashes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    verification_deadline: Optional[datetime] = None


class ProductionPlatform(str, Enum):
    MRNA = "MRNA"
    VIRAL_VECTOR = "VIRAL_VECTOR"
    RECOMBINANT_PROTEIN = "RECOMBINANT_PROTEIN"
    MONOCLONAL_ANTIBODY = "MONOCLONAL_ANTIBODY"
    SMALL_MOLECULE = "SMALL_MOLECULE"


class CandidateIntervention(BaseModel):
    candidate_id: str
    threat_pathogen_family: str
    platform: ProductionPlatform
    target_dose_count: int
    bioreactor_volume_liters_required: float
    storage_temp_celsius: float
    regulatory_target_regions: List[str]
    timestamp_emitted: datetime = Field(default_factory=datetime.utcnow)


class SlotStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    MAINTENANCE = "MAINTENANCE"
    CONFLICT_FLAGGED = "CONFLICT_FLAGGED"
    EXPIRED = "EXPIRED"


class ManufacturingCapacitySlot(BaseModel):
    slot_id: str
    facility_id: str
    facility_country: str
    supported_platforms: List[ProductionPlatform]
    bioreactor_capacity_liters: float
    window_start: datetime
    window_end: datetime
    status: SlotStatus = SlotStatus.AVAILABLE
    evidence_hash: str = Field(..., description="Cryptographic SHA-256 hash of partner-signed slot reservation")
    evidence_expires_at: datetime
    allocated_candidate_id: Optional[str] = None


class AgentTrigger(str, Enum):
    ON_UPSTREAM_EVENT = "ON_UPSTREAM_EVENT"
    ON_DOCUMENT_UPDATE = "ON_DOCUMENT_UPDATE"
    CRON_SCHEDULED = "CRON_SCHEDULED"
    MANUAL_INVOCATION = "MANUAL_INVOCATION"


class AgentRuntimeManifest(BaseModel):
    agent_id: str
    functional_group: str
    accountable_human_owner: str
    permitted_sources: List[str]
    allowed_tools: List[str]
    trigger: AgentTrigger
    execution_timeout_ms: int = 30000
    model_temperature: float = 0.0
    output_schema_name: str
