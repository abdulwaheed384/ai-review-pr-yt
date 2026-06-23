# ============================================================
# AI PR REVIEW - VIDEO 6
# ============================================================

import os
import requests


# ============================================================
# LOAD PROMPT
# ============================================================

def load_prompt():

    with open("ai/prompt.txt", "r") as file:
        return file.read()


# ============================================================
# LOAD TERRAFORM FILES
# ============================================================

def load_terraform_code():

    terraform_code = ""

    terraform_dir = "terraform"

    for file_name in os.listdir(terraform_dir):

        if file_name.endswith(".tf"):

            file_path = os.path.join(terraform_dir, file_name)

            with open(file_path, "r") as tf_file:

                terraform_code += f"\n\n### {file_name}\n"
                terraform_code += tf_file.read()

    return terraform_code


# ============================================================
# CALL CLAUDE API
# ============================================================

def get_claude_review(prompt, terraform_code):

    api_key = os.environ["CLAUDE_API_KEY"]

    full_prompt = f"""
{prompt}

Terraform Code:

{terraform_code}
"""

    url = "https://api.anthropic.com/v1/messages"

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1500,
        "messages": [
            {
                "role": "user",
                "content": full_prompt
            }
        ]
    }

    print("Sending request to Claude...")

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print(f"Claude Response Code: {response.status_code}")

    if response.status_code != 200:

        print(response.text)

        raise Exception(
            f"Claude API Error: {response.text}"
        )

    data = response.json()

    return data["content"][0]["text"]


# ============================================================
# POST COMMENT TO GITHUB PR
# ============================================================

def post_pr_comment(review):

    pr_number = os.environ.get("PR_NUMBER")

    if not pr_number:

        print("No PR context found. Skipping comment.")
        return

    repo = os.environ["GITHUB_REPOSITORY"]

    github_token = os.environ["GITHUB_TOKEN"]

    url = (
        f"https://api.github.com/repos/"
        f"{repo}/issues/{pr_number}/comments"
    )

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    body = {
        "body": f"## 🤖 AI Security Review\n\n{review}"
    }

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    print(f"GitHub Comment Status: {response.status_code}")


# ============================================================
# MAIN FLOW
# ============================================================

def main():

    print("Loading AI prompt...")

    prompt = load_prompt()

    print("Loading Terraform files...")

    terraform_code = load_terraform_code()

    print("Generating AI review...")

    review = get_claude_review(
        prompt,
        terraform_code
    )

    print("AI Review Generated Successfully")

    print(review)

    print("Posting review to Pull Request...")

    post_pr_comment(review)

    print("Review completed successfully.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()