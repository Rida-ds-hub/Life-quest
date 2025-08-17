# LifeQuest – Personal Task & Development Manager

LifeQuest is a centralized personal management platform designed to help users track and organize their **academic, professional, and personal milestones** in one place.  
It provides functionality for **goal tracking, habit monitoring, academic assignments, professional networking, and more** through a database-driven web interface.

---

## 📂 Project Structure
The main files included in this repository are:

- `lifequest.py` – Core Python backend script (Flask-based).  
- `Lifequest_base.ipynb` – Jupyter Notebook for database design, queries, and analysis.  

⚠️ **Note:** This project also requires a `templates/` folder (not included here) containing the necessary HTML files for rendering the web interface. The folder structure should look like this:

templates/
│── index.html
│── signup.html
│── signin.html
│── signin_success.html
│── personal_forms.html
│── personal_milestones.html
│── academic_milestones.html
│── professional_milestones.html


Make sure to place these files in the `templates/` directory before running the application.

---

## ⚙️ Requirements
- Python 3.8+  
- Flask  
- MySQL (or SQLite for lightweight testing)  
- Libraries: `pandas`, `numpy`, `matplotlib`, `seaborn`  


📊 Features
Personal Development: Goals, habits, mental health journal, achievement tracker.

Academic Development: Assignment tracking, exam/project deadlines, grade management.

Professional Development: Networking contacts, job application tracker, professional activities.

🛠️ Tech Stack
Backend: Python (Flask)

Database: MySQL (relational schema) + Neo4j (graph extension)

Frontend: HTML templates (Flask rendering)

Visualization: Matplotlib, Seaborn

✨ Authors
Rida Khan
Haritha Rathnam Kuppala

📌 This project was developed as part of Northeastern University’s IE6700 course.
