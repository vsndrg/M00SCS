import subprocess
import difflib
import os
import sys

# Compile source code file function.
# ARGUMENTS:
#   - source code file name:
#       src_filename;
#   - output executable file name:
#       out_filename;
# RETURNS:
#   (bool, string) compile success and error message or output string.
#
def compile(src_filename, out_filename):
    compile_cmd = ["clang", "-std=c99", src_filename, "-o", out_filename]
    result = subprocess.run(compile_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return False, result.stderr
    
    return True, result.stdout
# End of 'compile' function

# Run program on input test function.
# ARGUMENTS:
#   - executable file name:
#       exe_filename;
#   - test file name:
#       test_filename;
# RETURNS:
#   (string) a string that program outputs.
#
def run(exe_filename, test_filename):
    with open(test_filename, "r", encoding="utf-8") as fein:
        result = subprocess.run([exe_filename], stdin=fein, capture_output=True, text=True)
    return result.stdout
# End of 'run' function

# Compare program output with test answers funciton.
# ARGUMENTS:
#   - program ouput string:
#       program_ouput;
#   - expexted ouput file path:
#       expected_path;
# RETURNS:
#   (bool, string) success of comparing and differences with original output (if they are).
#
def compare(program_ouput, expected_path):
    with open(expected_path, "r", encoding="utf-8") as f:
        expected_ouput = f.read()
    
    program_ouput = program_ouput.strip()
    expected_ouput = expected_ouput.strip()

    if program_ouput == expected_ouput:
        return True, ""
    
    return False, f"  Correct ouput: {expected_ouput}\n  Your output: {program_ouput}\n"
# End of 'compare' function

# Run program on test data function.
# ARGUMENTS:
#   - executable file name:
#       exe_filename;
#   - test data directory:
#       tests_dir;
# RETURNS:
#   (bool, string) True if all tests passed, False otherwise, report if test(s) failed.
#
def run_tests(exe_filename, tests_dir):
    i = 1
    all_passed = True
    report = ""

    while True:
        input_path = os.path.join(tests_dir, f"input{i}.txt")
        expected_path = os.path.join(tests_dir, f"expected{i}.txt")

        if not (os.path.exists(input_path) and os.path.exists(expected_path)):
            break
        
        program_ouput = run(exe_filename, input_path)
        passed, diff = compare(program_ouput, expected_path)

        if passed:
            report += f"Test {i}: PASS\n"
        else:
            report += f"Test {i}: FAIL\n{diff}\n"
            all_passed = False
        
        i += 1

    if i == 1:
        print(f"Error: No tests found in {tests_dir} directory")
        return False, f"Internal tests error."

    return all_passed, report
# End of 'run_tests' function

# Main program function.
# ARGUMENTS: None.
# RETURNS: None.
#
def main():
    if len(sys.argv) < 2:
        print("Usage: python test_runner.py <source_file>.c")
        sys.exit(1)

    src_filename = sys.argv[1]
    exe_filename = f"{os.path.split(src_filename)[0]}.exe"

    success, compile_output = compile(src_filename, exe_filename)

    if not success:
        print("Error: Compilation failed:")
        print(compile_output)
        sys.exit(1)
    else:
        print("Error: Compilation successful.")

    tests_dir = "tests"
    passed, report = run_tests(exe_filename, tests_dir)
    print(report)

    if passed:
        print("All tests passed!")
    else:
        print("Some tests failed.")
# End of 'main' function
