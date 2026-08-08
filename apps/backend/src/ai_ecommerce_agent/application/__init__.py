"""Framework-neutral application ports.

The application layer owns the capabilities a use case needs.  Concrete
database/session objects stay in platform adapters and are injected by the
composition root.
"""

from .errors import (
    UnitOfWorkError,
    UnitOfWorkStateError,
)
from .ports import (
    UnitOfWork,
    UnitOfWorkFactory,
    UnitOfWorkState,
)

__all__ = [
    "UnitOfWork",
    "UnitOfWorkError",
    "UnitOfWorkFactory",
    "UnitOfWorkState",
    "UnitOfWorkStateError",
]
