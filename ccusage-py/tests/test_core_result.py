"""Tests for core result pattern implementation."""

from __future__ import annotations

import pytest

from ccusage.core.result import (
    Ok, Err, Result, ResultHelper,
    ok, err, is_ok, is_err, unwrap, unwrap_or, try_fn, try_async
)


class TestOkClass:
    """Test the Ok class."""
    
    def test_ok_creation(self):
        """Test Ok creation."""
        result = Ok(42)
        assert result.value == 42
        assert result.is_ok() is True
        assert result.is_err() is False
    
    def test_ok_with_none(self):
        """Test Ok with None value."""
        result = Ok(None)
        assert result.value is None
        assert result.is_ok() is True
        assert result.is_err() is False
    
    def test_ok_with_string(self):
        """Test Ok with string value."""
        result = Ok("test")
        assert result.value == "test"
        assert result.is_ok() is True
        assert result.is_err() is False


class TestErrClass:
    """Test the Err class."""
    
    def test_err_creation(self):
        """Test Err creation."""
        error = ValueError("test error")
        result = Err(error)
        assert result.error is error
        assert result.is_ok() is False
        assert result.is_err() is True
    
    def test_err_with_string(self):
        """Test Err with string error."""
        result = Err("string error")
        assert result.error == "string error"
        assert result.is_ok() is False
        assert result.is_err() is True


