import logging
import sys

from backend.app.core.config import settings
from backend.app.core.context import get_request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True


def configure_logging():
    level = logging.DEBUG if settings.debug else logging.INFO

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | [%(request_id)s] | %(name)s | %(message)s")
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    logging.basicConfig(
        level=level,
        handlers=[handler],
        force=True,
    )