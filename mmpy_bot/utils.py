import asyncio


def spaces(num: int):
    """Utility function to easily indent strings."""
    return " " * num


def completed_future():
    """Utility function to create a stub Future object that asyncio can wait for."""
    future = asyncio.Future()
    future.set_result(True)
    return future