class TestResultHelper:
    """Test the ResultHelper static methods."""
    
    def test_ok_creation(self):
        """Test ResultHelper.ok()."""
        result = ResultHelper.ok(42)
        assert isinstance(result, Ok)
        assert result.value == 42
    
    def test_err_creation(self):
        """Test ResultHelper.err()."""
        error = ValueError("test")
        result = ResultHelper.err(error)
        assert isinstance(result, Err)
        assert result.error is error
    
    def test_is_ok(self):
        """Test ResultHelper.is_ok()."""
        ok_result = Ok(42)
        err_result = Err(ValueError("test"))
        
        assert ResultHelper.is_ok(ok_result) is True
        assert ResultHelper.is_ok(err_result) is False
    
    def test_is_err(self):
        """Test ResultHelper.is_err()."""
        ok_result = Ok(42)
        err_result = Err(ValueError("test"))
        
        assert ResultHelper.is_err(ok_result) is False
        assert ResultHelper.is_err(err_result) is True
    
    def test_unwrap_ok(self):
        """Test ResultHelper.unwrap() with Ok."""
        result = Ok(42)
        assert ResultHelper.unwrap(result) == 42
    
    def test_unwrap_err(self):
        """Test ResultHelper.unwrap() with Err."""
        error = ValueError("test error")
        result = Err(error)
        
        with pytest.raises(ValueError, match="test error"):
            ResultHelper.unwrap(result)
    
    def test_unwrap_or_ok(self):
        """Test ResultHelper.unwrap_or() with Ok."""
        result = Ok(42)
        assert ResultHelper.unwrap_or(result, 99) == 42
    
    def test_unwrap_or_err(self):
        """Test ResultHelper.unwrap_or() with Err."""
        result = Err(ValueError("test"))
        assert ResultHelper.unwrap_or(result, 99) == 99
    
    def test_unwrap_or_else_ok(self):
        """Test ResultHelper.unwrap_or_else() with Ok."""
        result = Ok(42)
        assert ResultHelper.unwrap_or_else(result, lambda e: 99) == 42
    
    def test_unwrap_or_else_err(self):
        """Test ResultHelper.unwrap_or_else() with Err."""
        result = Err(ValueError("test"))
        assert ResultHelper.unwrap_or_else(result, lambda e: 99) == 99
        
        # Test that the function receives the error
        def error_handler(error):
            return f"handled: {error}"
        
        result = Err(ValueError("original error"))
        value = ResultHelper.unwrap_or_else(result, error_handler)
        assert "original error" in value
    
    def test_map_result_ok(self):
        """Test ResultHelper.map_result() with Ok."""
        result = Ok(42)
        mapped = ResultHelper.map_result(result, lambda x: x * 2)
        
        assert isinstance(mapped, Ok)
        assert mapped.value == 84
    
    def test_map_result_err(self):
        """Test ResultHelper.map_result() with Err."""
        error = ValueError("test")
        result = Err(error)
        mapped = ResultHelper.map_result(result, lambda x: x * 2)
        
        assert isinstance(mapped, Err)
        assert mapped.error is error
    
    def test_map_err_ok(self):
        """Test ResultHelper.map_err() with Ok."""
        result = Ok(42)
        mapped = ResultHelper.map_err(result, lambda e: f"mapped: {e}")
        
        assert isinstance(mapped, Ok)
        assert mapped.value == 42
    
    def test_map_err_err(self):
        """Test ResultHelper.map_err() with Err."""
        result = Err(ValueError("original"))
        mapped = ResultHelper.map_err(result, lambda e: f"mapped: {e}")
        
        assert isinstance(mapped, Err)
        assert mapped.error == "mapped: original"
    
    def test_and_then_ok(self):
        """Test ResultHelper.and_then() with Ok."""
        result = Ok(42)
        chained = ResultHelper.and_then(result, lambda x: Ok(x * 2))
        
        assert isinstance(chained, Ok)
        assert chained.value == 84
    
    def test_and_then_ok_returns_err(self):
        """Test ResultHelper.and_then() with Ok that returns Err."""
        result = Ok(42)
        chained = ResultHelper.and_then(result, lambda x: Err(ValueError("chain error")))
        
        assert isinstance(chained, Err)
        assert isinstance(chained.error, ValueError)
    
    def test_and_then_err(self):
        """Test ResultHelper.and_then() with Err."""
        error = ValueError("original")
        result = Err(error)
        chained = ResultHelper.and_then(result, lambda x: Ok(x * 2))
        
        assert isinstance(chained, Err)
        assert chained.error is error
    
    def test_or_else_ok(self):
        """Test ResultHelper.or_else() with Ok."""
        result = Ok(42)
        chained = ResultHelper.or_else(result, lambda e: Ok(99))
        
        assert isinstance(chained, Ok)
        assert chained.value == 42
    
    def test_or_else_err(self):
        """Test ResultHelper.or_else() with Err."""
        result = Err(ValueError("original"))
        chained = ResultHelper.or_else(result, lambda e: Ok(99))
        
        assert isinstance(chained, Ok)
        assert chained.value == 99
    
    def test_or_else_err_returns_err(self):
        """Test ResultHelper.or_else() with Err that returns Err."""
        result = Err(ValueError("original"))
        chained = ResultHelper.or_else(result, lambda e: Err("new error"))
        
        assert isinstance(chained, Err)
        assert chained.error == "new error"
    
    def test_try_fn_success(self):
        """Test ResultHelper.try_fn() with successful function."""
        def successful_func():
            return 42
        
        result = ResultHelper.try_fn(successful_func)
        assert isinstance(result, Ok)
        assert result.value == 42
    
    def test_try_fn_failure(self):
        """Test ResultHelper.try_fn() with failing function."""
        def failing_func():
            raise ValueError("test error")
        
        result = ResultHelper.try_fn(failing_func)
        assert isinstance(result, Err)
        assert isinstance(result.error, ValueError)
        assert str(result.error) == "test error"
    
    @pytest.mark.asyncio
    async def test_try_async_success(self):
        """Test ResultHelper.try_async() with successful async function."""
        async def successful_async_func():
            return 42
        
        result = await ResultHelper.try_async(successful_async_func)
        assert isinstance(result, Ok)
        assert result.value == 42
    
    @pytest.mark.asyncio
    async def test_try_async_failure(self):
        """Test ResultHelper.try_async() with failing async function."""
        async def failing_async_func():
            raise ValueError("async error")
        
        result = await ResultHelper.try_async(failing_async_func)
        assert isinstance(result, Err)
        assert isinstance(result.error, ValueError)
        assert str(result.error) == "async error"
    
    def test_collect_all_ok(self):
        """Test ResultHelper.collect() with all Ok results."""
        results = [Ok(1), Ok(2), Ok(3)]
        collected = ResultHelper.collect(results)
        
        assert isinstance(collected, Ok)
        assert collected.value == [1, 2, 3]
    
    def test_collect_with_err(self):
        """Test ResultHelper.collect() with one Err result."""
        error = ValueError("test error")
        results = [Ok(1), Err(error), Ok(3)]
        collected = ResultHelper.collect(results)
        
        assert isinstance(collected, Err)
        assert collected.error is error
    
    def test_collect_empty_list(self):
        """Test ResultHelper.collect() with empty list."""
        results = []
        collected = ResultHelper.collect(results)
        
        assert isinstance(collected, Ok)
        assert collected.value == []
    
    def test_collect_errors_all_ok(self):
        """Test ResultHelper.collect_errors() with all Ok results."""
        results = [Ok(1), Ok(2), Ok(3)]
        values, errors = ResultHelper.collect_errors(results)
        
        assert values == [1, 2, 3]
        assert errors == []
    
    def test_collect_errors_all_err(self):
        """Test ResultHelper.collect_errors() with all Err results."""
        error1 = ValueError("error1")
        error2 = ValueError("error2")
        results = [Err(error1), Err(error2)]
        values, errors = ResultHelper.collect_errors(results)
        
        assert values == []
        assert errors == [error1, error2]
    
    def test_collect_errors_mixed(self):
        """Test ResultHelper.collect_errors() with mixed results."""
        error = ValueError("test error")
        results = [Ok(1), Err(error), Ok(3)]
        values, errors = ResultHelper.collect_errors(results)
        
        assert values == [1, 3]
        assert errors == [error]
    
    def test_collect_errors_empty_list(self):
        """Test ResultHelper.collect_errors() with empty list."""
        results = []
        values, errors = ResultHelper.collect_errors(results)
        
        assert values == []
        assert errors == []
    
    def test_collect_first_error_stops_iteration(self):
        """Test that collect() stops at the first error and returns it immediately."""
        error1 = ValueError("first error")
        error2 = ValueError("second error")
        results = [Ok(1), Err(error1), Err(error2), Ok(3)]
        collected = ResultHelper.collect(results)
        
        assert isinstance(collected, Err)
        # Should return the first error encountered, not the second
        assert collected.error is error1
        assert str(collected.error) == "first error"
    
    def test_collect_errors_processes_all_items(self):
        """Test that collect_errors() processes all items in the list."""
        error1 = ValueError("error1")
        error2 = ValueError("error2")
        error3 = ValueError("error3")
        results = [Ok(1), Err(error1), Ok(2), Err(error2), Ok(3), Err(error3)]
        values, errors = ResultHelper.collect_errors(results)
        
        # Should collect all values and all errors
        assert values == [1, 2, 3]
        assert errors == [error1, error2, error3]
        assert len(errors) == 3


