"""Tipos compartilhados entre a camada de serviços e o domínio."""

from __future__ import annotations

from typing import TypeAlias

from models import Objeto, Relacao, Tag


DomainModel: TypeAlias = Objeto | Tag | Relacao
