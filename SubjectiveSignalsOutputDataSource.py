import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from subjective_abstract_data_source_package import SubjectiveDataSource

from trading_contracts.plugin_support import as_bool, icon_for


class SubjectiveSignalsOutputDataSource(SubjectiveDataSource):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.persist = as_bool(self._connection.get("persist", False))
        default_path = Path(__file__).resolve().parents[2] / "storage" / "signals.jsonl"
        self.path = Path(self._connection.get("path") or default_path)

    @classmethod
    def connection_schema(cls):
        return {"persist": {"type": "bool", "label": "Persist JSONL", "default": False}, "path": {"type": "file_path", "label": "JSONL Path"}}

    @classmethod
    def request_schema(cls):
        return {"signal": {"type": "object", "label": "Signal"}, "signals": {"type": "array", "label": "Signals"}}

    @classmethod
    def output_schema(cls):
        return {"signals": {"type": "array", "label": "Signals"}, "count": {"type": "int", "label": "Count"}, "path": {"type": "text", "label": "Path"}, "error": {"type": "text", "label": "Error"}}

    @classmethod
    def icon(cls):
        return icon_for(__file__)

    def run(self, request):
        request = request or {}
        signals = request.get("signals")
        if signals is None and request.get("signal") is not None:
            signals = [request["signal"]]
        signals = list(signals or [])
        try:
            if self.persist and signals:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with self.path.open("a", encoding="utf-8") as handle:
                    for signal in signals:
                        handle.write(json.dumps(signal, separators=(",", ":")) + "\n")
            return {"signals": signals, "count": len(signals), "path": str(self.path) if self.persist else "", "error": ""}
        except Exception as exc:
            return {"signals": signals, "count": len(signals), "path": str(self.path), "error": str(exc)}
