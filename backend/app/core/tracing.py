import uuid
import time
from dataclasses import dataclass, field


@dataclass
class RequestTrace:
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    start_time: float = field(default_factory=time.perf_counter)
    spans: list = field(default_factory=list)

    def add_span(self, name: str, duration_ms: float):
        self.spans.append({"name": name, "duration_ms": round(duration_ms, 2)})

    @property
    def elapsed_ms(self) -> float:
        return round((time.perf_counter() - self.start_time) * 1000, 2)


def new_trace() -> RequestTrace:
    return RequestTrace()
