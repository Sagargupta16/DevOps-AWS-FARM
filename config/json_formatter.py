import json
import logging
from datetime import datetime, timezone

# Attributes every LogRecord carries; anything else came in through `extra=` and is logged as a field
_STANDARD_ATTRS = set(vars(logging.makeLogRecord({}))) | {
    "message",
    "asctime",
    "taskName",
}


class JsonFormatter(logging.Formatter):
    """One JSON object per line, so CloudWatch Logs Insights can filter on fields directly."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        entry.update(
            {k: v for k, v in vars(record).items() if k not in _STANDARD_ATTRS}
        )
        if record.exc_info:
            entry["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)
