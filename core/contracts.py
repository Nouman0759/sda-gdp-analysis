from typing import Protocol, List, Dict, Any, runtime_checkable


@runtime_checkable
class DataSink(Protocol):
    """
    Outbound Abstraction:
    Core sends processed results to this.
    """

    def write(self, records: List[Dict]) -> None:
        ...


class PipelineService(Protocol):
    """
    Inbound Abstraction:
    Input plugins send raw data to this.
    """

    def execute(self, raw_data: List[Any]) -> None:
        ...