import csv
import tempfile
import os
import re
from pathlib import Path
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze

"""
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

"""
"""
import re
import pandas as pd
from collections import Counter

df1 = pd.read_csv('pylint_results.csv')

df2 = pd.read_csv('fix_result_withanalysis.csv')
merged_df=pd.merge(df1, df2, left_on='slug', right_on='slug', how='right')
merged_df.to_csv('pylintresult.csv', index=False)



def count_pylint_errors(csv_file):

    df = pd.read_csv(csv_file)

    error_counter = Counter()

    error_pattern = re.compile(r'([A-Z]\d{4}):')

    for result in df['Pylint_Results']:
        errors = error_pattern.findall(result)
        error_counter.update(errors)

    return error_counter


# 使用示例
error_counts = count_pylint_errors('pylintresult.csv')
print("Mistaken calculate:")
for error_code, count in error_counts.most_common():
    print(f"{error_code}: {count} times")
"""
"""
import pandas as pd
df1 = pd.read_csv('pylintresult.csv')

df2 = pd.read_csv('radon_results.csv', usecols=['slug', 'radon'])
merged_df=pd.merge(df1, df2, left_on='slug', right_on='slug', how='left')
merged_df.to_csv('allfixresult.csv', index=False)
"""
import csv
import ast
from collections import defaultdict


def analyze_metrics(csv_file):
    # 初始化统计字典
    difficulty_stats = defaultdict(lambda: {
        'count': 0,
        'complexity_stats': {
            'total': 0,
            'max': 0,
            'min': float('inf'),
            'values': []
        },
        'maintainability_stats': {
            'total': 0,
            'max': 0,
            'min': float('inf'),
            'values': []
        }
    })

    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                difficulty = row['difficulty_x']

                # 解析radon数据
                try:
                    radon_data = ast.literal_eval(row['radon'])
                except (SyntaxError, ValueError):
                    continue

                # 计算圈复杂度指标
                if 'cyclomatic_complexity' in radon_data:
                    complexities = [item['complexity'] for item in radon_data['cyclomatic_complexity']]
                    max_complexity = max(complexities) if complexities else 0
                    avg_complexity = sum(complexities) / len(complexities) if complexities else 0
                else:
                    max_complexity = 0
                    avg_complexity = 0

                # 获取可维护性指数
                maintainability = radon_data.get('maintainability_index', 0)

                # 更新统计信息
                stats = difficulty_stats[difficulty]
                stats['count'] += 1

                # 更新圈复杂度统计
                stats['complexity_stats']['total'] += avg_complexity
                stats['complexity_stats']['max'] = max(stats['complexity_stats']['max'], max_complexity)
                stats['complexity_stats']['min'] = min(stats['complexity_stats']['min'], max_complexity)
                stats['complexity_stats']['values'].append(max_complexity)

                # 更新可维护性指数统计
                stats['maintainability_stats']['total'] += maintainability
                stats['maintainability_stats']['max'] = max(stats['maintainability_stats']['max'], maintainability)
                stats['maintainability_stats']['min'] = min(stats['maintainability_stats']['min'], maintainability)
                stats['maintainability_stats']['values'].append(maintainability)

            except Exception as e:
                print(f"Error processing row: {e}")
                continue

    # 计算统计指标
    results = []
    for difficulty, stats in difficulty_stats.items():
        if stats['count'] > 0:
            # 圈复杂度统计
            avg_complexity = stats['complexity_stats']['total'] / stats['count']
            median_complexity = sorted(stats['complexity_stats']['values'])[
                len(stats['complexity_stats']['values']) // 2]

            # 可维护性指数统计
            avg_maintainability = stats['maintainability_stats']['total'] / stats['count']
            median_maintainability = sorted(stats['maintainability_stats']['values'])[
                len(stats['maintainability_stats']['values']) // 2]

            results.append({
                'difficulty': difficulty,
                'count': stats['count'],
                'cyclomatic_complexity': {
                    'average': avg_complexity,
                    'max': stats['complexity_stats']['max'],
                    'min': stats['complexity_stats']['min'],
                    'median': median_complexity
                },
                'maintainability_index': {
                    'average': avg_maintainability,
                    'max': stats['maintainability_stats']['max'],
                    'min': stats['maintainability_stats']['min'],
                    'median': median_maintainability
                }
            })

    return sorted(results, key=lambda x: ['Easy', 'Medium', 'Hard'].index(x['difficulty']))


def print_results(results):
    print("\n不同难度下的代码指标统计结果:")
    print("=" * 80)
    for r in results:
        print(f"\n难度级别: {r['difficulty']} (样本数: {r['count']})")
        print("-" * 60)
        print("圈复杂度(Cyclomatic Complexity):")
        print(f"  平均值: {r['cyclomatic_complexity']['average']:.2f}")
        print(f"  最大值: {r['cyclomatic_complexity']['max']}")
        print(f"  最小值: {r['cyclomatic_complexity']['min']}")

        print("\n可维护性指数(Maintainability Index):")
        print(f"  平均值: {r['maintainability_index']['average']:.2f}")
        print(f"  最大值: {r['maintainability_index']['max']:.2f}")
        print(f"  最小值: {r['maintainability_index']['min']:.2f}")
    print("=" * 80)


if __name__ == "__main__":
    csv_file = "allfixresult.csv"  # 替换为你的CSV文件路径
    results = analyze_metrics(csv_file)
    print_results(results)