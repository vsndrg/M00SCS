from clang import cindex
import chardet
import re
import os
import subprocess

# Initialize libclang
cindex.Config.set_library_file(r"C:/Program Files/LLVM/bin/libclang.dll")
index = cindex.Index.create()

# Read text from file function.
# ARGUMENTS:
#   - file path to read:
#       file_path;
# RETURNS:
#   file content string.
#
def get_text(file_path):
    with open(file_path, "rb") as file:
        file_content = file.read()

    result = chardet.detect(file_content)
    encoding = result['encoding']

    #print(f"File encoding: {encoding}")

    try:
        decoded_content = file_content.decode(encoding)
    except (UnicodeDecodeError, TypeError) as e:
        decoded_content = file_content.decode('utf-8', errors='replace')
        print("Debug: Considered as utf-8")

    return decoded_content
# End of 'get_text' function

# Get function header text function.
# ARGUMENTS:
#   - file content string:
#       file_content
#   - clang cursor:
#       cursor;
# RETURNS:
#   object: (header string, start index, end index).
#
def get_header(file_content, cursor):
    if cursor.kind != cindex.CursorKind.FUNCTION_DECL:
        return "", 0, 0
    extent = cursor.extent
    start_offset = extent.start.offset # Funciton start position in file
    end_offset = extent.end.offset     # Funciton end position in file
    print(f"Debug: Variable: start_offset: {start_offset}, end_offset: {end_offset}",)

    # Extract function text
    function_text = file_content[start_offset:end_offset]

    # Extract function header
    header_part, sep, remainder = function_text.partition('{')
    header_text = re.sub(r'\r?\n\s*', ' ', header_part).strip()

    # Calculate header end offset
    end_offset = start_offset + len(header_part)

    return header_text, start_offset, end_offset
# End of 'get_header' function

# Insert formated header in source code function.
# ARGUMENTS:
#   - file content string:
#       file_content;
#   - header start offset:
#       start_offset;
#   - header end offset:
#       end_offset;
# RETURNS: None.
#
def insert_header(file_content, new_header, start_offset, end_offset):
    return file_content[:start_offset] + new_header + file_content[end_offset - 1:]
# End of 'insert_header' function

# Reformat one header function.
# ARGUMENTS:
#   - function header string:
#       header
# RETURNS:
#   styled header string
#
def reformat_header(header):
    regex = r'^\s*((?:__inline\s|static\s)?(?:unsigned\s)?(?:signed\s)?(?:long\s)*?[a-zA-Z_]\w*)(\s\*+)?\s([a-zA-Z_]\w*)\(\s([a-zA-Z_](?:.*)\w)\s\);?\s*$'  # r'^\s*((?:__inline\s|static\s)?[a-zA-Z_]\w*)(\s\*+)?\s([a-zA-Z_]\w*)\(\s([a-zA-Z_](?:.*)\w)\s\);?\s*$'
    match = re.fullmatch(regex, header)

    formated_header = ""
    error = ""

    if match:
        return_type = match.group(1)
        pointer = match.group(2)
        function_name = match.group(3)
        params = match.group(4)
        formated_header = f"{return_type}{pointer if pointer is not None else ' '}{function_name}({params})"
    else:
        error = f'Error! Wrong style format in function header:\n  "{header}"'

    return formated_header, error
# End of 'reformat_header' function


# Save file content string to file function.
# ARGUMENTS:
#   - original file name:
#       original_filename;
#   - file content string:
#       file_content;
# RETURNS: None.
#
def save_to_file(original_filename, file_content):
    name, ext = os.path.splitext(original_filename)
    new_filename = f"{name}_reformat{ext}"

    file_content = file_content.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')

    with open(new_filename, 'w', encoding="utf-8", newline='') as f:
        f.write(file_content)
# End of 'save_to_file' function

# Reformat function headers in source code file function.
# ARGUMENTS:
#   - source code file name:
#       file_name;
# RETURNS:
#   True if success, False if errors occured.
#
def reformat(file_name):
    # Initialize parser
    original_filename = file_name
    file_name = file_name.lower()
    tu = index.parse(file_name, args=["-nostdinc", "-Xclang -fno-implicit-includes"])
    main_basename = os.path.basename(file_name)

    # Read file content
    file_content = get_text(file_name)

    headers_info = []
    errors = []

    # Find function headers in source code and reformat them
    for cursor in tu.cursor.get_children():
        if cursor.kind == cindex.CursorKind.FUNCTION_DECL and cursor.location.file and os.path.basename(cursor.location.file.name) == main_basename:
            header, start_offset, end_offset = get_header(file_content, cursor)
            print(f"Debug: Function header found: '{header}'")

            new_header, error = reformat_header(header)

            if new_header:
                headers_info.append((new_header, start_offset, end_offset))
            else:
                errors.append(error)

    # Check if errors occured
    if errors:
        return False, "\n".join(errors)

    # Insert formated headers in source code file
    for header, start_offset, end_offset in reversed(headers_info):
        file_content = insert_header(file_content, header, start_offset, end_offset)

    # Save formated code to new file
    no_warnings = "#define _CRT_SECURE_NO_WARNINGS\r\n"
    save_to_file(original_filename, no_warnings + file_content)

    return True, "Reformatting successful!"
# End of 'reformat' function

# Cut clang-format error message function
# ARGUMENTS:
#   - error message string:
#       stderr;
# RETURNS:
#   cut error message string.
#
def cut_error_msg(stderr):
    lines = stderr.splitlines()

    formated_errs = []

    for line in lines:
        regex = r'^.*\:(\d+)\:(\d+).*?code should be clang-formatted.*$'
        match = re.match(regex, line)

        if match:
            line = match.group(1)
            column = match.group(2)
            formated_errs.append(f"Error! Wrong style format at line {line}, column {column}:")
        else:
            formated_errs.append(line)

    return "\n".join(formated_errs)
# End of 'cut_error_msg' funtion

# Check source code style with clang-format function
# ARGUMENTS:
#   - source code file path:
#       file_path;
# RETURNS:
#   (bool, string) success and error message.
#
def check_clang(file_path):
    try:
        result = subprocess.run(
            [r"C:\Program Files\LLVM\bin\clang-format", "--dry-run", "--Werror", file_path],
            capture_output=True,
            text=True,
            check=False,
            shell=True
        )
        if result.returncode != 0:
            return False, cut_error_msg(result.stderr) # "\n".join(result.stderr.splitlines()[-2:])
        return True, "No style errors found."
    except FileNotFoundError:
        return False, "Error: clang-format not found. Make sure it is installed and in PATH."
# End of 'check_clang' function

