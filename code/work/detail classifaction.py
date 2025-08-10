import csv
import json
from bs4 import BeautifulSoup
import chardet
from collections import defaultdict

input_csv = "leetcode_with_details.csv"
output_csv = "output_data.csv"


def detect_file_encoding(file_path):
    with open(file_path, 'rb') as f:
        return chardet.detect(f.read())['encoding']


def extract_content_and_code(row, row_num):
    try:
        data = json.loads(row["details"])

        if not data.get("data", {}).get("question"):
            return None, None, None

        question = data["data"]["question"]
        difficulty = question.get("difficulty", "UNKNOWN")

        content = question.get("content", "")
        clean_content = BeautifulSoup(content, "html.parser").get_text()

        code_snippets = question.get("codeSnippets", [])
        python_code = next((snippet["code"] for snippet in code_snippets
                          if snippet["lang"] == "Python3"), "")

        return clean_content, python_code, difficulty
    except Exception as e:
        print(f" {row_num} error: {str(e)}")
        return None, None, None


stats = {
    'total_processed': 0,
    'skipped_no_code': defaultdict(int),
    'saved_records': 0
}

try:
    encoding = detect_file_encoding(input_csv)
except:
    encoding = 'utf-8'

valid_rows = []
with open(input_csv, mode='r', encoding=encoding) as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ["content", "python_code"]

    for i, row in enumerate(reader, 1):
        stats['total_processed'] += 1
        content, code, difficulty = extract_content_and_code(row, i)
        if not code:
            if difficulty:
                stats['skipped_no_code'][difficulty] += 1
            continue

        new_row = row.copy()
        new_row["content"] = content if content is not None else ""
        new_row["python_code"] = code
        valid_rows.append(new_row)
        stats['saved_records'] += 1

if valid_rows:
    with open(output_csv, mode='w', encoding='utf-8-sig', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(valid_rows)


print(f"\n the result have already been saved to {output_csv}")