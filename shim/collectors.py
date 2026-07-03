"""Collect system state and shape it into the Snapshot contract.

Every collector is defensive: hardware or services that aren't present on a given
machine yield None rather than raising, so the same shim binary runs unmodified on
rivendell (Linux + NVIDIA), the Mac Mini (no GPU), and the Windows dev box.
"""

from __future__ import annotations

import socket
import time
from datetime import datetime, timezone

import httpx
import psutil

from .schema import (
    Cpu,
    Disk,
    Gpu,
    Memory,
    Network,
    Model,
    LlamaCppService,
    Services,
    Snapshot,
)

JSON = dict[str, int | float | str | "JSON"] | list[int | float | str | "JSON"]


MB = 1024**2
GB = 1024**3
LLAMA_URL = "http://127.0.0.1:11434"

# Filesystem types that are virtual, in-memory, or otherwise not real storage we
# want to monitor. Reporting these pollutes the snapshot and, worse, lets a junk
# mount land at disk[0] and false-fire the disk-usage alert rule.
_PSEUDO_FSTYPES = {
    "squashfs",
    "overlay",
    "tmpfs",
    "devtmpfs",
    "ramfs",
    "proc",
    "sysfs",
    "cgroup",
    "cgroup2",
    "fuse.snapfuse",
    "9p",  # WSL host-mount transport
}

# Mount-point prefixes to skip outright (WSL/Docker plumbing, snap loop mounts).
_PSEUDO_MOUNT_PREFIXES = (
    "/mnt/wsl",
    "/snap",
    "/var/lib/docker",
)


def _is_real_disk(mountpoint: str, fstype: str) -> bool:
    if fstype.lower() in _PSEUDO_FSTYPES:
        return False

    if mountpoint.startswith(_PSEUDO_MOUNT_PREFIXES):
        return False

    return True


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def collect_cpu() -> Cpu:
    # interval=None returns the load since the previous call; the daemon polls on a
    # schedule so successive samples are meaningful without blocking here.
    percent = psutil.cpu_percent(interval=None)

    try:
        load_avg_1m = psutil.getloadavg()[0]

    except (AttributeError, OSError):
        load_avg_1m = None  # not available on stock Windows

    return Cpu(
        percent = round(percent, 1),
        core_count = psutil.cpu_count(logical=True) or 0,
        load_avg_1m = round(load_avg_1m, 2) if load_avg_1m is not None else None,
    )


def collect_memory() -> Memory:
    vm = psutil.virtual_memory()

    return Memory(
        total_gb = round(vm.total / GB, 1),
        used_gb = round(vm.used / GB, 1),
        percent = round(vm.percent, 1),
    )


def collect_disk() -> list[Disk]:
    disks: list[Disk] = []
    seen_devices: set[str] = set()

    for part in psutil.disk_partitions(all=False):
        if not _is_real_disk(part.mountpoint, part.fstype): continue

        if part.device in seen_devices: continue # Collapse multiple mounts backed by the same device down to one entry.

        seen_devices.add(part.device)

        try:
            usage = psutil.disk_usage(part.mountpoint)

        except (PermissionError, OSError): continue  # e.g. an unreadable or disconnected mount

        disks.append(
            Disk(
                mount = part.mountpoint,
                total_gb = round(usage.total / GB, 1),
                used_gb = round(usage.used / GB, 1),
                percent = round(usage.percent, 1),
            )
        )

    return disks


def collect_gpu() -> Gpu | None:
    """NVIDIA GPU via NVML. Returns None when no NVIDIA GPU or driver is present."""
    try:
        import pynvml
    except ImportError:
        return None

    try:
        pynvml.nvmlInit()
    except Exception:
        return None

    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        name = pynvml.nvmlDeviceGetName(handle)

        if isinstance(name, bytes):
            name = name.decode()

        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)

        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
        except Exception:
            util = None

        try:
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        except Exception:
            temp = None

        return Gpu(
            name = name,
            memory_total_mb = mem.total // MB,
            memory_used_mb = mem.used // MB,
            utilization_percent = util,
            temperature_c = temp,
        )

    except Exception:
        return None

    finally:
        try:
            pynvml.nvmlShutdown()
        except Exception:
            pass


def collect_network() -> Network:
    interfaces = [name for name in psutil.net_if_stats() if name != "lo"]

    return Network(
        interfaces = interfaces,
        reachable = True
    )


def collect_llama_cpp() -> LlamaCppService | None:
    """
    Query the local llama.cpp API for running status and models.

    `/v1/models` is the liveness signal: it lists every linked model and whether it is loaded

    Returns None on machines that don't run llama.cpp (Mac Mini, Windows box) so the
    field reads as "not applicable" rather than "down".
    """
    try:
        '''
        localhost:port/v1/models Format
        {
        "data": [
            {
                "id": "ggml-org/gemma-3-4b-it-GGUF:Q4_K_M",
                "path": "~/llama/models/Qwen3.5-0.8B-MTP-Q8_0.gguf",
                "status": {
                    "value": "loaded",
                    "args": ["llama-server", "-ctx", "4096"]
                },
                "architecture": {
                    "input_modalities": [
                        "text",
                        "image"
                    ],
                    "output_modalities": [
                        "text"
                    ]
                }
            },
            ...
        ]
        }
        '''
        tags_resp = httpx.get(f"{LLAMA_URL}/v1/models", timeout=2.0)
        tags_resp.raise_for_status()
    except httpx.HTTPError:
        return None  # llama.cpp not running or not installed on this machine

    data: list[dict[str, str | dict[str, str | list[str]]]] = tags_resp.json().get("data", [])

    models = [
        Model(
            name = model.get("id", ""),                                                        # type: ignore
            status = model.get("status", {}).get("value", ""),                                 # type: ignore
            has_vision = "image" in model.get("architecture", {}).get("input_modalities", []), # type: ignore
        )
        for model in data
    ]

    return LlamaCppService(
        running = True,
        models = models
    )



def collect_snapshot() -> Snapshot:
    llama_cpp = collect_llama_cpp()

    return Snapshot(
        hostname = socket.gethostname(),
        timestamp = utc_now(),
        cpu = collect_cpu(),
        memory = collect_memory(),
        disk = collect_disk(),
        gpu = collect_gpu(),
        network = collect_network(),
        services = Services(llama_cpp=llama_cpp),
        uptime_hours = round((time.time() - psutil.boot_time()) / 3600, 1),
    )
