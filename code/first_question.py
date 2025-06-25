import csv
import os
import time
from openai import OpenAI

input_csv = "output_data.csv"
output_csv = "first_try.csv"
target_columns = ["title", "content", "python_code"]
keep_columns = ["slug", "title"]


def validate_generated_code(code, expected_function_name):
    """验证生成的代码是否包含预期的方法名和类"""
    required = [
        f"def {expected_function_name}(",
        "class Solution:"
    ]
    return all(req in code for req in required)


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


def extract_function_name(code):
    """从现有代码中提取函数名"""
    if not code or not isinstance(code, str):
        return None
    lines = code.split('\n')
    for line in lines:
        if line.strip().startswith('def '):
            return line.split('def ')[1].split('(')[0].strip()
    return None


def process_problems(input_filename, output_filename, target_cols, keep_cols):
    client = OpenAI(
        api_key="sk-4f266e93e20c436d8b86e235ffb96065",
        base_url="https://api.deepseek.com"
    )

    init_output_file(output_filename, keep_cols)

    with open(input_filename, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        for i, row in enumerate(reader, 1):
            slug = row["slug"]
            if is_processed(output_filename, slug):
                print(f"Skipping processed: {row['title']}")
                continue

            # 获取问题和原始代码
            problem_content = row.get("content", "")
            original_code = row.get("python_code", "")
            function_name = extract_function_name(original_code) or "solution"  # 默认值

            prompt = f"""
            # LeetCode 题目: {row['title']}
            # 题目描述:
            {problem_content}

            # 原始代码 (必须保持函数名和参数不变):
            {original_code}

            # 任务:
            基于题目描述改进原始代码，但必须:
            1. 保持类名 'Solution' 不变
            2. 保持函数名 '{function_name}' 不变
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
                    if not validate_generated_code(clean_code, function_name):
                        error_msg = f"生成的代码不包含预期函数名 '{function_name}'或类名不正确"
                        raise ValueError(error_msg)

                    status = "Y"
                    print(f"✅ Processed {i}: {row['title']}")
                    break

                except Exception as e:
                    error_msg = str(e)
                    if attempt == max_retries - 1:
                        print(f"❌ Failed after {max_retries} attempts on {row['title']}: {error_msg}")
                    else:
                        print(f"⚠️ Attempt {attempt + 1} failed, retrying...")
                        time.sleep(retry_delay * (attempt + 1))

            with open(output_filename, 'a', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=keep_cols + ["generated_code", "status", "error"])
                writer.writerow({
                    "slug": slug,
                    "title": row["title"],
                    "generated_code": clean_code,
                    "status": status,
                    "error": error_msg if status == "E" else ""
                })

"""

process_problems(input_csv, output_csv, target_columns, keep_columns)
print("\nProcessing complete!")

"""
