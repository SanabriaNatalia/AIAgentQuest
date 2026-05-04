from calculator import add, subtract, multiply, divide

assert add(2, 3) == 5
assert subtract(5, 2) == 3
assert multiply(3, 4) == 12
assert divide(10, 2) == 5
assert divide(10, 0) == "Error: División por cero"