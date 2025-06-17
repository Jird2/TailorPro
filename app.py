from flask import Flask, request, render_template, send_file, send_from_directory, request, redirect, flash
from script import run, generate_resume_suggestions, revise_summary_and_bullets
from dotenv import load_dotenv
import os, uuid, smtplib
from email.mime.text import MIMEText

"""Email Issue in contacts unknown"""
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
load_dotenv()
sender_email = os.getenv("EMAIL_USER")
password = os.getenv("EMAIL_PASS")
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        print("Login successful!")
except Exception as e:
    print("Login failed:", e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('resume')
        company_desc = request.form.get('company_desc')
        job_posting = request.form.get('job_posting')

        if file and file.filename.endswith(".docx"):
            input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.docx")
            file.save(input_path)
            print("✔ Uploaded file saved at:", input_path)

            try:
                tailored_output_path = os.path.join(UPLOAD_FOLDER, f"tailored_{uuid.uuid4()}.docx")
                enhanced_output_path = os.path.join(UPLOAD_FOLDER, f"enhanced_{uuid.uuid4()}.docx")

                # Tailor the summary only (basic/regular version)
                run(input_path, company_desc, job_posting, tailored_output_path)
                print("Tailored resume saved at:", tailored_output_path)

                #Generate comprehensive suggestions from the original resume
                suggestions = generate_resume_suggestions(input_path, company_desc, job_posting)
                print("Generated suggestions")

                #Create comprehensive enhanced version from original resume
                revise_summary_and_bullets(input_path, suggestions, job_posting, enhanced_output_path)
                print("Enhanced resume saved at:", enhanced_output_path)

                return render_template(
                    "result.html",
                    tailored_resume=os.path.basename(tailored_output_path),
                    enhanced_resume=os.path.basename(enhanced_output_path),
                    suggestions=suggestions
                )
            except Exception as e:
                print(f"Error processing resume: {str(e)}")
                return f"Error processing resume: {str(e)}", 500
            finally:
                # Clean up the original uploaded file
                if os.path.exists(input_path):
                    os.remove(input_path)
        else:
            return "Invalid file type. Please upload a .docx resume.", 400

    return render_template('index.html')

def send_email(subject, body):
    receiver_email = os.getenv("EMAIL_USER")
    """No need to load email/password since i loaded them already from .env"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
        

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        full_message = f"From: {name} <{email}>\n\n{message}"

        # Send the email
        send_email("Bug Report or Feedback", full_message)
        return render_template("thanks.html")  # Create a simple thanks.html if you'd like
    return render_template("contact.html")

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)