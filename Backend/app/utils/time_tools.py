from datetime import datetime, timedelta, UTC

def now_utc_ts() -> float:
    return datetime.now(UTC).timestamp()