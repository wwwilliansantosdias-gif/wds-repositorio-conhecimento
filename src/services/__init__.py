"""Infraestrutura compartilhada pela camada de serviços."""

from services.base import BaseService
from services.types import DomainModel

__all__ = ["BaseService", "DomainModel"]
