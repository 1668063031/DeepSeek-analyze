import requests
import time
import textwrap
import os
import csv
import time
import math
from openai import OpenAI

import pandas as pd

"""
df1 = pd.read_csv('unperfect.csv')

df2 = pd.read_csv('output_data.csv', usecols=['slug', 'content'])
merged_df=pd.merge(df1, df2, left_on='slug', right_on='slug', how='left')

merged_df.to_csv('fix_data.csv', index=False)
print(merged_df.head())
"""
input_csv = "fix_data.csv"
output_csv = "noanalysis_result.csv"
target_columns = ["slug", "status_msg", "generated_code", "content"]
keep_columns = ["slug", "content"]


def get_file_encoding(file_path):
    import chardet
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # 检测前1万字节
    return result['encoding'] or 'utf-8'


def init_output_file(output_filename, keep_cols):
    """Initialize output file if not exists"""
    if not os.path.exists(output_filename):
        with open(output_filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keep_cols + ["generated_code", "status", "error"])
            writer.writeheader()


def is_processed(output_filename, slug):
    """Check if record already processed"""
    if not os.path.exists(output_filename):
        return False
    with open(output_filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return any(row["slug"] == slug and row["status"] in ["Y", "E"] for row in reader)




def process_problems(input_filename, output_filename, target_cols, keep_cols):
    client = OpenAI(
        api_key="sk-4f266e93e20c436d8b86e235ffb96065",
        base_url="https://api.deepseek.com"
    )

    init_output_file(output_filename, keep_cols)

    with open(input_filename, 'r', encoding='utf-8', errors='replace') as infile:
        reader = csv.DictReader(infile)

        for i, row in enumerate(reader, 1):
            slug = row["slug"]
            if is_processed(output_filename, slug):
                print(f"Skipping processed: {row['slug']}")
                continue

            # 获取问题和原始代码
            problem_content = row.get("content", "")
            original_code = row.get("generated_code", "")
            problem = row.get("status_msg", "")

            if problem == 'Accepted':

               prompt = f"""Please optimize the time complexity of the following Python code. The current code is completely correct and do not need to be modified, but the computational time complexity needs to be reduced. Strictly maintain the original function/class names and parameter signatures. Return only the final code without any explanations.
               # LeetCode 题目: {row['slug']}
               # 题目描述:
               {problem_content}

               # 原始代码 (必须保持函数名和参数不变):
               {original_code}

               # 任务:
               基于题目描述改进原始代码，但必须:
               1. 保持类名 'Solution' 不变
               2. 保持函数名不变
               3. 保持完全相同的参数签名
               4. 只改进代码实现部分
               5. 返回完整的可执行Python代码，不要任何解释

               # 注意:
               - 不要添加额外的方法或函数
               - 不要改变输入输出类型
               - 不要添加示例或测试用例
               """
            elif problem == 'Wrong Answer':
                prompt = f"""The code didn't passed, please modified it to make it passed. Strictly maintain the original function/class names and parameter signatures. Return only the final code without any explanations.
                # LeetCode 题目: {row['slug']}
                # 题目描述:
                {problem_content}

                # 原始代码 (必须保持函数名和参数不变):
                {original_code}

                # 任务:
                基于题目描述改进原始代码，但必须:
                1. 保持类名 'Solution' 不变
                2. 保持函数名不变
                3. 保持完全相同的参数签名
                4. 只改进代码实现部分
                5. 返回完整的可执行Python代码，不要任何解释

                # 注意:
                - 不要添加额外的方法或函数
                - 不要改变输入输出类型
                - 不要添加示例或测试用例
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

                    # 验证生成的代码
                    if not validate_generated_code(clean_code):
                        error_msg = f"生成的代码不包含预期函数名或类名不正确"
                        raise ValueError(error_msg)

                    status = "Y"
                    print(f"✅ Processed {i}: {row['slug']}")
                    break

                except Exception as e:
                    error_msg = str(e)
                    if attempt == max_retries - 1:
                        print(f"❌ Failed after {max_retries} attempts on {row['slug']}: {error_msg}")
                    else:
                        print(f"⚠️ Attempt {attempt + 1} failed, retrying...")
                        time.sleep(retry_delay * (attempt + 1))

            with open(output_filename, 'a', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=keep_cols + ["generated_code", "status", "error"])
                writer.writerow({
                    "slug": slug,
                    "content": row["content"],
                    "generated_code": clean_code,
                    "status": status,
                    "error": error_msg if status == "E" else ""
                })



process_problems(input_csv, output_csv, target_columns, keep_columns)
print("\nProcessing complete!")

