import pandas as pd
"""
df1 = pd.read_csv('analysiscode_result.csv', usecols=['slug', 'runtime_percentile_analysis', 'result_analysis'])


df2 = pd.read_csv('mergedresult1_fixwithoutanalysis_file.csv')
merged_df=pd.merge(df1, df2, left_on='slug', right_on='slug', how='right')

merged_df.to_csv('fix_data_withanalysis.csv', index=False)
print(merged_df.head())
"""
"""
df1 = pd.read_csv('fixresultanalysis.csv')

df2 = pd.read_csv('leetcode_with_details.csv', usecols=['slug', 'difficulty'])
merged_df=pd.merge(df1, df2, left_on='slug', right_on='slug', how='left')
merged_df.to_csv('fixresultanalysis.csv', index=False)
print(merged_df.head())
merged_df.to_csv('fix_result_withanalysis.csv', index=False)
print(merged_df.head())
"""

df1 = pd.read_csv('fix_result_withanalysis.csv')
accept_ratio = (df1['result_analysis'] == 'Accepted').mean()
print(f"'Accepted' proportion: {accept_ratio:.2%}")
accept_ratio_nomod = (df1['memory_percentile'] == 'Accepted').mean()
print(f"'Accepted' proportion no modify: {accept_ratio_nomod:.2%}")
perfect_ration = ((df1['runtime_percentile_analysis'] == '100') | (df1['runtime_percentile_analysis'] == 100)).mean()
print(f"'perfect_code' proportion: {perfect_ration:.2%}")
perfect_ration_nomod = ((df1['runtime_percentile'] == '100') | (df1['runtime_percentile'] == 100)).mean()
print(f"'perfect_code no modify' proportion: {perfect_ration_nomod:.2%}")
ave = ((df1['runtime_percentile_analysis'])).mean()
print("Average runtime: ", ave)
ave_nomod = ((df1['runtime_percentile'])).mean()
print("Average runtime no modify: ", ave_nomod)
accept_by_difficulty = df1[df1['result_analysis'] == 'Accepted'].groupby('difficulty_x').size() / df1.groupby(
'difficulty_x').size()
print("\n'Accepted' proportion by difficulty:")
print(accept_by_difficulty.apply(lambda x: f"{x:.2%}"))

perfect_by_difficulty = (df1['runtime_percentile_analysis'] == 100).groupby(df1['difficulty_x']).mean()
print("\n'perfect_code' proportion by difficulty after fixed:")
print(perfect_by_difficulty.apply(lambda x: f"{x:.2%}"))

group_avg = df1.groupby("difficulty_x")["runtime_percentile_analysis"].mean()
print("average time complexity by difficulty:")
print(group_avg)


print("Here is the data of compare")
df1 = pd.read_csv('fix_data_withanalysis.csv')
df2 = df1[df1['Accepted'] == 'Accepted']
df3 = df1[df1['result_analysis'] == 'Accepted']
df4 = df1[df1['memory_percentile_fixed'] == 'Accepted']

accept_ratio = (df1['result_analysis'] == 'Accepted').mean()
print(f"'Accepted' proportion: {accept_ratio:.2%}")
accept_ratio_nomod = (df1['memory_percentile_fixed'] == 'Accepted').mean()
print(f"'Accepted' proportion without analysis: {accept_ratio_nomod:.2%}")
accept_ratio_nomod = (df1['Accepted'] == 'Accepted').mean()
print(f"'Accepted' initial data proportion: {accept_ratio_nomod:.2%}")
ave = ((df3['runtime_percentile_analysis'])).mean()
print("Average runtime: ", ave)
ave_nomod = ((df4['runtime_percentile_fixed'])).mean()
print("Average runtime without modify: ", ave_nomod)
ave_no = ((df2['runtime_percentile'])).mean()
print("Average runtime initial data: ", ave_no)



perfect_ration = ((df1['runtime_percentile_analysis'] == '100') | (df1['runtime_percentile_analysis'] == 100)).mean()
print(f"'perfect_code' proportion: {perfect_ration:.2%}")

perfect_ration = ((df1['runtime_percentile_fixed'] == '100') | (df1['runtime_percentile_fixed'] == 100)).mean()
print(f"'perfect_code' proportion without analyze: {perfect_ration:.2%}")
