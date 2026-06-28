"""Structured data contract for shim payloads.

Every machine returns the same top-level structure. Fields that don't apply to a
machine (e.g. `gpu` on the Mac Mini) are returned as None, never omitted, so the
schema stays consistent across the fleet. See project-homelab-assistant.md.
"""

from __future__ import annotations

from pydantic import BaseModel


class Cpu(BaseModel):
    percent: float
    core_count: int
    load_avg_1m: float | None  # None on platforms without load average (Windows)


class Memory(BaseModel):
    total_gb: float
    used_gb: float
    percent: float


class Disk(BaseModel):
    mount: str
    total_gb: float
    used_gb: float
    percent: float


class Gpu(BaseModel):
    name: str
    memory_total_mb: int
    memory_used_mb: int
    utilization_percent: int | None
    temperature_c: int | None


class Network(BaseModel):
    interfaces: list[str]
    reachable: bool


class OllamaService(BaseModel):
    running: bool
    models_available: list[str]  # installed on disk (Ollama /api/tags)
    models_loaded: list[str]  # currently resident in memory (Ollama /api/ps)


class Services(BaseModel):
    ollama: OllamaService | None = None


class Snapshot(BaseModel):
    hostname: str
    timestamp: str  # ISO 8601, UTC, e.g. 2025-07-15T14:32:00Z
    cpu: Cpu
    memory: Memory
    disk: list[Disk]
    gpu: Gpu | None
    network: Network
    services: Services
    uptime_hours: float
