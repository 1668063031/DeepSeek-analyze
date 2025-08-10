import csv
import tempfile
import os
import re
import subprocess
from pathlib import Path

PYLINT_DISABLE = [
    # document
    'missing-module-docstring',
    'missing-class-docstring',
    'missing-function-docstring',

    # naming notations
    'invalid-name',  # C0103
    'disallowed-name',  # C0104

    # structure
    'too-few-public-methods',  # R0903
    'too-many-arguments',  # R0913
    'too-many-locals',  # R0914
    'too-many-branches',  # R0912
    'too-many-nested-blocks',  # R1702
    'too-many-statements',  # R0915
    'too-many-instance-attributes',  # R0902

    # format
    'trailing-whitespace',  # C0303
    'missing-final-newline',  # C0304
    'bad-whitespace',  # C0326
    'unnecessary-semicolon',  # W0301

    # format check
    'undefined-variable',  # E0602
    'no-member',  # E1101
    'unused-argument',  # W0613
    'unused-variable',  # W0612

    # others
    'consider-using-enumerate',  # R1721
    'consider-using-dict-items',  # R1737
    'use-a-generator',  # R1736
]


def clean_python_code(raw_code):
    if "List[" in raw_code or "Dict[" in raw_code or "Optional[" in raw_code:
        raw_code = "from typing import *\n" + raw_code
    code = re.sub(r'^```python|^```', '', raw_code, flags=re.IGNORECASE)
    code = re.sub(r'```$', '', code)
    return code.strip()


def analyze_python_code(code_string):
    cleaned_code = clean_python_code(code_string)
    pylint_directive = "\n".join([f"# pylint: disable={warning}" for warning in PYLINT_DISABLE])

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as tmp:
        tmp.write(f"{pylint_directive}\n{cleaned_code}")
        tmp_path = tmp.name

    result = subprocess.run(
        ['pylint', tmp_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    os.unlink(tmp_path)
    return result.stdout


def analyze_csv_column(csv_path, column_index=9, output_csv='pylint_compare.csv'):

    output_file = Path(output_csv)
    if not output_file.exists():
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['slug', 'Original Code', 'Pylint Results'])

    processed_ids = set()
    if output_file.exists():
        with open(output_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            processed_ids = {row[0] for row in reader if row}

    with open(csv_path, 'r', encoding='utf-8') as input_file:
        reader = csv.reader(input_file)
        headers = next(reader)

        for row in reader:
            if not row:
                continue

            slug = row[0]
            if slug in processed_ids or len(row) <= column_index:
                continue

            raw_code = row[column_index]
            pylint_results = analyze_python_code(raw_code)

            with open(output_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([slug, raw_code, pylint_results])

            print(f"Processed ID: {slug}")

    print(f"Analysis completed. Results in {output_csv}")

analyze_csv_column('unperfect.csv', column_index=9)