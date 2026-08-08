"""Private PostgreSQL adapter composition seam."""

from .uow import TaskManagementPostgresUnitOfWorkFactory

__all__ = [
    "TaskManagementPostgresUnitOfWorkFactory",
]
