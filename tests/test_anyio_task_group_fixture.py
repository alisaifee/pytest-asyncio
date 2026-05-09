from __future__ import annotations

from textwrap import dedent

from pytest import Pytester


def test_async_context_manager_mixin_with_task_group(pytester: Pytester):
    pytester.makeini("[pytest]\nasyncio_default_fixture_loop_scope = function")
    pytester.makepyfile(
        dedent("""\
        from __future__ import annotations

        from collections.abc import AsyncGenerator
        from contextlib import asynccontextmanager
        from typing import Self

        import pytest
        import pytest_asyncio
        from anyio import AsyncContextManagerMixin, create_task_group


        class TaskGroupOwner(AsyncContextManagerMixin):
            @asynccontextmanager
            async def __asynccontextmanager__(self) -> AsyncGenerator[Self]:
                async with create_task_group():
                    yield self


        @pytest_asyncio.fixture
        async def owner():
            async with TaskGroupOwner() as owner:
                yield owner


        @pytest.mark.asyncio
        async def test_use_task_group(owner):
            assert owner is not None
        """)
    )
    result = pytester.runpytest("--asyncio-mode=strict")
    result.assert_outcomes(passed=1)
