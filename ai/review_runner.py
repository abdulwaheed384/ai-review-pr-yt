# ============================================================
# AI PR REVIEW - VIDEO 6
# ============================================================
#
# Purpose:
# This script reads Terraform code from the repository,
# sends it to Claude AI for review,
# and posts the AI review back to the Pull Request.
#
# Workflow:
#
# Terraform Files
#        │
#        ▼
# Load Prompt
#        │
#        ▼
# Claude API
#        │
#        ▼
# AI Review
#        │
#        ▼
# GitHub PR Comment
#
# ============================================================

import os
import requests
from anthropic import Anthropic


# ============================================================
# STEP 1
# LOAD THE REVIEW PROMPT
# ============================================================
#
# We keep the prompt outside the Python code
# so it can be modified without changing code.
#
# This also prepares us for future videos where
# we will introduce:
#
# - policy.md
# - scoring.json
#
# and make the AI reviewer context-aware.
#
# ============================================================

def load_prompt():

    with open("ai/prompt.txt", "r") as file:
        return file.read()


# ============================================================
# STEP 2
# LOAD TERRAFORM CODE
# ============================================================
#
# For Video 6 we keep things simple.
#
# Instead of analysing PR diffs,
# we read all Terraform files.
#
# Terraform Folder:
#
# terraform/
# ├── main.tf
# ├── network.tf
# ├── nsg.tf
# ├── variables.tf
# └── outputs.tf
#
# These files are combined into a single string
# and sent to Claude.
#
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
# STEP 3
# SEND CODE TO CLAUDE
# ============================================================
#
# Claude receives:
#
# 1. Prompt Template
# 2. Terraform Code
#
# Example:
#
# "Review this Terraform code.
# Identify security risks,
# misconfigurations and recommendations."
#
# Claude then returns a detailed review.
#
# ============================================================

def get_claude_review(prompt, terraform_code):

    # Create Claude client
    client = Anthropic(
        api_key=os.environ["CLAUDE_API_KEY"]
    )

    # Build final prompt
    full_prompt = f"""
{prompt}

Terraform Code:

{terraform_code}
"""

    # Send request to Claude
    response = client.messages.create(

        model="claude-sonnet-4-20250514",

        max_tokens=1500,

        messages=[
            {
                "role": "user",
                "content": full_prompt
            }
        ]
    )

    # Extract text response
    return response.content[0].text


# ============================================================
# STEP 4
# POST REVIEW TO GITHUB
# ============================================================
#
# Once Claude returns a response,
# we post it directly to the Pull Request.
#
# GitHub automatically provides:
#
# GITHUB_TOKEN
#
# which allows the workflow
# to create comments.
#
# Example Result:
#
# -----------------------------
# AI Security Review
#
# Findings
# - NSG allows unrestricted access
#
# Recommendation
# - Restrict source IP ranges
# -----------------------------
#
# ============================================================

def post_pr_comment(review):

    # Pull Request Number
    pr_number = os.environ.get("PR_NUMBER")

    # Skip if workflow was not triggered by a PR
    if not pr_number:

        print("No PR context found. Skipping comment.")
        return

    # Repository Name
    repo = os.environ["GITHUB_REPOSITORY"]

    # GitHub Authentication Token
    github_token = os.environ["GITHUB_TOKEN"]

    # GitHub API Endpoint
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

    print(f"GitHub Response: {response.status_code}")


# ============================================================
# MAIN EXECUTION FLOW
# ============================================================
#
# This is where everything comes together.
#
# Step 1:
# Load Prompt
#
# Step 2:
# Load Terraform Code
#
# Step 3:
# Send To Claude
#
# Step 4:
# Receive Review
#
# Step 5:
# Post Comment To PR
#
# ============================================================

def main():

    print("Loading AI prompt...")

    prompt = load_prompt()

    print("Loading Terraform files...")

    terraform_code = load_terraform_code()

    print("Sending code to Claude...")

    review = get_claude_review(
        prompt,
        terraform_code
    )

    print("Claude review received.")

    print(review)

    print("Posting review to Pull Request...")

    post_pr_comment(review)

    print("Review completed.")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================
#
# Python starts execution here.
#
# ============================================================

if __name__ == "__main__":
    main()