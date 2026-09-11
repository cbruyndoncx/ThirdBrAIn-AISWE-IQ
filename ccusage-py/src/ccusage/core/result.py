"""Result pattern implementation for functional error handling."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

T = TypeVar("T")
E = TypeVar("E", bound=Exception)
U = TypeVar("U")


@dataclass(frozen=True)
class Ok[T]:
    """Success result containing a value."""

    value: T

    def is_ok(self) -> bool:
        """Check if this is an Ok result."""
        return True

    def is_err(self) -> bool:
        """Check if this is an Err result."""
        return False


@dataclass(frozen=True)
class Err[E]:
    """Error result containing an exception."""

    error: E

    def is_ok(self) -> bool:
        """Check if this is an Ok result."""
        return False

    def is_err(self) -> bool:
        """Check if this is an Err result."""
        return True


# Type alias for Result
Result = Ok[T] | Err[E]


class ResultHelper:
    """Helper class for working with Result types."""

    @staticmethod
    def ok(value: T) -> Result[T, Any]:
        """Create an Ok result."""
        return Ok(value)

    @staticmethod
    def err(error: E) -> Result[Any, E]:
        """Create an Err result."""
        return Err(error)

    @staticmethod
    def is_ok(result: Result[T, E]) -> bool:
        """Check if result is Ok."""
        return isinstance(result, Ok)

    @staticmethod
    def is_err(result: Result[T, E]) -> bool:
        """Check if result is Err."""
        return isinstance(result, Err)

    @staticmethod
    def unwrap(result: Result[T, E]) -> T:
        """Unwrap result value or raise exception."""
        match result:
            case Ok(value):
                return value
            case Err(error):
                raise error

    @staticmethod
    def unwrap_or(result: Result[T, E], default: T) -> T:
        """Unwrap result value or return default."""
        match result:
            case Ok(value):
                return value
            case Err(_):
                return default

    @staticmethod
    def unwrap_or_else(result: Result[T, E], func: Callable[[E], T]) -> T:
        """Unwrap result value or call function with error."""
        match result:
            case Ok(value):
                return value
            case Err(error):
                return func(error)

    @staticmethod
    def map_result(result: Result[T, E], func: Callable[[T], U]) -> Result[U, E]:
        """Map function over Ok value."""
        match result:
            case Ok(value):
                return Ok(func(value))
            case Err(error):
                return Err(error)

    @staticmethod
    def map_err(result: Result[T, E], func: Callable[[E], U]) -> Result[T, U]:
        """Map function over Err value."""
        match result:
            case Ok(value):
                return Ok(value)
            case Err(error):
                return Err(func(error))

    @staticmethod
    def and_then(result: Result[T, E], func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Chain result with function that returns Result."""
        match result:
            case Ok(value):
                return func(value)
            case Err(error):
                return Err(error)

    @staticmethod
    def or_else(result: Result[T, E], func: Callable[[E], Result[T, U]]) -> Result[T, U]:
        """Chain error with function that returns Result."""
        match result:
            case Ok(value):
                return Ok(value)
            case Err(error):
                return func(error)

    @staticmethod
    def try_fn(func: Callable[[], T]) -> Result[T, Exception]:
        """Try to execute function and return Result."""
        try:
            return Ok(func())
        except Exception as e:
            return Err(e)

    @staticmethod
    async def try_async(func: Callable[[], T]) -> Result[T, Exception]:
        """Try to execute async function and return Result."""
        try:
            result = await func()
            return Ok(result)
        except Exception as e:
            return Err(e)

    @staticmethod
    def collect(results: list[Result[T, E]]) -> Result[list[T], E]:
        """Collect list of Results into Result of list."""
        values = []
        for result in results:
            match result:
                case Ok(value):
                    values.append(value)
                case Err(error):
                    return Err(error)
        return Ok(values)

    @staticmethod
    def collect_errors(results: list[Result[T, E]]) -> tuple[list[T], list[E]]:
        """Collect Results into separate lists of values and errors."""
        values = []
        errors = []
        for result in results:
            match result:
                case Ok(value):
                    values.append(value)
                case Err(error):
                    errors.append(error)
        return values, errors


# Convenience functions for common operations
def ok[T](value: T) -> Result[T, Any]:
    """Create an Ok result."""
    return ResultHelper.ok(value)


def err[E](error: E) -> Result[Any, E]:
    """Create an Err result."""
    return ResultHelper.err(error)


def is_ok[T, E](result: Result[T, E]) -> bool:
    """Check if result is Ok."""
    return ResultHelper.is_ok(result)


def is_err[T, E](result: Result[T, E]) -> bool:
    """Check if result is Err."""
    return ResultHelper.is_err(result)


def unwrap[T, E](result: Result[T, E]) -> T:
    """Unwrap result value or raise exception."""
    return ResultHelper.unwrap(result)


def unwrap_or(result: Result[T, E], default: T) -> T:
    """Unwrap result value or return default."""
    return ResultHelper.unwrap_or(result, default)


def try_fn[T](func: Callable[[], T]) -> Result[T, Exception]:
    """Try to execute function and return Result."""
    return ResultHelper.try_fn(func)


async def try_async[T](func: Callable[[], T]) -> Result[T, Exception]:
    """Try to execute async function and return Result."""
    return await ResultHelper.try_async(func)
