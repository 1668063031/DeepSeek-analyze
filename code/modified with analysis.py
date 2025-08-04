import requests
import time
import textwrap
import os
import csv
import time
import math
from openai import OpenAI

import pandas as pd


input_csv = "fix_data_analysis.csv"
print(input_csv)
output_csv = "analysis_result.csv"
target_columns = ["slug", "status_msg", "code", "content", "radon", "Pylint_Results"]
keep_columns = ["slug", "content"]



def init_output_file(output_filename, keep_cols):
    if not os.path.exists(output_filename):
        with open(output_filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keep_cols + ["generated_code", "status", "error"])
            writer.writeheader()


def is_processed(output_filename, slug):
    if not os.path.exists(output_filename):
        return False
    with open(output_filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return any(row["slug"] == slug and row["status"] in ["Y", "E"] for row in reader)

def extract_function_name(code):
    if not code or not isinstance(code, str):
        return None
    lines = code.split('\n')
    for line in lines:
        if line.strip().startswith('def '):
            return line.split('def ')[1].split('(')[0].strip()
    return None


def process_problems(input_filename, output_filename, target_cols, keep_cols):
    client = OpenAI(
        api_key="......",
        base_url="https://api.deepseek.com"
    )

    init_output_file(output_filename, keep_cols)

    df = pd.read_csv(input_filename, encoding='utf-8-sig')

    for i, row in df.iterrows():
        slug = row['slug']
        print(slug)
        if is_processed(output_filename, slug):
            print(f"Skipping processed: {row['slug']}")
            continue

        problem_content = row['content']
        original_code = row['code']
        problem = row['status_msg']
        radon = row['radon']
        pylint = row['Pylint_Results']
        function_name = extract_function_name(original_code) or "solution"  # 默认值

        if problem == 'Accepted':

            prompt = f"""Please optimize the time complexity of the following Python code. The current code is completely correct and do not need to be modified, but the computational time complexity needs to be reduced. Strictly maintain the original function/class names and parameter signatures. Return only the final code without any explanations. Radon and Pylint give some suggestions, consider about those advices.
               # LeetCode question: {slug}
               # Description and examples:
               {problem_content}

               # original code:
               {original_code}

                # radon_suggestion:
               {radon}

                # pylint_suggestion:
               {pylint}


               # mission:
               Based on the problem description, improve the original code while strictly adhering to the following requirements:
               1. Keep the class name unchanged
               2. Keep the function name unchanged
               3. Maintain exactly the same parameter signatures
               4. Only modify the code implementation (don't change structure)
               5. Return complete executable Python code without any explanations

               # mission:
               Do not add extra methods or functions
               Do not modify the input/output types 
               # Do not include examples or test cases
               """

        else:
            prompt = f"""The code didn't passed, please modified it to make it passed. Strictly maintain the original function/class names and parameter signatures. Return only the final code without any explanations. Radon and Pylint give some suggestions, consider about those advices.
                # LeetCode question: {row['slug']}
                # Description and examples:
                {problem_content}

                # original code:
                {original_code}

                # radon_suggestion:
               {radon}

                # pylint_suggestion:
               {pylint}

               # mission:
               Based on the problem description, improve the original code while strictly adhering to the following requirements:
               1. Keep the class name unchanged
               2. Keep the function name unchanged
               3. Maintain exactly the same parameter signatures
               4. Only modify the code implementation (don't change structure)
               5. Return complete executable Python code without any explanations

               # mission:
               Do not add extra methods or functions
               Do not modify the input/output types 
               # Do not include examples or test cases
               """

        max_retries = 3
        retry_delay = 5
        status = "E"
        clean_code = ""
        error_msg = ""

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional Python code optimization expert. You must strictly maintain the original function names, class names, and parameter signatures, and return only the complete code without any explanations."

                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )

                raw_code = response.choices[0].message.content
                clean_code = '\n'.join([line for line in raw_code.split('\n')
                                        if not line.strip().startswith('#')
                                        and not line.strip().startswith('"""')])




                status = "Y"
                print(f"✅ Processed {i}: {row['slug']}")
                break

            except Exception as e:
                error_msg = str(e)
                if attempt == max_retries - 1:
                    status = "E"
                    print(f"❌ Final attempt failed on {row['slug']}: {error_msg}")
                else:
                    print(f"⚠️ Attempt {attempt + 1} failed, retrying...")
                    time.sleep(retry_delay * (attempt + 1))


        with open(output_filename, 'a', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=keep_cols + ["generated_code", "status", "error"])
            writer.writerow({
                "slug": slug,
                "content": row["content"],
                "generated_code": clean_code,
                "error": error_msg if status == "E" else ""
            })


process_problems(input_csv, output_csv, target_columns, keep_columns)
print("\nProcessing complete!")