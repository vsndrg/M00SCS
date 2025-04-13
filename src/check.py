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
#   - test input string:
#       test_input;
# RETURNS:
#   (string) a string that program outputs.
#
def run(exe_filename, test_input):
    result = subprocess.run([exe_filename], input=test_input, capture_output=True, text=True)
    return result.stdout.strip()
# End of 'run' function

# Compare program output with test answers funciton.
# ARGUMENTS:
#   - program ouput string:
#       program_ouput;
#   - expexted ouptut string:
#       expected_path;
# RETURNS:
#   (bool, string) success of comparing and differences with original output (if they are).
#
def compare(program_output, expected_output):
    program_output = program_output.strip()
    expected_output = expected_output.strip()

    if program_output == expected_output:
        return True, ""
    
    return False, f"  Correct ouput: {expected_output}\n  Your output: {program_output}\n"
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

    print(f"Debug: Test file path: {os.path.join(tests_dir, "test.txt")}")
    with open(os.path.join(tests_dir, "test.txt"), "r") as f:
        content = f.read().split("####### TEST CASE #######")[1:]

    for test_case in content:
        parts = test_case.strip().split("---")
        test_input = parts[0].strip()
        expexted_ouput = parts[1].strip()
        # print(f"Debug: Test #{i}: {test_input}\n{expexted_ouput}")
        
        program_ouput = run(exe_filename, test_input)
        passed, diff = compare(program_ouput, expexted_ouput)

        # if passed:
        #     report += f"Test {i}: PASS\n"
        if not passed:
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
