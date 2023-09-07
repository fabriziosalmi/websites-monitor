import os
import requests
from github import Github
import pdfkit

def markdown_to_html(md_content):
    response = requests.post("https://md2pdf.netlify.app/.netlify/functions/convert", data={"input": md_content})
    return response.text

def html_to_pdf(html_content, output_filename):
    pdfkit.from_string(html_content, output_filename)

def get_filtered_readme_content():
    url = "https://raw.githubusercontent.com/fabriziosalmi/websites-monitor/main/README.md"
    response = requests.get(url)
    content = response.text.splitlines()
    start_index = None
    for idx, line in enumerate(content):
        if "Monitoring Checks" in line:
            start_index = idx
            break
    if start_index is None:
        print("Start index not found in README.md")
        return None
    return "\n".join(content[start_index:])

def create_github_release(pdf_path):
    g = Github(os.environ["PAT"])
    repo = g.get_user().get_repo("websites-monitor")

    # Delete existing 'latest' tag if it exists
    try:
        tag_ref = repo.get_git_ref("tags/latest")
        tag_ref.delete()
    except:
        pass

    release = repo.create_git_release(tag="latest", name="Latest Report", message="Latest monitoring report.", draft=False, prerelease=False)
    release.upload_asset(pdf_path)

def main():
    md_content = get_filtered_readme_content()
    html_content = markdown_to_html(md_content)
    pdf_path = "latest.pdf"
    html_to_pdf(html_content, pdf_path)
    create_github_release(pdf_path)

if __name__ == "__main__":
    main()
