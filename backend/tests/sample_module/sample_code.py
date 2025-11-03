def simple_function(x):
    '''Simple function with complexity 1'''
    return x + 1

def moderate_function(x, y):
    '''Moderate complexity function'''
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    else:
        return 0

def complex_function(a, b, c):
    '''Complex function with multiple branches'''
    result = 0
    if a > 0:
        result += a
    if b > 0:
        result += b
    elif b < 0:
        result -= b
    
    if c > 0:
        if result > 10:
            return result * c
        else:
            return result + c
    else:
        return result