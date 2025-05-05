from flask import Flask, request, jsonify, send_file, send_from_directory, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import subprocess
import os
import random
# from solcheck.reformat import reformat, check_clang
from solcheck.check import compile, run_tests
import hashlib
from flask_cors import CORS
import sys

# Create flask app
app = Flask(__name__, static_folder="./static")

# Initialize limiter
limiter = Limiter(
    app=app,
    
    key_func=get_remote_address
)

# Set directories
UPLOAD_DIR = "./out/uploads"
OUT_DIR = "./out"
TESTS_DIR = "./tests"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TESTS_DIR, exist_ok=True)

cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Check source code style with clang-format function
# ARGUMENTS: None.
# RETURNS:
#   JSON object with message.
#

@app.route('/test')
def test_route():
    return 'hi world'

@app.route("/", methods=["POST"])
@limiter.limit("3 per 5 seconds")
def check():
    # return jsonify({"error": "Wait..."}), 400
    # Check if file uploaded
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    # Check file suitability
    file = request.files["file"]

    # Check that program name matches selected name
    task_name = request.form.get("task", "")
    if file.filename != (task_name + ".C"):
        return jsonify({"error": "Error: Wrong task selected or wrong file name.\n\n"
                                 "File name must match this format: <TASK_NAME>.C, "
                                 "where <TASK_NAME> is the task name you selected."}), 400

    # Save lowered filename    
    filename = file.filename.lower()
    if not (filename.endswith(".c")):
        return jsonify({"error": "Error: Only .C files are allowed"}), 400

    # Check 

    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    file_path = file_path.lower()
    print(f"Debug: Variable: file_path: {file_path}")
    file.save(file_path)


    # # Reformat code
    # print(f"Debug: Function call 'reformat(\"{file_path}\")'")
    # success, reformat_message = reformat(file_path)
    # if not success:
    #     return jsonify({"error": reformat_message}), 400
    
    # # Check that program name matches selected name
    # task_name = request.form.get("task", "")
    # if file.filename != (task_name + ".C"):
    #     return jsonify({"error": "Error: Wrong task selected or wrong file name.\n\n"
    #                              "File name must match this format: <TASK_NAME>.C, "
    #                              "where <TASK_NAME> is the task name you selected."}), 400
    
    # formatted_file_path = file_path.replace('.C', '_reformat.c')

    # # Check code style with clang-format
    # print(f"Debug: Function call 'check_clang(\"{formatted_file_path}\")'")
    # success, check_message = check_clang(formatted_file_path)
    # if not success:
    #     return jsonify({"error": check_message}), 400
    
    ### TODO : DELETE
    formatted_file_path = file_path

    # Compile program
    solution_name, ext = os.path.splitext(filename)
    print(f"Debug: Variable: solution_name: {solution_name}")

    exe_path = os.path.join(OUT_DIR, filename.replace(".c", ""))  # for Windows: exe_path = os.path.join(OUT_DIR, filename.replace(".c", ".exe"))
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

    # Delete executable file.
    try:
        os.remove(exe_path)
    except Exception as e:
        print(f"Warning: could not remove executable: {e}")


    os.remove(formatted_file_path)

    # Get task verification code
    print(f"Debug: Task name for hash: {os.path.basename(file_path).encode('utf-8')}")
    hash = hashlib.sha256(os.path.basename(file_path).encode('utf-8')).hexdigest()

    # TODO : Delete this
    reformat_message = "Delete this."
    check_message = "Delete this."
    return jsonify({
        "reformat": reformat_message, "check": check_message,
        "compile": compile_message, "tests": tests_message,
        "verificationCode": hash
        })
# End of 'check_style' function

@app.route('/', methods=['GET'])
def index():
    # if random.random() < 1/100:
    #     return redirect('...')

    return send_from_directory('./static', 'index.html')

# Limiter error hanfler function.
# ARGUMENTS:
#   - error code:
#       e;
# RETURNS:
#   (json) error message.
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": f"Too many requests. Please stop spamming."}), 429
# End of 'ratelimit_handler' function

# Launch process    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=443, ssl_context=('../cert/fullchain.pem', '../cert/privkey.pem'))
