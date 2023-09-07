from fpdf import FPDF
from github import Github
import os

def generate_pdf_report(data):
    # Initialize PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add data to PDF (customize this section as needed)
    for line in data:
        pdf.cell(200, 10, txt=line, ln=True)

    pdf_output_path = "report.pdf"
    pdf.output(pdf_output_path)

    return pdf_output_path

def create_github_release(pdf_path):
    # Authenticate with GitHub using a token (set this in your GitHub secrets)
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_user().get_repo("websites-monitor")

    # Create a new release
    release = repo.create_git_release(tag="latest", name="Report.PDF", message="Latest monitoring report.", draft=False, prerelease=False)

    # Attach PDF to the release
    release.upload_asset(pdf_path)

def main(data):
    pdf_path = generate_pdf_report(data)
    create_github_release(pdf_path)