class TestMatchCaseBranches:
    """Test specific match case branches for complete coverage."""
    
    def test_unwrap_err_case_branch(self):
        """Test the Err case branch in unwrap specifically."""
        custom_error = RuntimeError("custom unwrap error")
        result = Err(custom_error)
        
        # This should hit the 77->exit branch (case Err(error): raise error)
        with pytest.raises(RuntimeError) as exc_info:
            ResultHelper.unwrap(result)
        assert exc_info.value is custom_error
    
    def test_unwrap_or_err_case_branch(self):
        """Test the Err case branch in unwrap_or specifically."""
        result = Err(RuntimeError("any error"))
        default_value = "default_result"
        
        # This should hit the 86->exit branch (case Err(_): return default)
        actual = ResultHelper.unwrap_or(result, default_value)
        assert actual == default_value
    
    def test_unwrap_or_else_err_case_branch(self):
        """Test the Err case branch in unwrap_or_else specifically."""
        original_error = RuntimeError("original error")
        result = Err(original_error)
        
        def error_handler(error):
            return f"handled: {str(error)}"
        
        # This should hit the 95->exit branch (case Err(error): return func(error))
        actual = ResultHelper.unwrap_or_else(result, error_handler)
        assert actual == "handled: original error"
    
    def test_map_result_err_case_branch(self):
        """Test the Err case branch in map_result specifically."""
        original_error = ValueError("mapping error")
        result = Err(original_error)
        
        # This should hit the 104->exit branch (case Err(error): return Err(error))
        mapped = ResultHelper.map_result(result, lambda x: x * 10)
        assert isinstance(mapped, Err)
        assert mapped.error is original_error
    
    def test_map_err_err_case_branch(self):
        """Test the Err case branch in map_err specifically."""
        original_error = ValueError("original")
        result = Err(original_error)
        
        def error_mapper(error):
            return f"mapped_{error}"
        
        # This should hit the 113->exit branch (case Err(error): return Err(func(error)))
        mapped = ResultHelper.map_err(result, error_mapper)
        assert isinstance(mapped, Err)
        assert mapped.error == "mapped_original"
    
    def test_and_then_err_case_branch(self):
        """Test the Err case branch in and_then specifically."""
        original_error = ValueError("chain error")
        result = Err(original_error)
        
        def chain_func(value):
            return Ok(value * 2)
        
        # This should hit the 122->exit branch (case Err(error): return Err(error))
        chained = ResultHelper.and_then(result, chain_func)
        assert isinstance(chained, Err)
        assert chained.error is original_error
    
    def test_or_else_err_case_branch(self):
        """Test the Err case branch in or_else specifically."""
        original_error = ValueError("original error")
        result = Err(original_error)
        
        def recovery_func(error):
            return Ok(f"recovered from {error}")
        
        # This should hit the 131->exit branch (case Err(error): return func(error))
        recovered = ResultHelper.or_else(result, recovery_func)
        assert isinstance(recovered, Ok)
        assert recovered.value == "recovered from original error"


