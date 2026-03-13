"""
contracts.py - Core data types, interfaces, and abstract contracts.
Domain-agnostic. No business logic here.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from abc import ABC, abstractmethod


# 
#  Data Packets
# 

@dataclass
class RawPacket:
    """A single row ingested from the CSV, schema-mapped and type-cast."""
    serial: int                      
    entity_name: str                  
    time_period: int                  
    metric_value: float               
    security_hash: str                
    extra_fields: dict = field(default_factory=dict)  


@dataclass
class ProcessedPacket:
    """Output of a Core worker after verification + optional enrichment."""
    serial: int
    entity_name: str
    time_period: int
    metric_value: float
    verified: bool
    computed_metric: Optional[float] = None   


# 
#  Abstract Interfaces (DIP contracts)
#

class IInputModule(ABC):
    @abstractmethod
    def run(self, raw_queue, stop_event) -> None:
        """Read data and push RawPackets into raw_queue."""
        ...


class ICoreWorker(ABC):
    @abstractmethod
    def run(self, raw_queue, processed_queue, stop_event) -> None:
        """Pull RawPackets, process, push ProcessedPackets."""
        ...


class IOutputModule(ABC):
    @abstractmethod
    def run(self, processed_queue, telemetry, stop_event) -> None:
        """Consume ProcessedPackets and render the dashboard."""
        ...


class ITelemetryObserver(ABC):
    @abstractmethod
    def on_telemetry_update(self, snapshot: dict) -> None:
        """Called when telemetry subject emits a new snapshot."""
        ...