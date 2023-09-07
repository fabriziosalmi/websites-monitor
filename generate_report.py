import requests
import subprocess
import os
from github import Github

def generate_pdf_report_from_readme():
    # Fetch README.md content from GitHub
    repo_url = "https://raw.githubusercontent.com/fabriziosalmi/websites-monitor/main/README.md"
    response = requests.get(repo_url)
    response.raise_for_status()
    content = response.text.splitlines()

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
    output_file = "report.pdf"
    cmd = f"pandoc temp.md -o {output_file}"
    subprocess.call(cmd, shell=True)
    os.remove("temp.md")  # Cleanup temporary markdown file

    return output_file

def create_github_release(pdf_path):
    # Authenticate with GitHub using PAT
    g = Github(os.environ["PAT"])
    repo = g.get_user().get_repo("websites-monitor")

    # Check if "latest" release already exists; if it does, delete it
    try:
        latest_release = repo.get_release("latest")
        latest_release.delete_release()
    except:
        pass

    # Create a new release
    release = repo.create_git_release(tag="latest", name="Report.PDF", message="Latest monitoring report.", draft=False, prerelease=False)

    # Attach PDF to the release
    release.upload_asset(pdf_path)

def main():
    pdf_path = generate_pdf_report_from_readme()
    create_github_release(pdf_path)

if __name__ == "__main__":
    main()