class TestExhaustiveBranchCoverage:
    """Test edge cases to achieve 100% branch coverage."""
    
    def test_exhaustive_match_patterns(self):
        """Test all possible match pattern combinations to ensure exhaustive coverage."""
        # Test with different types of Ok values
        ok_int = Ok(42)
        ok_str = Ok("test")
        ok_none = Ok(None)
        ok_list = Ok([1, 2, 3])
        
        # Test with different types of Err values
        err_value_error = Err(ValueError("test"))
        err_runtime_error = Err(RuntimeError("runtime"))
        err_string = Err("string error")
        err_int = Err(123)
        
        # Exhaustively test each method with both Ok and Err to ensure all branches are hit
        test_cases = [
            (ok_int, "ok_int"),
            (ok_str, "ok_str"), 
            (ok_none, "ok_none"),
            (ok_list, "ok_list"),
            (err_value_error, "err_value_error"),
            (err_runtime_error, "err_runtime_error"),
            (err_string, "err_string"),
            (err_int, "err_int")
        ]
        
        for result, case_name in test_cases:
            # Test unwrap_or - this should hit both Ok and Err branches completely
            default_val = "default"
            actual = ResultHelper.unwrap_or(result, default_val)
            if isinstance(result, Ok):
                assert actual == result.value, f"unwrap_or failed for {case_name}"
            else:
                assert actual == default_val, f"unwrap_or failed for {case_name}"
            
            # Test unwrap_or_else - this should hit both branches completely
            def handler(error):
                return f"handled_{error}"
            actual = ResultHelper.unwrap_or_else(result, handler)
            if isinstance(result, Ok):
                assert actual == result.value, f"unwrap_or_else failed for {case_name}"
            else:
                assert f"handled_{result.error}" == actual, f"unwrap_or_else failed for {case_name}"
            
            # Test map_result - should hit both branches
            def mapper(x):
                return f"mapped_{x}"
            mapped = ResultHelper.map_result(result, mapper)
            if isinstance(result, Ok):
                assert isinstance(mapped, Ok), f"map_result should return Ok for {case_name}"
                assert mapped.value == f"mapped_{result.value}", f"map_result failed for {case_name}"
            else:
                assert isinstance(mapped, Err), f"map_result should return Err for {case_name}"
                assert mapped.error is result.error, f"map_result failed for {case_name}"
            
            # Test map_err - should hit both branches
            def error_mapper(e):
                return f"error_mapped_{e}"
            err_mapped = ResultHelper.map_err(result, error_mapper)
            if isinstance(result, Ok):
                assert isinstance(err_mapped, Ok), f"map_err should return Ok for {case_name}"
                assert err_mapped.value == result.value, f"map_err failed for {case_name}"
            else:
                assert isinstance(err_mapped, Err), f"map_err should return Err for {case_name}"
                assert err_mapped.error == f"error_mapped_{result.error}", f"map_err failed for {case_name}"
            
            # Test and_then - should hit both branches
            def chain_func(x):
                return Ok(f"chained_{x}")
            chained = ResultHelper.and_then(result, chain_func)
            if isinstance(result, Ok):
                assert isinstance(chained, Ok), f"and_then should return Ok for {case_name}"
                assert chained.value == f"chained_{result.value}", f"and_then failed for {case_name}"
            else:
                assert isinstance(chained, Err), f"and_then should return Err for {case_name}"
                assert chained.error is result.error, f"and_then failed for {case_name}"
            
            # Test or_else - should hit both branches
            def recovery_func(e):
                return Ok(f"recovered_from_{e}")
            recovered = ResultHelper.or_else(result, recovery_func)
            if isinstance(result, Ok):
                assert isinstance(recovered, Ok), f"or_else should return Ok for {case_name}"
                assert recovered.value == result.value, f"or_else failed for {case_name}"
            else:
                assert isinstance(recovered, Ok), f"or_else should return Ok for {case_name}"
                assert recovered.value == f"recovered_from_{result.error}", f"or_else failed for {case_name}"
    
    def test_collect_loop_branch_coverage(self):
        """Test collect method with various combinations to hit all loop branches."""
        # Test early return on error (159->155 branch)
        test_cases = [
            # Error at beginning
            [Err(ValueError("first")), Ok(2), Ok(3)],
            # Error in middle  
            [Ok(1), Err(ValueError("middle")), Ok(3)],
            # Error at end
            [Ok(1), Ok(2), Err(ValueError("last"))],
            # Multiple errors (should stop at first)
            [Ok(1), Err(ValueError("first_error")), Err(ValueError("second_error"))],
            # Empty list (loop doesn't execute)
            [],
            # Single Ok
            [Ok(42)],
            # Single Err
            [Err(ValueError("single"))],
        ]
        
        for results in test_cases:
            collected = ResultHelper.collect(results)
            if not results:
                # Empty case
                assert isinstance(collected, Ok) and collected.value == []
            elif all(isinstance(r, Ok) for r in results):
                # All Ok case
                assert isinstance(collected, Ok)
                assert collected.value == [r.value for r in results]
            else:
                # Has error case - should return first error
                assert isinstance(collected, Err)
                first_error = next(r for r in results if isinstance(r, Err))
                assert collected.error is first_error.error
    
    def test_collect_errors_loop_branch_coverage(self):
        """Test collect_errors method to hit all loop branches (172->168)."""
        test_cases = [
            # All Ok
            [Ok(1), Ok(2), Ok(3)],
            # All Err
            [Err(ValueError("e1")), Err(ValueError("e2"))], 
            # Mixed - Ok first
            [Ok(1), Err(ValueError("e1")), Ok(2)],
            # Mixed - Err first
            [Err(ValueError("e1")), Ok(1), Err(ValueError("e2"))],
            # Empty
            [],
            # Single items
            [Ok(42)],
            [Err(ValueError("single"))],
        ]
        
        for results in test_cases:
            values, errors = ResultHelper.collect_errors(results)
            
            expected_values = [r.value for r in results if isinstance(r, Ok)]
            expected_errors = [r.error for r in results if isinstance(r, Err)]
            
            assert values == expected_values, f"Values mismatch for {results}"
            assert errors == expected_errors, f"Errors mismatch for {results}"


