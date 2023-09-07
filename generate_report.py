from github import Github
import os
import subprocess
import datetime

def generate_pdf_report_from_readme():
    # Use pandoc to convert README.md to PDF, excluding the introduction
    output_file = "report.pdf"
    with open("README.md", "r") as file:
        content = file.readlines()

    # Filter out the introduction or any other unwanted lines
    start_index = None
    for idx, line in enumerate(content):
        if "| Website | Result |" in line:  # Assuming this is the start of your table
            start_index = idx
            break

    if start_index is None:
        print("Table not found in README.md")
        return

    table_content = content[start_index:]
    temp_md = "\n".join(table_content)
    with open("temp.md", "w") as temp_file:
        temp_file.write(temp_md)

    # Convert to PDF
    cmd = f"pandoc temp.md -o {output_file}"
    subprocess.call(cmd, shell=True)
    os.remove("temp.md")  # Cleanup temporary markdown file

    return output_file

def create_github_release(pdf_path):
    # Authenticate with GitHub
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_user().get_repo("websites-monitor")

    # Create a new release
    release = repo.create_git_release(tag="latest", name="Report.PDF", message="Latest monitoring report.", draft=False, prerelease=False)

    # Attach PDF to the release
    release.upload_asset(pdf_path)

def main():
    pdf_path = generate_pdf_report_from_readme()
    create_github_release(pdf_path)
