from github import Github
import os
import subprocess
import requests

def generate_pdf_report_from_readme():
    # Get the raw content of README.md from the repo
    url = "https://raw.githubusercontent.com/fabriziosalmi/websites-monitor/main/README.md"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to fetch README.md. Status Code: {response.status_code}")
        return

    content = response.text
    output_file = "latest.pdf"

    with open("temp.md", "w") as temp_file:
        temp_file.write(content)

    # Convert the temporary markdown file to PDF
    cmd = f"pandoc temp.md -o {output_file}"
    subprocess.call(cmd, shell=True)
    os.remove("temp.md")  # Cleanup temporary markdown file

    return output_file

def create_github_release(pdf_path):
    # Authenticate with GitHub
    g = Github(os.environ["PAT"])
    repo = g.get_user().get_repo("websites-monitor")

    # Create a new release
    release = repo.create_git_release(tag="latest", name="Latest Report", message="Latest monitoring report.", draft=False, prerelease=False)

    # Attach PDF to the release
    release.upload_asset(pdf_path)

def main():
    pdf_path = generate_pdf_report_from_readme()
    if pdf_path:
        create_github_release(pdf_path)

if __name__ == "__main__":
    main()
