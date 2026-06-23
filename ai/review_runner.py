# ============================================================
# AI PR REVIEW - VIDEO 6
#
# Purpose:
# Automatically review Terraform code using Claude AI
# and post the review directly into a GitHub Pull Request.
#
# Workflow:
#
# Pull Request
#      │
#      ▼
# Load Prompt
#      │
#      ▼
# Load Terraform Files
#      │
#      ▼
# Send to Claude AI
#      │
#      ▼
# Receive Review
#      │
#      ▼
# Post Comment to GitHub PR
#
# ============================================================

import os
import requests


# ============================================================
# LOAD PROMPT
# ============================================================
#
# The prompt defines how Claude should behave.
#
# Instead of hardcoding instructions in Python,
# we store them in prompt.txt.
#
# Benefits:
# - Easier to update AI behavior
# - No code changes required
# - Prompt engineering separated from application logic
#
# ============================================================

def load_prompt():

    with open("ai/prompt.txt", "r") as file:
        return file.read()


# ============================================================
# LOAD TERRAFORM FILES
# ============================================================
#
# This function gathers all Terraform files from
# the terraform folder.
#
# Current Video 6 Approach:
# - Read every .tf file
# - Combine them into a single string
# - Send the complete codebase to Claude
#
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
# CALL CLAUDE API
# ============================================================
#
# This is the AI engine of the solution.
#
# Steps:
# 1. Read API key from GitHub Secrets
# 2. Combine Prompt + Terraform Code
# 3. Send request to Claude
# 4. Receive AI-generated review
#
# Claude acts as a Security Architect and reviews:
#
# - Security risks
# - Misconfigurations
# - Terraform best practices
# - Azure recommendations
# - Networking concerns
#
# ============================================================

def get_claude_review(prompt, terraform_code):

    # Read Claude API Key from GitHub Actions Secret
    api_key = os.environ["CLAUDE_API_KEY"]

    # Combine Prompt + Terraform Source Code
    full_prompt = f"""
{prompt}

Terraform Code:

{terraform_code}
"""

    # Anthropic Messages API Endpoint
    url = "https://api.anthropic.com/v1/messages"

    # Required API Headers
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    # Request Payload
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

    # Handle API Errors
    if response.status_code != 200:

        print(response.text)

        raise Exception(
            f"Claude API Error: {response.text}"
        )

    # Parse Claude Response
    data = response.json()

    return data["content"][0]["text"]


# ============================================================
# POST COMMENT TO GITHUB PR
# ============================================================
#
# Once Claude generates the review,
# we automatically publish it back into GitHub.
#
# We use:
# - GITHUB_TOKEN
# - Repository Name
# - Pull Request Number
#
# GitHub then displays the review directly
# inside the Pull Request conversation.
#
# This is the "WOW" moment of Video 6.
#
# ============================================================

def post_pr_comment(review):

    # Pull Request Number supplied by GitHub Actions
    pr_number = os.environ.get("PR_NUMBER")

    # Skip execution if not running from a PR
    if not pr_number:

        print("No PR context found. Skipping comment.")
        return

    # Repository Information
    repo = os.environ["GITHUB_REPOSITORY"]

    # GitHub Actions Token
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

    # Comment Body
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
# MAIN ORCHESTRATION FLOW
# ============================================================
#
# This function controls the entire workflow.
#
# Step 1 - Load Prompt
# Step 2 - Load Terraform Code
# Step 3 - Generate AI Review
# Step 4 - Post Comment to PR
#
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
# APPLICATION ENTRY POINT
# ============================================================
#
# Python starts execution here.
#
# ============================================================

if __name__ == "__main__":
    main()