import requests
import markdown
from github import Github
from weasyprint import HTML

def generate_pdf_report_from_readme():
    # Get README from repo
    response = requests.get("https://raw.githubusercontent.com/fabriziosalmi/websites-monitor/main/README.md")
    content = response.text.split("Monitoring Checks")[1]  # Grab from "Monitoring Checks" onwards

    # Convert markdown to HTML, then to PDF
    html_content = markdown.markdown(content)
    HTML(string=html_content).write_pdf("latest.pdf")

    return "latest.pdf"

def create_github_release(pdf_path):
    g = Github(os.environ["PAT"])
    repo = g.get_repo("fabriziosalmi/websites-monitor")
    
    # Delete existing 'latest' release if it exists
    try:
        latest_release = repo.get_release("latest")
        latest_release.delete_release()
    except:
        pass  # If no such release exists, simply pass

    # Now create the release
    release = repo.create_git_release(tag="latest", name="Latest Report", message="Latest monitoring report.", draft=False, prerelease=False)
    release.upload_asset(pdf_path)


def main():
    pdf_path = generate_pdf_report_from_readme()
    if pdf_path:
        create_github_release(pdf_path)

if __name__ == "__main__":
    main()
