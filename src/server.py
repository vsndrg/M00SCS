from flask import Flask, request, jsonify
import subprocess
import os
from reformat import reformat, check_clang
from check import compile, run_tests
import hashlib
from flask_cors import CORS

app = Flask(__name__, static_folder="./static")
UPLOAD_DIR = "../out/uploads"
OUT_DIR = "../out"
TESTS_DIR = "../tests"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TESTS_DIR, exist_ok=True)

cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Check source code style with clang-format function
# ARGUMENTS: None.
# RETURNS:
#   JSON object with message.
#
@app.route("/", methods=["POST"])
def check():
    # Check if file uploaded
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    # Check file suitability
    file = request.files["file"]
    if not (file.filename.endswith(".c") or file.filename.endswith(".C")):
        return jsonify({"error": "Only .c files are allowed"}), 400
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(file_path)

    # Check function headers errros and reformat file content
    print(f"Debug: Function call 'reformat(\"{file_path}\")'")
    success, reformat_message = reformat(file_path)
    if not success:
        return jsonify({"error": reformat_message}), 400
    
    formatted_file_path = file_path.replace('.c', '_reformat.c')

    # Check code style with clang-format
    print(f"Debug: Function call 'check_clang(\"{formatted_file_path}\")'")
    success, check_message = check_clang(formatted_file_path)
    if not success:
        return jsonify({"error": check_message}), 400
    

    # Compile program
    solution_name, ext = os.path.splitext(file.filename)

    exe_path = os.path.join(OUT_DIR, file.filename.replace(".c", ".exe"))
    print(f"Debug: Function call 'compile(\"{formatted_file_path}\", \"{exe_path}\")'")
    success, compile_message = compile(formatted_file_path, exe_path)
    if not success:
        return jsonify({"error": compile_message}), 400
    
    # Check program output on tests
    print(f"Debug: Variable: solution_name: \"{solution_name}\"")
    print(f"Debug: Function call 'run_tests(\"{exe_path}\", \"{os.path.join(TESTS_DIR, solution_name)}\")'")
    success, tests_message = run_tests(exe_path, os.path.join(TESTS_DIR, solution_name))
    print(tests_message)
    if not success:
        return jsonify({"error": tests_message}), 400

    # Delete executable file
    try:
        os.remove(exe_path)
    except Exception as e:
        print(f"Warning: could not remove executable: {e}")


    os.remove(formatted_file_path)

    # Get task verification code
    hash = hashlib.sha256(os.path.basename(file_path).encode('utf-8')).hexdigest()

    return jsonify({
        "reformat": reformat_message, "check": check_message,
        "compile": compile_message, "tests": tests_message,
        "verificationCode": hash
        })
# End of 'check_style' function

# Launch process    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)