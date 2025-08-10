import requests
import json
import csv

def catch_problems():
    url = "https://leetcode.com/api/problems/all/"
    response = requests.get(url)
    data = response.json()
    return [
        {
            "id": item["stat"]["question_id"],
            "title": item["stat"]["question__title"],
            "slug": item["stat"]["question__title_slug"],
            "difficulty": ["Easy", "Medium", "Hard"][item["difficulty"]["level"] - 1],
            "paid_only": item["paid_only"]
        }
        for item in data["stat_status_pairs"]
    ]

all_problems = fetch_all_problems()
easy_problems = [p for p in all_problems if p["difficulty"] == "Easy" and not p["paid_only"]][:400]
med_problems = [p for p in all_problems if p["difficulty"] == "Medium" and not p["paid_only"]][:400]
hard_problems = [p for p in all_problems if p["difficulty"] == "Hard" and not p["paid_only"]][:400]

with open("leetcode_easy_1600.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["id", "title", "slug", "difficulty", "paid_only"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(easy_problems)
    writer.writerows(med_problems)
    writer.writerows(hard_problems)

print(f"saved {len(easy_problems)} question to database.csv")


