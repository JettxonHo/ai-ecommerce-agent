"""Source and Evidence application-owned ports.

The concrete persistence adapter is composed later.  Keeping these contracts
in the application layer lets the module own its transaction-facing boundary
without exposing repository or infrastructure details through ``public``.
"""

from .ports import (
    SourceEvidenceUnitOfWork,
    SourceEvidenceUnitOfWorkFactory,
    SourceVersionProcessingRepositoryPort,
    SourceVersionRepositoryPort,
    TaskSourceAssociationRepositoryPort,
)

__all__ = [
    "SourceEvidenceUnitOfWork",
    "SourceEvidenceUnitOfWorkFactory",
    "SourceVersionProcessingRepositoryPort",
    "SourceVersionRepositoryPort",
    "TaskSourceAssociationRepositoryPort",
]
