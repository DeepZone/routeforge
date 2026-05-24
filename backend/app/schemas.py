from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.core.normalize import normalize_asn, validate_prefix


class ChangeCaseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


class ChangeCaseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: str | None = None


class ChangeCaseRead(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    created_by_user_id: int | None
    created_at: datetime
    updated_at: datetime
    affected_prefixes: list[str] | None = None
    planned_origin_asns: list[str] | None = None
    risk_summary: str | None = None
    decision: str | None = None
    required_actions: list[str] | None = None
    post_change_status: str | None = None
    last_preflight_at: datetime | None = None
    last_verification_at: datetime | None = None

    class Config:
        from_attributes = True


class AsnCheckRequest(BaseModel):
    change_case_id: int | None = None
    asn: str

    @field_validator("asn")
    @classmethod
    def valid_asn(cls, v: str) -> str:
        normalize_asn(v)
        return v




class AsnRpkiBatchRequest(BaseModel):
    change_case_id: int | None = None
    asn: str
    limit: int = Field(default=25, ge=1, le=100)

    @field_validator("asn")
    @classmethod
    def valid_asn(cls, v: str) -> str:
        normalize_asn(v)
        return v


class PrefixCheckRequest(BaseModel):
    change_case_id: int | None = None
    prefix: str
    origin_as: str | None = None

    @field_validator("prefix")
    @classmethod
    def valid_prefix(cls, v: str) -> str:
        validate_prefix(v)
        return v

    @field_validator("origin_as")
    @classmethod
    def valid_origin(cls, v: str | None) -> str | None:
        if v is not None:
            normalize_asn(v)
        return v



class PreflightCheckRequest(BaseModel):
    change_case_id: int | None = None
    prefix: str
    planned_origin_as: str

    @field_validator("prefix")
    @classmethod
    def valid_prefix(cls, v: str) -> str:
        validate_prefix(v)
        return v

    @field_validator("planned_origin_as")
    @classmethod
    def valid_planned_origin(cls, v: str) -> str:
        normalize_asn(v)
        return v




class RoaPreflightCheckRequest(BaseModel):
    change_case_id: int | None = None
    prefix: str
    origin_as: str
    max_length: int | None = None

    @field_validator("prefix")
    @classmethod
    def valid_prefix(cls, v: str) -> str:
        validate_prefix(v)
        return v

    @field_validator("origin_as")
    @classmethod
    def valid_origin(cls, v: str) -> str:
        normalize_asn(v)
        return v

class BgpVisibilityCheckRequest(BaseModel):
    change_case_id: int | None = None
    prefix: str
    expected_origin_as: str | None = None

    @field_validator("prefix")
    @classmethod
    def valid_prefix(cls, v: str) -> str:
        validate_prefix(v)
        return v

    @field_validator("expected_origin_as")
    @classmethod
    def valid_expected_origin(cls, v: str | None) -> str | None:
        if v is not None:
            normalize_asn(v)
        return v


class CheckResponse(BaseModel):
    report_id: int
    status: str
    summary: str
    explanation: str | None = None
    risk: str | None = None
    recommendations: list[str]
    input: dict[str, Any] | None = None
    checks: dict[str, Any] | None = None
    details: dict[str, Any]
    markdown: str
    html: str


class ReportRead(BaseModel):
    id: int
    check_id: int
    json_data: dict[str, Any]
    markdown: str
    html: str
    created_at: datetime

    class Config:
        from_attributes = True


class WatchTargetCreate(BaseModel):
    name: str
    watch_type: str
    prefix: str | None = None
    asn: str | None = None
    origin_as: str | None = None
    expected_origin_as: str | None = None
    max_length: int | None = None
    interval_minutes: int = Field(default=60, ge=1)
    is_active: bool = True
    change_case_id: int | None = None

class WatchTargetUpdate(BaseModel):
    name: str | None = None
    prefix: str | None = None
    asn: str | None = None
    origin_as: str | None = None
    expected_origin_as: str | None = None
    max_length: int | None = None
    interval_minutes: int | None = Field(default=None, ge=1)
    is_active: bool | None = None
    change_case_id: int | None = None

class WatchTargetRead(BaseModel):
    id: int
    name: str
    watch_type: str
    prefix: str | None
    asn: str | None
    origin_as: str | None
    expected_origin_as: str | None
    max_length: int | None
    interval_minutes: int
    is_active: bool
    change_case_id: int | None
    created_by_user_id: int | None
    last_run_at: datetime | None
    next_run_at: datetime | None
    last_status: str | None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class WatchRunRead(BaseModel):
    id: int
    watch_target_id: int
    report_id: int | None
    previous_status: str | None
    status: str
    changed: bool
    summary: str
    alert_delivery_status: str | None = None
    alert_delivered_at: datetime | None = None
    alert_error_message: str | None = None
    created_at: datetime
    class Config:
        from_attributes = True
