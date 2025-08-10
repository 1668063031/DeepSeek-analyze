import json
import csv
import re
import pandas as pd

"""

with open('gptpython.json', 'r') as f:
    data = json.load(f)

with open('gptpython.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['name', 'is_pass']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for item in data:
        original_name = item['name']
        clean_name = re.sub(r'^\d+-', '', original_name)

        row = {
            'name': clean_name,
            'is_pass': item['is_pass']
        }
        writer.writerow(row)
"""
"""
df1 = pd.read_csv('first_result.csv')


df2 = pd.read_csv('gptpython.csv')
merged_df=pd.merge(df1, df2, left_on='slug', right_on='slug', how='inner')

merged_df.to_csv('gptdeepseek.csv', index=False)

df1 = pd.read_csv('gptdeepseek.csv')

df2 = pd.read_csv('leetcode_with_details.csv',usecols=['slug', 'difficulty'])
merged_df=pd.merge(df1, df2, left_on='slug', right_on='slug', how='left')

merged_df.to_csv('gptdeepseek.csv', index=False)

"""

df1=pd.read_csv('gptdeepseek.csv')

accept1 = (df1['memory_percentile'] == 'Accepted').sum()
print(accept1)
accept_percent1 = accept1 / len(df1)
print(f"'Accepted' proportion of DeepSeek: {accept_percent1:.2%}")

accept2 = (df1['is_pass'] == 1).sum()
print(accept2)
accept_percent2 = accept2 / len(df1)
print(f"'Accepted' proportion of GPT3.5: {accept_percent2:.2%}")

accept_by_difficulty = df1[df1['memory_percentile'] == 'Accepted'].groupby('difficulty').size() / df1.groupby(
        'difficulty').size()
print("\n'Accepted' proportion by difficulty for DeepSeek:")
print(accept_by_difficulty.apply(lambda x: f"{x:.2%}"))

accept_by_difficulty = df1[df1['is_pass'] == 1].groupby('difficulty').size() / df1.groupby(
        'difficulty').size()
print("\n Accepted' proportion by difficulty for GPT 3.5:")
print(accept_by_difficulty.apply(lambda x: f"{x:.2%}"))

common_accept = ((df1['memory_percentile'] == 'Accepted') & (df1['is_pass'] == 1)).sum()
print("\n Deepseek and GPT 3.5 solution both accepted:", common_accept)

