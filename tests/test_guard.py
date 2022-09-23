import asyncio

from asyncio_guard import Guard


async def test_set() -> None:
    guard = Guard(obj=1)

    async with guard as obj:
        assert obj == 1

    await guard.set(2)
    async with guard as obj:
        assert obj == 2


async def test_update() -> None:
    values_iter = iter(range(1, 3))

    async def update_func() -> int:
        return (next(values_iter))

    guard = Guard(update_func=update_func)

    async with guard as obj:
        assert obj == 1

    await guard.update()
    async with guard as obj:
        assert obj == 2


async def test_exclusivity() -> None:
    # If guard doesn't provide exclusive access
    # then there will be deadlock
    mutex1, mutex2 = asyncio.Lock(), asyncio.Lock()

    guard = Guard(obj=1)

    async def first_worker() -> None:
        async with guard as obj:
            async with mutex1:
                await asyncio.sleep(1)
                async with mutex2:
                    assert obj == 1

    async def second_worker() -> None:
        async with guard as obj:
            async with mutex2:
                await asyncio.sleep(1)
                async with mutex1:
                    assert obj == 1

    await asyncio.gather(first_worker(), second_worker())
