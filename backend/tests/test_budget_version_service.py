from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from app.modules.planning.exceptions import (
    BudgetVersionLockedError,
    BudgetVersionNotFoundError,
)
from app.modules.planning.models import BudgetVersion
from app.modules.planning.repositories import BudgetVersionRepository
from app.modules.planning.services import BudgetVersionService


def build_service() -> tuple[BudgetVersionService, AsyncMock]:
    repository = AsyncMock(spec=BudgetVersionRepository)
    service = BudgetVersionService(repository)

    return service, repository


@pytest.mark.asyncio
async def test_create_returns_created_version() -> None:
    service, repository = build_service()

    version = Mock(spec=BudgetVersion)
    repository.add.return_value = version

    returned = await service.create(version)

    assert returned is version
    repository.add.assert_awaited_once_with(version)


@pytest.mark.asyncio
async def test_get_returns_budget_version() -> None:
    service, repository = build_service()

    version = Mock(spec=BudgetVersion)
    repository.get_by_id.return_value = version

    returned = await service.get(
        uuid4(),
        uuid4(),
    )

    assert returned is version


@pytest.mark.asyncio
async def test_get_raises_when_not_found() -> None:
    service, repository = build_service()

    repository.get_by_id.return_value = None

    with pytest.raises(BudgetVersionNotFoundError):
        await service.get(
            uuid4(),
            uuid4(),
        )


@pytest.mark.asyncio
async def test_lock_marks_version_locked() -> None:
    service, repository = build_service()

    version = Mock(spec=BudgetVersion)
    version.is_locked = False

    repository.get_by_id.return_value = version
    repository.save.return_value = version

    returned = await service.lock(
        uuid4(),
        uuid4(),
    )

    assert returned is version
    assert version.is_locked is True

    repository.save.assert_awaited_once_with(version)


@pytest.mark.asyncio
async def test_activate_deactivates_previous_version() -> None:
    service, repository = build_service()

    active = Mock(spec=BudgetVersion)
    active.is_active = True

    new_version = Mock(spec=BudgetVersion)
    new_version.is_active = False

    repository.get_active_for_scenario.return_value = active
    repository.get_by_id.return_value = new_version

    repository.save.side_effect = [
        active,
        new_version,
    ]

    returned = await service.activate(
        uuid4(),
        uuid4(),
    )

    assert returned is new_version

    assert active.is_active is False
    assert new_version.is_active is True

    assert repository.save.await_count == 2


@pytest.mark.asyncio
async def test_activate_when_no_active_version_exists() -> None:
    service, repository = build_service()

    version = Mock(spec=BudgetVersion)
    version.is_active = False

    repository.get_active_for_scenario.return_value = None
    repository.get_by_id.return_value = version
    repository.save.return_value = version

    returned = await service.activate(
        uuid4(),
        uuid4(),
    )

    assert returned is version
    assert version.is_active is True

    repository.save.assert_awaited_once_with(version)


def test_validate_editable_accepts_unlocked_version() -> None:
    version = Mock(spec=BudgetVersion)
    version.is_locked = False

    BudgetVersionService.validate_editable(version)


def test_validate_editable_raises_for_locked_version() -> None:
    version = Mock(spec=BudgetVersion)
    version.id = uuid4()
    version.is_locked = True

    with pytest.raises(BudgetVersionLockedError):
        BudgetVersionService.validate_editable(version)
