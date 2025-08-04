"""
# this is a funtion to unit excel and find difficulty.
import pandas as pd

df1 = pd.read_csv('first_result.csv')
df2 = pd.read_csv('output_data.csv')



column_to_move = 'difficulty'
df2_subset = df2[['slug', column_to_move]]
merged_df=pd.merge(df2_subset, df1, left_on='slug', right_on='slug', how='left')

merged_df.to_csv('merged_file.csv', index=False)
print(merged_df.head())
"""
import math

import pandas as pd
import numpy as np

df1 = pd.read_csv('merged_file.csv')

accept = (df1['Accepted'] == 'Accepted').sum()
print(accept)
accept_percent = accept / len(df1)
print(f"'Accepted' proportion: {accept_percent:.2%}")

perfect_ration = ((df1['runtime_percentile'] == 100).sum() / len(df1))
print(f"'perfect_code' proportion: {perfect_ration:.2%}")

print("\nProportions by difficulty:")

accept_by_difficulty = df1[df1['Accepted'] == 'Accepted'].groupby('difficulty').size() / df1.groupby(
        'difficulty').size()
print("\n'Accepted' proportion by difficulty:")
print(accept_by_difficulty.apply(lambda x: f"{x:.2%}"))

# Perfect code proportion by difficulty
perfect_by_difficulty = (df1['runtime_percentile'] == 100).groupby(df1['difficulty']).mean()
print("\n'perfect_code' proportion by difficulty:")
print(perfect_by_difficulty.apply(lambda x: f"{x:.2%}"))

df1 = pd.read_csv('merged_file.csv', dtype={'runtime_percentile': float})
averesult = df1['runtime_percentile'].astype(float).mean()
easyaversult = (df1[df1['Accepted'] == 'Accepted']['runtime_percentile'].astype(float)
          .groupby(df1['difficulty'])
          .sum()
)
accepted_counts = df1[df1['Accepted'] == 'Accepted'].groupby('difficulty')['Accepted'].count()
easyaversult=easyaversult/accepted_counts
print(averesult)
print("\n'average_complexity' proportion by difficulty:")
print(easyaversult)

"""
import pandas as pd

df1 = pd.read_csv('noanalysis_fixresult.csv')
df2 = pd.read_csv('merged_file.csv')



df2_subset = df2[['slug', 'difficulty', 'runtime_percentile', 'status_msg', 'Accepted' ]]
merged_df=pd.merge(df1, df2_subset, left_on='slug', right_on='slug', how='left')

merged_df.to_csv('mergedresult1_file.csv', index=False)
print(merged_df.head())
"""

print('here is the data of fix with out analysis')

# In this files, memory_percentile_fixed is sames as Accepted in df1

df3 = pd.read_csv('mergedresult1_fixwithoutanalysis_file.csv')

accept_ratio = (df3['memory_percentile_fixed'] == 'Accepted').mean()
print(f"'Accepted' proportion: {accept_ratio:.2%}")

accept_ratio_NO = (df3['Accepted'] == 'Accepted').mean()
print(f"'Accepted' proportion without modify: {accept_ratio_NO:.2%}")

perfect_ration = ((df3['runtime_percentile_fixed'] == '100') | (df3['runtime_percentile_fixed'] == 100)).mean()
print(f"'perfect_code' proportion: {perfect_ration:.2%}")

perfect_ration = ((df3['runtime_percentile'] == '100') | (df3['runtime_percentile'] == 100)).mean()
print(f"'perfect_code' proportion before: {perfect_ration:.2%}")


print("\nProportions by difficulty:")


accept_by_difficulty = df3[df3['memory_percentile_fixed'] == 'Accepted'].groupby('difficulty').size() / df3.groupby(
'difficulty').size()
print("\n'Accepted' proportion by difficulty:")
print(accept_by_difficulty.apply(lambda x: f"{x:.2%}"))

perfect_by_difficulty = (df3['runtime_percentile_fixed'] == 100).groupby(df3['difficulty']).mean()
print("\n'perfect_code' proportion by difficulty after fixed:")
print(perfect_by_difficulty.apply(lambda x: f"{x:.2%}"))

non_accepted_total = (df3['Accepted'] != 'Accepted').sum()

special_case = ((df3['Accepted'] != 'Accepted') & (df3['memory_percentile_fixed'] == 'Accepted')).sum()

if non_accepted_total > 0:
    ratio = special_case / non_accepted_total
else:
    ratio = 0

print(f"Proportion where 'memory_percentile_fixed' is 'Accepted' among non-'Accepted' rows: {ratio:.2%}")

bug_case = ((df3['memory_percentile_fixed'] != 'Accepted') & (df3['Accepted'] == 'Accepted')).sum()
accepted_total = (df3['Accepted'] == 'Accepted').sum()
if accepted_total > 0:
    ratio = bug_case / accepted_total
else:
    ratio = 0
print(f"Proportion where 'memory_percentile_fixed' is 'Accepted' among non-'Accepted' rows: {ratio:.2%}")

fixed= ((df3['memory_percentile_fixed'] == 'Accepted') & (df3['Accepted'] != 'Accepted')).sum()
allwrong=(df3['Accepted'] != 'Accepted').sum()
rate=fixed/allwrong
print("fix the wrong solution:",rate)

averesult = ((df3['runtime_percentile_fixed']) ).mean()
ave = ((df3['runtime_percentile'])).mean()

perfect_by_difficulty = (df3['runtime_percentile_fixed'] == 100).groupby(df3['difficulty']).mean()
print("\n'perfect_code' proportion by difficulty:")
print(perfect_by_difficulty.apply(lambda x: f"{x:.2%}"))
group_avg = df3.groupby("difficulty")["runtime_percentile_fixed"].mean()
print("average time complexity by difficulty:")
print(group_avg)



print("average:", ave, averesult)