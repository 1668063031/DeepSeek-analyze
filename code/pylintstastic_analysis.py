import csv
import tempfile
import os
import re
from pathlib import Path
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze


def clean_python_code(raw_code):
    code = re.sub(r'^```(python)?|```$', '', raw_code, flags=re.IGNORECASE | re.MULTILINE)
    code = '\n'.join(line for line in code.splitlines() if line.strip())
    if any(t in code for t in ["List[", "Dict[", "Optional[", "Tuple[", "Set["]):
        code = "from typing import *\n" + code
    return code.strip()


def randonanalyze(code_string):
    try:
        cleaned_code = clean_python_code(code_string)
        if not cleaned_code:
            return "Error: Empty code after cleaning"

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as tmp:
            tmp.write(cleaned_code)
            tmp_path = tmp.name

        try:
            with open(tmp_path, 'r', encoding='utf-8') as f:
                cc_results = cc_visit(f.read())

            mi_score = mi_visit(cleaned_code, multi=True)

            raw_metrics = analyze(cleaned_code)

            result = {
                'cyclomatic_complexity': [{
                    'name': func.name,
                    'complexity': func.complexity,
                    'lineno': func.lineno
                } for func in cc_results],
                'maintainability_index': mi_score,
                'raw_metrics': {
                    'loc': raw_metrics.loc,
                    'lloc': raw_metrics.lloc,
                    'sloc': raw_metrics.sloc,
                    'comments': raw_metrics.comments,
                }
            }
            return str(result)

        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass

    except SyntaxError as e:
        return f"SyntaxError: {str(e)}"
    except Exception as e:
        return f"Analysis Error: {str(e)}"


def analyzecsv(csv_path, column_index=9, output_csv='radon_results.csv'):
    output_file = Path(output_csv)
    if not output_file.exists():
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['slug', 'code', 'radon'])

    processed_ids = set()
    if output_file.exists():
        with open(output_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            processed_ids = {row[0] for row in reader if row}

    # 增量处理新行
    with open(csv_path, 'r', encoding='utf-8') as input_file:
        reader = csv.reader(input_file)
        headers = next(reader)

        for row in reader:
            if not row:
                continue

            original_id = row[0]
            if original_id in processed_ids or len(row) <= column_index:
                continue

            raw_code = row[column_index]
            radon_results = randonanalyze(raw_code)

            # 追加写入结果
            with open(output_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([original_id, raw_code, radon_results])

            print(f"Processed ID: {original_id} - Result: {radon_results[:50]}...")

    print(f"Radon analysis completed. Results in {output_csv}")


if __name__ == "__main__":
    analyzecsv('unperfect.csv', column_index=9)