from calculator import add, subtract, multiply, divide

assert add(2, 3) == 5, f"add(2, 3) devolvió {add(2, 3)}, esperaba 5"
assert subtract(5, 2) == 3, f"subtract(5, 2) devolvió {subtract(5, 2)}, esperaba 3"
assert multiply(3, 4) == 12, f"multiply(3, 4) devolvió {multiply(3, 4)}, esperaba 12"
assert divide(10, 2) == 5, f"divide(10, 2) devolvió {divide(10, 2)}, esperaba 5"
assert divide(10, 0) == "Error: División por cero", (
    f"divide(10, 0) devolvió {divide(10, 0)!r}"
)

print("All tests passed!")
