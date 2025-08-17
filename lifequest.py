from flask import Flask, render_template, request, session, redirect, url_for

import mysql.connector

import plotly.graph_objs as go 
import plotly.offline as pyo
import numpy as np

app = Flask(__name__)
app.secret_key = '******'

# Connect to MySQL database
connection = mysql.connector.connect(
    user='root',
    password='*********',
    host='localhost',
    database='lifequest',
    ssl_disabled=True
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials in the database
        cursor = connection.cursor(dictionary=True)  # Fetch as dictionary
        cursor.execute("SELECT * FROM user WHERE Username = %s AND Password = %s", (username, password))
        user = cursor.fetchone()
        
        if user:
            # Store User_ID in session
            session['User_ID'] = user['User_ID']
            if 'username' in user:
                session['username'] = user['username']
            else:
                session['username'] = username
            cursor.close()
            # Redirect to success page or user dashboard
            return render_template('signin_success.html', username=username)
        else:
            cursor.close()
            # Redirect to error page or sign in page with error message
            return render_template('signin.html', error="Invalid username or password")
    else:
        return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        
        # Insert into database
        cursor = connection.cursor()
        cursor.execute("INSERT INTO user (Username, Name_Fname, Name_Lname, Email, Password, Phone) VALUES (%s, %s, %s, %s, %s, %s)", (username, firstname, lastname, email, password, phone))
        connection.commit()
        cursor.close()
        
        # Redirect to success page or homepage
        return render_template('signin.html')
    else:
        return render_template('signup.html')
    
@app.route('/signin_success')
def signin_success():
    # Get the User_ID from the session
    username = session.get('username')
    return render_template('signin_success.html', username=username)

    
@app.route('/personal_milestones', methods=['GET', 'POST'])
def personal_milestones():
    if request.method == 'POST' and 'show_forms' in request.form:
        # Redirect to the personal_forms route when the button is clicked
        return redirect(url_for('personal_forms'))

    
    user_id = session.get('User_ID')  # Get the User_ID from the session
    cursor = connection.cursor(dictionary=True)
    # Fetch data from PERSONAL table for the logged-in user
    cursor.execute("SELECT DISTINCT p.Personal_Type FROM PERSONAL p JOIN PERSONAL_GOAL pg ON p.Personal_ID = pg.Personal_ID WHERE pg.User_ID = %s", (user_id,))
    personal_data = [row['Personal_Type'] for row in cursor.fetchall()]
    # Split the personal_data list into chunks of 5 for the template
    personal_data_chunks = [personal_data[i:i + 5] for i in range(0, len(personal_data), 5)]

   # Fetch personal goals for the logged-in user
    cursor.execute("SELECT Goal_Name, MAX(Deadline) AS Deadline, MAX(Priority) AS Priority, MAX(Category) AS Category, MAX(Motivation) AS Motivation FROM PERSONAL_GOAL WHERE User_ID = %s GROUP BY Goal_Name", (user_id,))
    personal_goals = cursor.fetchall()
     # Fetch habit data
    cursor.execute("SELECT Habit_Name, Frequency, Reminder FROM HABIT WHERE User_ID = %s", (user_id,))
    habits = cursor.fetchall()
    
    #fetch achievement data 
    cursor.execute("SELECT Description, Date_Achieved, Impact, Lessons_Learned FROM Achievement WHERE User_ID = %s", (user_id,))
    achievements = cursor.fetchall()
    
    # Fetch mental health entries (limit to top 3)
    cursor.execute("SELECT Date, Mood, Journal_Entry, Coping_Strategies FROM MENTAL_HEALTH_ENTRY WHERE User_ID = %s", (user_id,))
    mental_health_entries = cursor.fetchall()

# Fetch notes (limit to top 3)
    cursor.execute("SELECT Title, Content, Tags, Importance, Context FROM NOTE WHERE User_ID = %s", (user_id,))
    notes = cursor.fetchall()

    cursor.close()
    
    return render_template('personal_milestones.html', personal_data_chunks=personal_data_chunks, personal_goals=personal_goals, habits=habits, achievements=achievements, mental_health_entries=mental_health_entries, notes=notes)




# Route for rendering the personal_forms.html template
@app.route('/personal_forms')
def personal_forms():
    # Fetch unique categories from the personal table and pass them to the template
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT Personal_Type FROM PERSONAL")
    categories = [row[0] for row in cursor.fetchall()]
    

    # Fetch unique priorities from the personal goal table and pass them to the template
    cursor.execute("SELECT DISTINCT Priority FROM PERSONAL_GOAL")
    priorities = [row[0] for row in cursor.fetchall()]
    
    
    cursor.close()
    return render_template('personal_forms.html', categories=categories, priorities=priorities)


# Route for handling the submission of a new goal
@app.route('/submit_goal', methods=['POST'])
def submit_goal():
    # Extract data from the form
    goal_name = request.form['goal_name']
    deadline = request.form['deadline']
    priority = request.form['priority']
    category = request.form['category']
    motivation = request.form['motivation']
    
    # Fetch the Personal_ID based on the provided category
    cursor = connection.cursor()
    cursor.execute("SELECT Personal_ID FROM PERSONAL WHERE Personal_Type = %s", (category,))
    personal_id = cursor.fetchone()[0]  # Assuming Personal_ID is the first column in the result
    cursor.close()
    
    # Process the form data (insert into the database, etc.)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO PERSONAL_GOAL (Goal_Name, Deadline, Priority, Category, Motivation, Personal_ID, User_ID) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (goal_name, deadline, priority, category, motivation, personal_id, session['User_ID']))
    connection.commit()
    cursor.close()
    
    # Redirect to the personal_forms page after submission
    return redirect('/personal_forms')

 

import plotly.graph_objs as go
import plotly.offline as pyo

@app.route('/academic_milestones')
def academic_milestones():
    user_id = session.get('User_ID')  # Get the User_ID from the session
    cursor = connection.cursor(dictionary=True)
    
    # Fetch scores data from the database
    cursor.execute("SELECT g.Score FROM GRADE g JOIN COURSE_ASSIGNMENT ca ON g.Task_ID = ca.Task_ID WHERE ca.User_ID = %s", (user_id,))
    scores_data = [row['Score'] for row in cursor.fetchall()]

    # Fetch difficulty levels and scores for different levels
    difficulty_levels = ['Easy', 'Medium', 'Hard']
    scores_by_difficulty = []
    for level in difficulty_levels:
        cursor.execute("SELECT g.Score FROM GRADE g JOIN COURSE_ASSIGNMENT ca ON g.Task_ID = ca.Task_ID WHERE ca.User_ID = %s AND ca.Difficulty = %s", (user_id, level))
        scores = [row['Score'] for row in cursor.fetchall()]
        scores_by_difficulty.append(scores)

    # Create histogram trace
    histogram_trace = go.Histogram(x=scores_data, marker=dict(color='orange'), opacity=0.7)

    # Create boxplot traces
    boxplot_traces = [
        go.Box(y=scores, name=level, marker=dict(color=color))
        for scores, level, color in zip(scores_by_difficulty, difficulty_levels, ['lightblue', 'lightgreen', 'lightcoral'])
    ]

    # Create layout for histogram
    histogram_layout = go.Layout(title='Distribution of Scores', xaxis=dict(title='Score'), yaxis=dict(title='Count'))

    # Create layout for boxplot
    boxplot_layout = go.Layout(title='Distribution of Scores for Different Difficulty Levels', xaxis=dict(title='Difficulty Level'), yaxis=dict(title='Score'))

    # Create figures
    fig_histogram = go.Figure(data=[histogram_trace], layout=histogram_layout)
    fig_boxplot = go.Figure(data=boxplot_traces, layout=boxplot_layout)

    # Save figures as HTML files
    histogram_html = pyo.plot(fig_histogram, output_type='div', include_plotlyjs=False)
    boxplot_html = pyo.plot(fig_boxplot, output_type='div', include_plotlyjs=False)

    # Fetch academic data
    cursor.execute("SELECT DISTINCT ca.Course_Subject, a.Academic_ID FROM COURSE_ASSIGNMENT ca JOIN ACADEMIC a ON ca.Academic_ID = a.Academic_ID WHERE ca.User_ID = %s", (user_id,))
    academic_subjects = cursor.fetchall()

    academic_data = []
    for subject in academic_subjects:
        # Fetch data for each subject
        cursor.execute("""SELECT ca.Task_Name, g.Score, ca.Weightage 
                          FROM COURSE_ASSIGNMENT ca 
                          JOIN GRADE g ON ca.Task_ID = g.Task_ID 
                          WHERE ca.User_ID = %s AND ca.Academic_ID = %s""", (user_id, subject['Academic_ID']))
        subject_data = cursor.fetchall()

        if subject_data:
            # Calculate overall grade for the subject
            overall_grade = sum(task['Score'] * task['Weightage'] for task in subject_data) / sum(task['Weightage'] for task in subject_data)
            academic_data.append({'Subject': subject['Course_Subject'], 'Tasks': subject_data, 'Overall_Grade': round(overall_grade, 2)})
        else:
            # If there are no tasks, set overall grade to 0
            academic_data.append({'Subject': subject['Course_Subject'], 'Tasks': [], 'Overall_Grade': 0})

    cursor.close()
    
    return render_template('academic_milestones.html', academic_data=academic_data, histogram_html=histogram_html, boxplot_html=boxplot_html)



@app.route('/professional_milestones')
def professional_milestones():
    user_id = session.get('User_ID')  # Get the User_ID from the session
    cursor = connection.cursor(dictionary=True)
    
    # Fetch data from PROFESSIONAL_ACTIVITY table for the logged-in user
    cursor.execute("SELECT * FROM PROFESSIONAL_ACTIVITY WHERE User_ID = %s", (user_id,))
    professional_activities = cursor.fetchall()
    
    # Fetch data from NETWORKING_EVENT table for the logged-in user
    cursor.execute("""SELECT nc.*, p.Professional_Type
                      FROM NETWORKING_CONTACT nc 
                      JOIN NETWORKING_EVENT ne ON nc.Associated_Event = ne.Event_ID 
                      JOIN PROFESSIONAL p ON nc.Professional_ID = p.Professional_ID
                      WHERE ne.User_ID = %s""", (user_id,))
    networking_contacts = cursor.fetchall()
    
    # Fetch data from JOB_APPLICATION table for the logged-in user
    cursor.execute("SELECT * FROM JOB_APPLICATION WHERE User_ID = %s", (user_id,))
    job_applications = cursor.fetchall()
    
    # Group data into chunks of 5 for easier rendering in the template
    professional_data_chunks = [
        {
            'Professional_Activities': professional_activities[i:i + 5],
            'Networking_Contacts': networking_contacts[i:i + 5],
            'Job_Applications': job_applications[i:i + 5]
        }
        for i in range(0, max(len(professional_activities), len(networking_contacts), len(job_applications)), 5)
    ]
    
    # Prepare data for horizontal bar chart (total number of networking contacts for each professional type)
    professional_types = [contact.get('Professional_Type', 'Unknown') for contact in networking_contacts]
    professional_type_counts = {ptype: professional_types.count(ptype) for ptype in set(professional_types)}
    professional_type_counts_sorted = dict(sorted(professional_type_counts.items(), key=lambda item: item[1], reverse=True))
    
    # Create trace for horizontal bar chart
    bar_chart_data = go.Bar(x=list(professional_type_counts_sorted.values()), y=list(professional_type_counts_sorted.keys()), orientation='h')
    
    # Create layout for horizontal bar chart
    bar_chart_layout = go.Layout(title='Total Number of Networking Contacts for Each Professional Type', yaxis=dict(title='Number of Contacts'), xaxis=dict(title='Professional Type'))
    
    # Create figure for horizontal bar chart
    bar_chart_fig = go.Figure(data=[bar_chart_data], layout=bar_chart_layout)
    
    # Display plot as HTML div
    bar_chart_div = pyo.plot(bar_chart_fig, output_type='div', include_plotlyjs=False)
    
    # Prepare data for treemap chart (distribution among industries of networking contacts)
    industries = [contact['Industry'] for contact in networking_contacts]
    industry_counts = {industry: industries.count(industry) for industry in set(industries)}
    labels = list(industry_counts.keys())
    parents = ['' for _ in range(len(industry_counts))]
    values = list(industry_counts.values())
    
    # Create treemap chart
    treemap_data = go.Treemap(labels=labels, parents=parents, values=values, textinfo='label+value')
    
    # Create layout for treemap chart
    treemap_layout = go.Layout(title='Distribution Among Industries of Networking Contacts')
    
    # Create figure for treemap chart
    treemap_fig = go.Figure(data=[treemap_data], layout=treemap_layout)
    
    # Display plot as HTML div
    treemap_div = pyo.plot(treemap_fig, output_type='div', include_plotlyjs=False)
    
    # Close cursor
    cursor.close()
    
    # Render the template with data and plots
    return render_template('professional_milestones.html', professional_data_chunks=professional_data_chunks, bar_chart_div=bar_chart_div, treemap_div=treemap_div)



if __name__ == "__main__":
    app.run(debug=True)
