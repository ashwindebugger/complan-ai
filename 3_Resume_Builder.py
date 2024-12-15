import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import tempfile

def create_resume_pdf(name, email, phone, address, education, experience, skills, hobbies, languages):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf_path = tmpfile.name

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        'CustomStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=12, spaceAfter=10
    )
    content = []

    content.append(Paragraph(name, styles['Title']))
    content.append(Spacer(1, 12))

    contact_info = f"Email: {email} | Phone: {phone} | Address: {address}"
    content.append(Paragraph(contact_info, custom_style))
    content.append(Spacer(1, 12))

    def add_section(title, items,bullet=True):
        content.append(Paragraph(title, styles['Heading2']))
        for item in items:
            if bullet == True:
                content.append(Paragraph(f"• {item}", custom_style))
            else:
                content.append(Paragraph(f"{item}", custom_style))
        content.append(Spacer(1, 12))

    add_section("Education", education, False)
    add_section("Work Experience", experience, False)
    add_section("Skills", skills)
    add_section("Hobbies", hobbies)
    add_section("Languages", languages)

    doc.build(content)

    return pdf_path

def main():
    st.set_page_config(page_title="Resume Builder", page_icon=":memo:", layout="wide")
    
    st.title("Resume Builder")
    st.write("### Create a professional resume with ease.")

    with st.form(key='resume_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Personal Information")
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            address = st.text_input("Address")

        with col2:
            st.subheader("Resume Details")
            
            education = st.text_area("Education (separate entries with a newline)", value="\n".join(st.session_state.get('education', [])))
            experience = st.text_area("Work Experience (separate entries with a newline)", value="\n".join(st.session_state.get('experience', [])))
            skills = st.text_area("Skills (separate entries with a newline)", value="\n".join(st.session_state.get('skills', [])))
            hobbies = st.text_area("Hobbies (separate entries with a newline)", value="\n".join(st.session_state.get('hobbies', [])))
            languages = st.text_area("Languages (separate entries with a newline)", value="\n".join(st.session_state.get('languages', [])))
            
            submit_button = st.form_submit_button("Generate PDF")
    
    if submit_button:
        if name and email and phone and address and education and experience and skills and hobbies and languages:
            education_list = education.split('\n')
            experience_list = experience.split('\n')
            skills_list = skills.split('\n')
            hobbies_list = hobbies.split('\n')
            languages_list = languages.split('\n')
            
            pdf_path = create_resume_pdf(name, email, phone, address, education_list, experience_list, skills_list, hobbies_list, languages_list)
            
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
                st.download_button(label="Download Resume", data=pdf_bytes, file_name="resume.pdf", mime="application/pdf")
        else:
            st.error("Please fill out all fields before generating the resume.")

if __name__ == "__main__":
    main()
