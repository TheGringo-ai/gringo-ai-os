#!/usr/bin/env python3
"""
Gringo's Parallel Agent Runner
Demonstrates parallel runtime + test execution
"""

import fredfix_agent
import sys

def main():
    print("🎯 Gringo's Parallel Agent - Ready for Action!")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "runtime":
            return fredfix_agent.run_runtime_check()
        elif mode == "tests":
            return fredfix_agent.run_parallel_tests()
        elif mode == "full":
            return fredfix_agent.run_full_validation()
        else:
            print(f"Unknown mode: {mode}")
            return False
    else:
        # Default: run full validation
        return fredfix_agent.run_full_validation()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
