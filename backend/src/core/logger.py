import structlog
import logging
import sys
from src.core.config import settings


shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.CallSiteParameterAdder(
        [structlog.processors.CallSiteParameter.FILENAME, 
         structlog.processors.CallSiteParameter.LINENO]
    ),
]


if settings.APP_ENV in ["production", "pre-production"]:
    processors = shared_processors + [
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ]
else:
    processors = shared_processors + [
        structlog.dev.ConsoleRenderer(),
    ]


structlog.configure(
    processors=processors,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(structlog.stdlib.ProcessorFormatter(
    processor=structlog.processors.JSONRenderer() if settings.APP_ENV in ["production", "pre-production"] else structlog.dev.ConsoleRenderer(),
))


root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)


logger = structlog.get_logger()
