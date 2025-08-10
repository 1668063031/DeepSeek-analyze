import requests
import json
import csv
from tempfile import NamedTemporaryFile
import shutil


def fetch_question(title_slug: str):

    url = "https://leetcode.com/graphql"
    headers = {"Content-Type": "application/json"}
    query = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        title
        difficulty
        content
        codeSnippets { lang code }
      }
    }
    """
    variables = {"titleSlug": title_slug}
    response = requests.post(
        url,
        json={"query": query, "variables": variables},
        headers=headers
    )
    data = response.json()
    if "data" in data and "question" in data["data"]:
        question_data = data["data"]["question"]
        python_snippets = [
            snippet for snippet in question_data.get("codeSnippets", [])
            if snippet.get("lang") == "Python3" or snippet.get("langSlug") == "python3"
        ]
        question_data["codeSnippets"] = python_snippets
    return data


def catch_detailed():

    input_csv = "leetcode_easy_1600.csv"
    output_csv = "leetcode_with_details.csv"

    with open(input_csv, "r", encoding="utf-8") as infile, \
            open(output_csv, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["details"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            slug = row["slug"]
            print(f"Fetching data for slug: {slug}")
            data = fetch_question(slug)
            row["details"] = json.dumps(data, ensure_ascii=False)
            writer.writerow(row)

    print(f"the data save to {output_csv}")


catch_detailed()