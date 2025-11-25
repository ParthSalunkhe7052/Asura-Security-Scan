def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    """Divide a by b with zero check"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def is_even(n):
    """Check if a number is even"""
    return n % 2 == 0

def is_positive(n):
    """Check if a number is positive (greater than zero)"""
    return n > 0

def factorial(n):
    """Calculate factorial of n"""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def max_of_three(a, b, c):
    """Return the maximum of three numbers"""
    if a >= b and a >= c:
        return a
    elif b >= a and b >= c:
        return b
    else:
        return c

def is_palindrome(s):
    """Check if a string is a palindrome (case-insensitive, ignores spaces)"""
    # Remove spaces and convert to lowercase
    cleaned = s.replace(" ", "").lower()
    # Check if it reads the same forwards and backwards
    return cleaned == cleaned[::-1]
