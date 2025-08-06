import os
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def create_followup_task(task_description):
    """Log follow-up tasks to tasks.json"""
    try:
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as f:
                tasks = json.load(f)
        else:
            tasks = []
        
        tasks.append({
            "task": task_description,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "status": "pending"
        })
        
        with open("tasks.json", "w") as f:
            json.dump(tasks, f, indent=2)
        
        print(f"📝 Task logged: {task_description}")
    except Exception as e:
        print(f"⚠️ Failed to log task: {e}")

def run_runtime_check(entry_file=None):
    """Attempt to run all detected entry points (in parallel if multiple) or the specified file, capturing runtime errors."""
    print("🚀 Running runtime execution check...")

    candidate_files = ["main.py", "app.py", "server.py", "run.py"]

    # Auto-detect entry files if not specified
    if entry_file is None:
        detected_entries = [f for f in candidate_files if os.path.exists(f)]
    else:
        detected_entries = [entry_file] if os.path.exists(entry_file) else []

    if not detected_entries:
        print("ℹ️ No entry files found (main.py, app.py, server.py, run.py). Skipping runtime check.")
        return True

    def run_entry(entry):
        print(f"🚀 Testing entry point: {entry}")
        try:
            result = subprocess.run(["python3", entry], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Runtime executed successfully for {entry}")
                return True
            else:
                print(f"❌ Runtime error in {entry}:\n{result.stderr}")
                create_followup_task(f"Fix runtime error in {entry}: {result.stderr.splitlines()[0]}")
                return False
        except Exception as e:
            print(f"⚠️ Runtime check error for {entry}: {e}")
            create_followup_task(f"Investigate runtime execution error for {entry}")
            return False

    all_passed = True
    with ThreadPoolExecutor(max_workers=len(detected_entries)) as executor:
        futures = {executor.submit(run_entry, entry): entry for entry in detected_entries}
        for future in as_completed(futures):
            success = future.result()
            if not success:
                all_passed = False

    return all_passed

def run_parallel_tests(test_pattern="test_*.py"):
    """Run all test files in parallel for faster validation"""
    print("🧪 Running parallel test execution...")
    
    import glob
    test_files = glob.glob(test_pattern)
    
    if not test_files:
        print(f"ℹ️ No test files found matching pattern '{test_pattern}'. Skipping test run.")
        return True
    
    print(f"📋 Found {len(test_files)} test files: {', '.join(test_files)}")
    
    def run_test_file(test_file):
        print(f"🧪 Running test file: {test_file}")
        try:
            result = subprocess.run(["python3", test_file], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ Tests passed in {test_file}")
                return True
            else:
                print(f"❌ Tests failed in {test_file}:\n{result.stderr}")
                create_followup_task(f"Fix failing tests in {test_file}: {result.stderr.splitlines()[0] if result.stderr else 'Unknown error'}")
                return False
        except subprocess.TimeoutExpired:
            print(f"⏰ Test timeout in {test_file}")
            create_followup_task(f"Investigate timeout in test file {test_file}")
            return False
        except Exception as e:
            print(f"⚠️ Test execution error for {test_file}: {e}")
            create_followup_task(f"Fix test execution error in {test_file}")
            return False
    
    all_passed = True
    with ThreadPoolExecutor(max_workers=min(len(test_files), 4)) as executor:
        futures = {executor.submit(run_test_file, test_file): test_file for test_file in test_files}
        for future in as_completed(futures):
            success = future.result()
            if not success:
                all_passed = False
    
    if all_passed:
        print("✅ All parallel tests completed successfully!")
    else:
        print("❌ Some tests failed - check tasks.json for follow-ups")
    
    return all_passed

def run_full_validation(entry_pattern=None, test_pattern="test_*.py"):
    """Run both runtime checks and tests in parallel for complete validation"""
    print("🚀 Starting full parallel validation...")
    
    runtime_success = run_runtime_check(entry_pattern)
    test_success = run_parallel_tests(test_pattern)
    
    if runtime_success and test_success:
        print("🎉 Full validation passed - all systems operational!")
        return True
    else:
        print("⚠️ Validation issues detected - check tasks.json for details")
        return False
