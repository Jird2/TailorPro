from script import run
resume_path = "resume.docx"
output_path = "tailored_resume.docx"
company_desc = "Google is a technology company focused on organizing the world’s information..."
job_posting = "We're seeking an intern with experience in Python and ML to join our AI team..."

run(resume_path, company_desc, job_posting, output_path)