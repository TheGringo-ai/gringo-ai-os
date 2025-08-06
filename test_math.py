#!/usr/bin/env python3
"""Math test file for parallel testing demo"""

def test_multiplication():
    assert 3 * 4 == 12
    print("✅ Multiplication test passed")

def test_division():
    assert 8 / 2 == 4
    print("✅ Division test passed")

if __name__ == "__main__":
    test_multiplication()
    test_division()
    print("All math tests passed!")
