import subprocess
import difflib
import os
import sys
from subprocess import TimeoutExpired
import re

# Compile source code file function.
# ARGUMENTS:
#   - source code file name:
#       src_filename;
#   - output executable file name:
#       out_filename;
#   - file extension:
#       ext;
# RETURNS:
#   (bool, string) compile success and error message or output string.
#
def compile(src_filename, out_filename, ext):
    compile_cmd = ''
    print(f"Debug: ext = {ext}")
    if ext == '.C':
        compile_cmd = ["clang", "-std=c99", src_filename, "-o", out_filename]
    elif ext == '.v':
        compile_cmd = ["coqc", "-v", src_filename, "-o", out_filename]

    # Check result
    result = subprocess.run(compile_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False, result.stderr
    
    return True, result.stdout
# End of 'compile' function

# Check Coq goals completion function.
# ARGUMENTS:
#   - file path:
#       file_path;
# RETURNS:
#   (?) ?.
#
def check_coq_goals(file_path, goals_path):
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    process = subprocess.run(["coqtop", "-quiet"], input=file_content, capture_output=True, text=True)

    return process.stdout, process.stderr
# End of 'check_coq_goals' function

# Run program on input test function.
# ARGUMENTS:
#   - executable file name:
#       exe_filename;
#   - test input string:
#       test_input;
#   - maximum program execution time in seconds:
#       timeout_sec;
# RETURNS:
#   (string, string) a string that program outputs and error (if occured).
#
def run(exe_filename, test_input, timeout_sec = 3):
    passed = True
    try:
        # print(f"Debug: exe_filename: {exe_filename}, test_input: {test_input}")
        result = subprocess.run(
            [exe_filename],
            input=test_input,
            capture_output=True,
            text=True,
            timeout = timeout_sec,
            check=True
        )
    except TimeoutExpired as e:
        print("Error: Program execution time limit exceeded!")
        return False, "", f"Error: Program execution time limit exceeded! ({timeout_sec} sec)\n"
    except subprocess.CalledProcessError as e:
        print(f"Error: Program execution failed. Error code: {e.returncode}:\n  {e.stderr}")
        return False, "", f"Error: Program execution failed. Error code: {e.returncode}:\n  {e.stderr}\n"

    return passed, result.stdout.strip(), ""
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
def compare(program_output_lines, expected_output_lines, tol):
    program_output_lines = program_output_lines.strip().splitlines()
    expected_output_lines = expected_output_lines.strip().splitlines()

    # Compare number of strings
    if len(program_output_lines) != len(expected_output_lines):
        return False, f"Correct output:\n  {"\n".join(expected_output_lines)}\nYour output:\n  {"\n".join(program_output_lines)}\n"

    # Find all numbers in program output
    num_pat = re.compile(r'-?\d+(?:\.\d+)?')
    for pl, el in zip(program_output_lines, expected_output_lines):
        # Cut numbers from output string and compare cut strings
        if num_pat.sub('', pl) != num_pat.sub('', el):
            return False, f"Correct output:\n  {"\n".join(expected_output_lines)}\nYour output:\n  {"\n".join(program_output_lines)}\n"
        
        # Convert numbers to floats
        pnums = [float(x) for x in num_pat.findall(pl)]
        enums = [float(x) for x in num_pat.findall(el)]

        # Compare number of numbers
        if len(pnums) != len(enums):
            return False, f"Correct output:\n  {"\n".join(expected_output_lines)}\nYour output:\n  {"\n".join(program_output_lines)}\n"
        
        # Compare numbers with a given precision
        for p, e in zip(pnums, enums):
            if abs(p - e) > tol:
                return False, f"Correct output:\n  {"\n".join(expected_output_lines)}\nYour output:\n  {"\n".join(program_output_lines)}\n"

    return True, ""
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

    tests_filename = "test.txt"
    full_path = os.path.join(tests_dir, tests_filename)
    print(f"Debug: Test file path: {full_path}")
    try:
        with open(full_path, "r") as f:
            content = f.read().split("####### TEST CASE #######")[1:]
    except FileNotFoundError:
        print(f"Internal tests error: Test file '{tests_filename}' does not exist.")
        return False, f"Internal tests error: Test file '{tests_filename}' does not exist.\n"
    except:
        return False, f"Internal tests error: Something wrong with tests.\n"

    # print(f"Debug: Variable 'content': {content}")
    for test_case in content:
        is_regex = False

        # Split test input and expected ouput on two strings
        parts = test_case.strip().split("---")

        # Check if it is a regex format
        if parts[0].strip() == "@-$%regex@-$%":
            is_regex = True

        test_input = parts[0].strip()
        expexted_ouput = parts[1].strip()
        # print(f"Debug: Test #{i}: {test_input}\n{expexted_ouput}")

        # Run program on test        
        passed, program_ouput, err = run(exe_filename, test_input if not is_regex else "")
        if not passed:
            print(err)
            return False, err
            
        # Compare program output with correct output
        if not is_regex:
            passed, diff = compare(program_ouput, expexted_ouput, 1e-2)
            if not passed:
                report += f"Test {i}: FAIL\n{diff}\n"
                all_passed = False
        else:
            print(f"Debug: Regex found: {expexted_ouput}, Program output:\n{program_ouput}")
            match = re.fullmatch(expexted_ouput, program_ouput)
            if not match:
                report += f"Wrong answer format:\n{program_ouput}\n"
                all_passed = False
        
        i += 1

    if i == 1:
        print(f"Internal tests error: test file in '{tests_dir}' is empty or there is no suitable tests.")
        return False, f"Internal tests error: test file is empty or there is no suitable tests.\n"

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
