from github import Github
import os
import subprocess
import datetime
import traceback

def generate_pdf_report_from_readme():
    output_file = "report.pdf"
    with open("README.md", "r") as file:
        content = file.readlines()

    start_index = None
    for idx, line in enumerate(content):
        if "| Website | Result |" in line:
            start_index = idx
            break

    if start_index is None:
        print("Table not found in README.md")
        return

    table_content = content[start_index:]
    temp_md = "\n".join(table_content)
    with open("temp.md", "w") as temp_file:
        temp_file.write(temp_md)

    cmd = f"pandoc temp.md -o {output_file}"
    subprocess.call(cmd, shell=True)
    os.remove("temp.md")

    return output_file

def create_github_release(pdf_path):
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo("fabriziosalmi/websites-monitor")  # Specifying repo in this manner

    release = repo.create_git_release(tag="latest", name="Report.PDF", message="Latest monitoring report.", draft=False, prerelease=False)
    release.upload_asset(pdf_path)

def main():
    try:
        pdf_path = generate_pdf_report_from_readme()
        if pdf_path:
            create_github_release(pdf_path)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
