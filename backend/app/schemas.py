from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.core.normalize import normalize_asn, validate_prefix


class AsnCheckRequest(BaseModel):
    asn: str

    @field_validator("asn")
    @classmethod
    def valid_asn(cls, v: str) -> str:
        normalize_asn(v)
        return v




class AsnRpkiBatchRequest(BaseModel):
    asn: str
    limit: int = Field(default=25, ge=1, le=100)

    @field_validator("asn")
    @classmethod
    def valid_asn(cls, v: str) -> str:
        normalize_asn(v)
        return v


class PrefixCheckRequest(BaseModel):
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
