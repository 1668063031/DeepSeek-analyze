import requests
import time
import textwrap
import os
import csv
import time
import random

LEETCODE_SESSION = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMTczNTQyNTIiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJhbGxhdXRoLmFjY291bnQuYXV0aF9iYWNrZW5kcy5BdXRoZW50aWNhdGlvbkJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI3MWIwYzZlMGEyMTY0NjU2MzQwMTM2MTQ4OGE0NzM3MWNjZjAzYjhlYzA0YjEyMzNhYTdlNDAyMWZmYjU1ODhiIiwic2Vzc2lvbl91dWlkIjoiZGY2YTY2OTkiLCJpZCI6MTczNTQyNTIsImVtYWlsIjoiY2hlbnpoZW5neWFuZ2p3cDEyM0BnbWFpbC5jb20iLCJ1c2VybmFtZSI6IkxraEhQd2E5eWEiLCJ1c2VyX3NsdWciOiJMa2hIUHdhOXlhIiwiYXZhdGFyIjoiaHR0cHM6Ly9hc3NldHMubGVldGNvZGUuY29tL3VzZXJzL0xraEhQd2E5eWEvYXZhdGFyXzE3NDQzMjUxNDgucG5nIiwicmVmcmVzaGVkX2F0IjoxNzQ4OTYxNTYwLCJpcCI6IjEzMC4yMjYuMTYxLjkyIiwiaWRlbnRpdHkiOiIwZmU2ZmViNTQyODlmNGM2NzAyN2VjMDZjYzIxMzFmOCIsImRldmljZV93aXRoX2lwIjpbImE0ZjAyNTk0YTEzYjM5N2Q1YmQzZDA4NzYzNjNjMzc2IiwiMTMwLjIyNi4xNjEuOTIiXX0.jT5P5sdBbBxBuz_qyd4aWZPR08eZ6lmslG02EKQ29i0"
CSRF_TOKEN = "PChv6dqxWbIqTBoQxJVyRyvtXUBchklgDjENGsoBwxrSwruxHmwZ47hrt75Efa3a"

# set the header
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": f"https://leetcode.com/problems/",
    "Origin": "https://leetcode.com",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json",
    "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}",
    "x-csrftoken": CSRF_TOKEN,
}


def extract_pure_code(code_str):

    lines = code_str.split('\n')

    pure_lines = []
    code_block_started = False

    for line in lines:
        stripped = line.strip()
        if stripped in ['```python', '```']:
            continue
        if not stripped or stripped.startswith('#'):
            continue
        pure_lines.append(line)

    pure_code = '\n'.join(pure_lines)
    return pure_code

response = requests.get("https://leetcode.com/api/problems/all/", headers=headers)

if response.status_code == 200:
    print("✅ Cookies is valid")
    print("return data:", response.json()["num_total"])
else:
    print("❌ log in fail！HTTP status code:", response.status_code)


def get_question_id(title_slug, headers):

    query = """
    query getQuestionDetail($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionId
        }
    }
    """
    response = requests.post(
        "https://leetcode.com/graphql",
        headers=headers,
        json={"query": query, "variables": {"titleSlug": title_slug}},
    )
    return response.json()["data"]["question"]["questionId"]

def poll_submission_result(submission_id, headers, max_retries=10):

    for _ in range(max_retries):
        response = requests.get(
            f"https://leetcode.com/submissions/detail/{submission_id}/check/",
            headers=headers,
        )
        result = response.json()
        if result.get("state") == "SUCCESS":
            return result
        time.sleep(5)
    return {"error": "time limit out"}

def is_processed(output_filename, slug):

    if not os.path.exists(output_filename):
        return False

    with open(output_filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return any(row["slug"] == slug and row["processed"] == "True" for row in reader)


def test_leetcode_submission(title_slug, lang, code, leetcode_session, csrf_token=None):
    headers["Cookie"] += f"; csrftoken={csrf_token}"
    """
    Test LeetCode code submission  
    :param title_slug: Problem URL identifier (e.g., "two-sum")  
    :param lang: Language (e.g., "python3")  
    :param code: Code to submit (string)  
    :param leetcode_session: LEETCODE_SESSION value  
    :param csrf_token: Optional, must be provided if required by the API  
    :return: Submission result (dictionary)  
    """

    if csrf_token:
        headers["Cookie"] += f"; csrftoken={csrf_token}"
        headers["x-csrftoken"] = csrf_token


    question_id = get_question_id(title_slug, headers)


    submit_url = f"https://leetcode.com/problems/{title_slug}/submit/"
    data = {
        "lang": lang,
        "question_id": question_id,
        "typed_code": code,
    }
    response = requests.post(submit_url, headers=headers, json=data)
    time.sleep(20 + random.random() * 3)


    if response.status_code == 200:
        submission_id = response.json().get("submission_id")
        return poll_submission_result(submission_id, headers)
    else:
        return {"error": f"submit fail，status code: {response.status_code}", "response": response.text}


def process_problems(input_filename, output_filename, target_cols, keep_cols):
    init_output_file(output_filename, keep_cols)

    processed_slugs = set()
    if os.path.exists(output_filename):
        with open(output_filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            processed_slugs = {row['slug'] for row in reader if str(row.get('processed', '')).lower() in ['true', 'y']}

    with open(input_filename, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            slug = row["slug"]

            if slug in processed_slugs:
                print(f"skip processed question: {slug}")
                continue

            code = extract_pure_code(row["generated_code"])
            print(f"handle: {slug}")

            result = test_leetcode_submission(
                slug,
                "python3",
                code,
                leetcode_session=LEETCODE_SESSION,
                csrf_token=CSRF_TOKEN
            )

            print(result)

            output_data = {
                "slug": slug,
                "total_testcases": result.get("total_testcases", ""),
                "total_correct": result.get("total_correct", ""),
                "runtime_percentile": result.get("runtime_percentile", ""),
                "state": result.get("state", ""),
                "memory_percentile": result.get("memory_percentile", ""),
                "status_msg": result.get("status_msg", result.get("error", "")),
                "processed": "True"
            }

            with open(output_filename, 'a', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=keep_cols + [
                    "total_testcases",
                    "total_correct",
                    "runtime_percentile",
                    "state",
                    "memory_percentile",
                    "status_msg",
                    "processed"
                ])
                writer.writerow(output_data)

            print(f"已保存结果: {slug} - {output_data['status_msg']}")
            time.sleep(10)

def init_output_file(output_filename, keep_cols):
    """Initialize output file if not exists"""
    if not os.path.exists(output_filename):
        with open(output_filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keep_cols + ["total_testcases", "total_correct", "runtime_percentile", "state","status_msg", "memory_percentile", "processed"])
            writer.writeheader()

input_csv = "first_try.csv"
target_columns = ["slug", "generated_code"]
output_csv = "first_result.csv"
keep_columns = ["slug"]

process_problems(input_csv, output_csv, target_columns, keep_columns)