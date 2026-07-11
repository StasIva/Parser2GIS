from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


@dataclass
class City:
    id: int
    name: str
    source_id: str | None = None
    region: str | None = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> City:
        return cls(
            id=data["id"],
            name=data["name"],
            source_id=data.get("source_id"),
            region=data.get("region"),
            created_at=data.get("created_at", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}


@dataclass
class Rubric:
    id: int
    name: str
    parent_id: int | None = None
    source_id: str | None = None
    sort_order: int = 0
    created_at: str = ""
    children: list[Rubric] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], children: list[Rubric] | None = None) -> Rubric:
        return cls(
            id=data["id"],
            name=data["name"],
            parent_id=data.get("parent_id"),
            source_id=data.get("source_id"),
            sort_order=data.get("sort_order", 0),
            created_at=data.get("created_at", ""),
            children=children,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {f.name: getattr(self, f.name) for f in fields(self)}
        d["children"] = [c.to_dict() for c in (self.children or [])]
        return d


@dataclass
class Task:
    id: int
    name: str
    city_id: int
    rubric_id: int
    status: str = "created"
    progress: int = 0
    orgs_found: int = 0
    orgs_saved: int = 0
    errors_count: int = 0
    checkpoint_data: str | None = None
    created_at: str = ""
    updated_at: str = ""
    completed_at: str | None = None
    city_name: str = ""
    rubric_name: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            city_id=data["city_id"],
            rubric_id=data["rubric_id"],
            status=data.get("status", "created"),
            progress=data.get("progress", 0),
            orgs_found=data.get("orgs_found", 0),
            orgs_saved=data.get("orgs_saved", 0),
            errors_count=data.get("errors_count", 0),
            checkpoint_data=data.get("checkpoint_data"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            completed_at=data.get("completed_at"),
            city_name=data.get("city_name", ""),
            rubric_name=data.get("rubric_name", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}


@dataclass
class Organization:
    id: int
    task_id: int
    name: str
    source_id: str | None = None
    city: str | None = None
    address: str | None = None
    phones: str | None = None
    emails: str | None = None
    website: str | None = None
    social: str | None = None
    rubric_name: str | None = None
    work_hours: str | None = None
    lat: float | None = None
    lon: float | None = None
    raw_json: str | None = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Organization:
        return cls(
            id=data["id"],
            task_id=data["task_id"],
            name=data["name"],
            source_id=data.get("source_id"),
            city=data.get("city"),
            address=data.get("address"),
            phones=data.get("phones"),
            emails=data.get("emails"),
            website=data.get("website"),
            social=data.get("social"),
            rubric_name=data.get("rubric_name"),
            work_hours=data.get("work_hours"),
            lat=data.get("lat"),
            lon=data.get("lon"),
            raw_json=data.get("raw_json"),
            created_at=data.get("created_at", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}


@dataclass
class Contact:
    id: int
    organization_id: int
    type: str
    value: str
    is_primary: bool = False
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Contact:
        return cls(
            id=data["id"],
            organization_id=data["organization_id"],
            type=data["type"],
            value=data["value"],
            is_primary=bool(data.get("is_primary", 0)),
            created_at=data.get("created_at", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}


@dataclass
class ExportRecord:
    id: int
    task_id: int
    format: str
    file_path: str
    record_count: int = 0
    status: str = "running"
    error_message: str | None = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExportRecord:
        return cls(
            id=data["id"],
            task_id=data["task_id"],
            format=data["format"],
            file_path=data["file_path"],
            record_count=data.get("record_count", 0),
            status=data.get("status", "running"),
            error_message=data.get("error_message"),
            created_at=data.get("created_at", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}


@dataclass
class ParseLog:
    id: int
    task_id: int
    level: str
    message: str
    source: str | None = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ParseLog:
        return cls(
            id=data["id"],
            task_id=data["task_id"],
            level=data["level"],
            message=data["message"],
            source=data.get("source"),
            created_at=data.get("created_at", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}