class TestCoverageCompletionEdgeCases:
    """Test very specific edge cases to try to achieve 100% branch coverage."""
    
    def test_unwrap_exception_path(self):
        """Test unwrap with exception to ensure exception raising branch is fully covered."""
        # Create different types of errors to test the exception path thoroughly
        test_errors = [
            ValueError("value error"),
            RuntimeError("runtime error"), 
            TypeError("type error"),
            Exception("generic error"),
            KeyError("key error")
        ]
        
        for error in test_errors:
            result = Err(error)
            try:
                ResultHelper.unwrap(result)
                assert False, f"Expected exception for {error}"
            except Exception as raised:
                assert raised is error, f"Exception identity mismatch for {error}"
        
        # Test with non-exception error object - this should raise TypeError
        non_exception_error = "non-exception error object"
        result = Err(non_exception_error)
        try:
            ResultHelper.unwrap(result)
            assert False, "Expected TypeError for non-exception error"
        except TypeError:
            # This is expected - Python requires exceptions to derive from BaseException
            pass
    
    def test_match_statement_fall_through_patterns(self):
        """Test match statements with patterns that should ensure complete branch coverage."""
        # Test the 'default' return patterns in each method very specifically
        
        # Test unwrap_or with different Err patterns
        for error_val in [ValueError("test"), "string", 42, None, [], {}]:
            err_result = Err(error_val)
            default = "fallback_value"
            actual = ResultHelper.unwrap_or(err_result, default)
            assert actual == default, f"unwrap_or failed for error: {error_val}"
        
        # Test unwrap_or_else with function calls
        for error_val in [ValueError("test"), "string", 42]:
            err_result = Err(error_val)
            def error_func(e):
                return f"processed_{e}_end"
            actual = ResultHelper.unwrap_or_else(err_result, error_func)
            assert actual == f"processed_{error_val}_end", f"unwrap_or_else failed for error: {error_val}"
            
        # Test map_result error path
        for error_val in [ValueError("test"), "string", 42]:
            err_result = Err(error_val)
            def never_called(x):
                raise AssertionError("Should not be called")
            mapped = ResultHelper.map_result(err_result, never_called)
            assert isinstance(mapped, Err), f"map_result should return Err for {error_val}"
            assert mapped.error is error_val, f"map_result error identity failed for {error_val}"
            
        # Test map_err error path  
        for error_val in [ValueError("test"), "string", 42]:
            err_result = Err(error_val)
            def transform_error(e):
                return f"transformed_{e}"
            mapped = ResultHelper.map_err(err_result, transform_error)
            assert isinstance(mapped, Err), f"map_err should return Err for {error_val}"
            assert mapped.error == f"transformed_{error_val}", f"map_err failed for {error_val}"
            
        # Test and_then error path
        for error_val in [ValueError("test"), "string", 42]:
            err_result = Err(error_val)
            def never_called(x):
                raise AssertionError("Should not be called")
            chained = ResultHelper.and_then(err_result, never_called)
            assert isinstance(chained, Err), f"and_then should return Err for {error_val}"
            assert chained.error is error_val, f"and_then error identity failed for {error_val}"
            
        # Test or_else error path
        for error_val in [ValueError("test"), "string", 42]:
            err_result = Err(error_val)
            def recovery_func(e):
                return Ok(f"recovered_from_{e}")
            recovered = ResultHelper.or_else(err_result, recovery_func)
            assert isinstance(recovered, Ok), f"or_else should return Ok for {error_val}"
            assert recovered.value == f"recovered_from_{error_val}", f"or_else failed for {error_val}"
    
    def test_collect_exhaustive_early_return(self):
        """Test collect method focusing specifically on early return branch coverage."""
        # Test immediate error return (should hit 159->155 branch)
        immediate_error_cases = [
            [Err("immediate")],  # Single error
            [Err("first"), Ok(1)],  # Error first
            [Err("only_error"), Err("never_reached")],  # Multiple errors, stops at first
        ]
        
        for case in immediate_error_cases:
            result = ResultHelper.collect(case)
            assert isinstance(result, Err), f"Should return Err for {case}"
            # Should be the first error
            first_err = next(r for r in case if isinstance(r, Err))
            assert result.error == first_err.error, f"Should return first error for {case}"
    
    def test_collect_errors_complete_iteration(self):
        """Test collect_errors to ensure complete loop iteration branch coverage."""
        # Test all possible branching patterns in the loop
        test_patterns = [
            # Pattern: Ok, Err, Ok, Err (alternating)
            [Ok(1), Err("e1"), Ok(2), Err("e2")],
            # Pattern: Multiple consecutive Errs
            [Err("e1"), Err("e2"), Err("e3")],
            # Pattern: Multiple consecutive Oks
            [Ok(1), Ok(2), Ok(3)],
            # Pattern: Err at start and end
            [Err("start"), Ok(1), Ok(2), Err("end")],
            # Pattern: Complex mixed
            [Ok(1), Err("e1"), Ok(2), Ok(3), Err("e2"), Ok(4), Err("e3")],
        ]
        
        for pattern in test_patterns:
            values, errors = ResultHelper.collect_errors(pattern)
            expected_values = [r.value for r in pattern if isinstance(r, Ok)]
            expected_errors = [r.error for r in pattern if isinstance(r, Err)]
            assert values == expected_values, f"Values failed for {pattern}"
            assert errors == expected_errors, f"Errors failed for {pattern}"


