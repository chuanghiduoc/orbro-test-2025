"""Parser - Handles parsing of Tag data from raw messages."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TagData:
    tag_id: str
    cnt: int
    timestamp: datetime
    raw: str


class TagParser:
    """Parses TAG messages in format: TAG,<tag_id>,<cnt>,<timestamp>"""

    @staticmethod
    def parse(raw_data: str) -> Optional[TagData]:
        try:
            parts = raw_data.strip().split(",")
            if len(parts) != 4 or parts[0] != "TAG":
                return None

            tag_id = parts[1]
            cnt = int(parts[2])
            timestamp_str = parts[3]

            timestamp = TagParser._parse_timestamp(timestamp_str)

            return TagData(
                tag_id=tag_id,
                cnt=cnt,
                timestamp=timestamp,
                raw=raw_data.strip()
            )
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _parse_timestamp(ts: str) -> datetime:
        if "." in ts:
            main_part, ms_part = ts.split(".")
            dt = datetime.strptime(main_part, "%Y%m%d%H%M%S")
            return dt.replace(microsecond=int(ms_part) * 1000)
        return datetime.strptime(ts, "%Y%m%d%H%M%S")
