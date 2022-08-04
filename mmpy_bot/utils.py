import asyncio


def spaces(num: int):
    """Utility function to easily indent strings."""
    return " " * num


def completed_future():
    """Utility function to create a stub Future object that asyncio can wait for."""
    future = asyncio.Future()
    future.set_result(True)
    return future


def split_docstring(doc):
    """Split docstring into first line (header) and full body."""
    return (doc.split("\n", 1)[0], doc) if doc is not None else ("", "")
