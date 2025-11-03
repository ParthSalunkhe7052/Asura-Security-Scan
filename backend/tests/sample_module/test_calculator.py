"""
Test suite for calculator module
These tests will be used by mutmut to evaluate mutation coverage
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path to import calculator
sys.path.insert(0, str(Path(__file__).parent))

from calculator import (
    add, subtract, multiply, divide,
    is_even, is_positive, factorial,
    max_of_three, is_palindrome
)


class TestArithmetic:
    """Test arithmetic operations"""
    
    def test_add(self):
        assert add(2, 3) == 5
        assert add(-1, 1) == 0
        assert add(0, 0) == 0
        assert add(-5, -3) == -8
    
    def test_subtract(self):
        assert subtract(5, 3) == 2
        assert subtract(0, 5) == -5
        assert subtract(-3, -3) == 0
        assert subtract(10, 3) == 7
    
    def test_multiply(self):
        assert multiply(2, 3) == 6
        assert multiply(-2, 3) == -6
        assert multiply(0, 5) == 0
        assert multiply(-2, -3) == 6
    
    def test_divide(self):
        assert divide(6, 2) == 3
        assert divide(5, 2) == 2.5
        assert divide(-6, 2) == -3
        assert divide(0, 5) == 0
    
    def test_divide_by_zero(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)


class TestPredicates:
    """Test boolean predicate functions"""
    
    def test_is_even(self):
        assert is_even(2) == True
        assert is_even(3) == False
        assert is_even(0) == True
        assert is_even(-4) == True
        assert is_even(-3) == False
    
    def test_is_positive(self):
        assert is_positive(5) == True
        assert is_positive(-5) == False
        assert is_positive(0) == False
        assert is_positive(0.1) == True


class TestFactorial:
    """Test factorial function"""
    
    def test_factorial_base_cases(self):
        assert factorial(0) == 1
        assert factorial(1) == 1
    
    def test_factorial_positive(self):
        assert factorial(5) == 120
        assert factorial(3) == 6
        assert factorial(4) == 24
    
    def test_factorial_negative(self):
        with pytest.raises(ValueError, match="Factorial not defined for negative"):
            factorial(-1)


class TestMaxOfThree:
    """Test max_of_three function"""
    
    def test_max_first(self):
        assert max_of_three(10, 5, 3) == 10
    
    def test_max_second(self):
        assert max_of_three(5, 10, 3) == 10
    
    def test_max_third(self):
        assert max_of_three(5, 3, 10) == 10
    
    def test_max_equal(self):
        assert max_of_three(5, 5, 5) == 5
        assert max_of_three(5, 5, 3) == 5


class TestPalindrome:
    """Test palindrome checker"""
    
    def test_palindrome_simple(self):
        assert is_palindrome("racecar") == True
        assert is_palindrome("hello") == False
    
    def test_palindrome_case_insensitive(self):
        assert is_palindrome("Racecar") == True
        assert is_palindrome("RaceCar") == True
    
    def test_palindrome_with_spaces(self):
        assert is_palindrome("race car") == True
        assert is_palindrome("A man a plan a canal Panama") == True
    
    def test_palindrome_single_char(self):
        assert is_palindrome("a") == True
    
    def test_palindrome_empty(self):
        assert is_palindrome("") == True