class TestConvenienceFunctions:
    """Test the convenience functions."""
    
    def test_ok_function(self):
        """Test ok() convenience function."""
        result = ok(42)
        assert isinstance(result, Ok)
        assert result.value == 42
    
    def test_err_function(self):
        """Test err() convenience function."""
        error = ValueError("test")
        result = err(error)
        assert isinstance(result, Err)
        assert result.error is error
    
    def test_is_ok_function(self):
        """Test is_ok() convenience function."""
        ok_result = ok(42)
        err_result = err(ValueError("test"))
        
        assert is_ok(ok_result) is True
        assert is_ok(err_result) is False
    
    def test_is_err_function(self):
        """Test is_err() convenience function."""
        ok_result = ok(42)
        err_result = err(ValueError("test"))
        
        assert is_err(ok_result) is False
        assert is_err(err_result) is True
    
    def test_unwrap_function_ok(self):
        """Test unwrap() convenience function with Ok."""
        result = ok(42)
        assert unwrap(result) == 42
    
    def test_unwrap_function_err(self):
        """Test unwrap() convenience function with Err."""
        error = ValueError("test error")
        result = err(error)
        
        with pytest.raises(ValueError, match="test error"):
            unwrap(result)
    
    def test_unwrap_or_function_ok(self):
        """Test unwrap_or() convenience function with Ok."""
        result = ok(42)
        assert unwrap_or(result, 99) == 42
    
    def test_unwrap_or_function_err(self):
        """Test unwrap_or() convenience function with Err."""
        result = err(ValueError("test"))
        assert unwrap_or(result, 99) == 99
    
    def test_try_fn_function_success(self):
        """Test try_fn() convenience function with success."""
        def successful_func():
            return 42
        
        result = try_fn(successful_func)
        assert isinstance(result, Ok)
        assert result.value == 42
    
    def test_try_fn_function_failure(self):
        """Test try_fn() convenience function with failure."""
        def failing_func():
            raise ValueError("test error")
        
        result = try_fn(failing_func)
        assert isinstance(result, Err)
        assert isinstance(result.error, ValueError)
    
    @pytest.mark.asyncio
    async def test_try_async_function_success(self):
        """Test try_async() convenience function with success."""
        async def successful_async_func():
            return 42
        
        result = await try_async(successful_async_func)
        assert isinstance(result, Ok)
        assert result.value == 42
    
    @pytest.mark.asyncio
    async def test_try_async_function_failure(self):
        """Test try_async() convenience function with failure."""
        async def failing_async_func():
            raise ValueError("async error")
        
        result = await try_async(failing_async_func)
        assert isinstance(result, Err)
        assert isinstance(result.error, ValueError)


if __name__ == "__main__":
    pytest.main([__file__])