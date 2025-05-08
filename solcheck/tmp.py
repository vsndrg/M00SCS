import subprocess

try:
    result = subprocess.run(
        ['clang-format', '--dry-run', '--Werror', '../out/uploads/h00fst_reformat.c'],
        capture_output=True,
        text=True,
        check=False,
        shell=False
    )
    if result.returncode != 0:
        print('\n'.join(result.stderr.splitlines()[-2:]))
    else:
        print('No style errors found.')
except FileNotFoundError:
    print('Error: clang-format not found. Make sure it is installed and in PATH.')
