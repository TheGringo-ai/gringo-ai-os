#!/usr/bin/env python3
"""Basic test file for parallel testing demo"""

def test_addition():
    assert 2 + 2 == 4
    print("✅ Addition test passed")

def test_string():
    assert "hello".upper() == "HELLO"
    print("✅ String test passed")

if __name__ == "__main__":
    test_addition()
    test_string()
    print("All basic tests passed!")
