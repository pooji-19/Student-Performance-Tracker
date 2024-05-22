#import module dependencies
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort,url_for
import sqlite3
import csv
import pandas
import plotly.express as px
import re

#create flask app object
app = Flask(__name__,template_folder='template')


#default page of the website
@app.route('/')
def home():
    return render_template('index.html')


#renders login webpage (rendering template --> index.html)
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pswrd']
        #Getting the data from the database
        conn = sqlite3.connect("credential.db")
        cursor = conn.cursor()
        data = cursor.execute("Select * from credentialstable ").fetchall()
        account = (username,password) in data
        cursor.close()
        conn.close()
        usertype = ''
        if account:
            item = username
            it = item[:item.find('@')]
            if re.search('01$', it):
                usertype = "student"
            if re.search('02$', it):
                usertype = "admin1"
            if re.search('03$', it):
                usertype = "superadmin"
            #rendering the templates according to the user type
            if usertype == "student":
                return redirect(url_for('studentmainpage', username = username))
            if usertype == "admin1":
                return redirect(url_for('adminpage', username = username))
            if usertype == "superadmin":
                return redirect(url_for('superadmin', username = username))
        else:
            msg = 'Invalid username or password'
            return render_template('index.html', msg = msg)


#endpoint that redirect to the mainpage if login successful
@app.route('/mainPage')
def mainPage():
    return render_template('mainPage.html')


#Registering as a new user
@app.route('/register.html', methods =['GET', 'POST'])
def register():
    msg = ''
    try:
        return render_template('register.html',msg = msg)
    except:
        pass
    finally:
       if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['newPassword']
        new_password_confirm = request.form['pswrd']
        if(new_password != new_password_confirm):
            msg = "Passwords does not match"
            return render_template('register.html',msg = msg)

        else:
            insert_database(new_username,new_password)
            return redirect("mainPage")


#This Function inserts new user credentials to the database securely 
def insert_database(new_username,new_password):
    msg = ''
    conn = sqlite3.connect("credential.db")
    cursor = conn.cursor()
    cursor.execute("Insert into credentialstable values(?,?)",(new_username,new_password))
    conn.commit()
    cursor.close()
    conn.close()


#this route renders the data to the mainpage 
@app.route('/studentmainpage')
def studentmainpage():
    username = request.args.get('username')
    with open("students_data.csv") as f:
        csv_ob = csv.reader(f)
        req_student_tuple = []
        for student_tuple in csv_ob:
            if(student_tuple[0] == username):
                req_student_tuple = student_tuple
                break
        student_name = req_student_tuple[3]
        student_rank = int(req_student_tuple[38])
        student_latest_test_marks = float(req_student_tuple[36])
        student_overall_test_score = float(req_student_tuple[37])
        student_present_performance = ''
        if student_overall_test_score > 90 :
            student_present_performance = 'Distinction'
        elif student_overall_test_score > 75 and student_overall_test_score <= 90:
            student_present_performance = 'Good'
        elif student_overall_test_score > 50 and student_overall_test_score <= 75:
            student_present_performance = 'Average'
        else:
            student_present_performance = 'Poor'
        # for student all subject and their marks
        df = pandas.read_csv('students_data.csv')
        columns = ['Math_T1', 'Physics_T1', 'Chemistry_T1', 'English_T1', 'Clang_T1',
        'Math_T2', 'Physics_T2', 'Chemistry_T2', 'English_T2', 'Clang_T2',
        'Math_T3', 'Physics_T3', 'Chemistry_T3', 'English_T3', 'Clang_T3',
        'Math_T4', 'Physics_T4', 'Chemistry_T4', 'English_T4', 'Clang_T4',
        'Math_T5', 'Physics_T5', 'Chemistry_T5', 'English_T5', 'Clang_T5']
        # assuming one need to be replaced
        name = username 
        subjects_data = df[df['username'] == name][columns]
        subject_names = subjects_data.columns
        subject_scores = subjects_data.values[0]
        total_subjects = {'Subject names' : subject_names, 'Subject scores' : subject_scores}
        tot_sub_fig = px.bar(total_subjects, x='Subject names', y='Subject scores', title='All Test Marks')
        tot_sub_fig.update_layout(title='All Test Marks')
        plot_all_sub = tot_sub_fig.to_json()
        # students for tests
        columns_of_test = ['Average_T1', 'Average_T2', 'Average_T3', 'Average_T4', 'Average_T5']
        # assuming one need to be replaced
        name = df['username'].loc[1]
        tests_data = df[df['username'] == name][columns_of_test]
        test_columns = tests_data.columns
        test_data = tests_data.values[0]
        test_subjects = {'Test names' : test_columns , 'Test data' : test_data}
        test_fig = px.bar(test_subjects, x='Test names', y='Test data', title='Test Marks')
        test_fig.update_layout(title='Test Marks')
        plot_test = test_fig.to_json()
        return render_template('mainPage.html',student_name = student_name,student_rank = student_rank,student_latest_test_marks = student_latest_test_marks,student_overall_test_score = student_overall_test_score,student_present_performance = student_present_performance,plot_all_sub = plot_all_sub, plot_test = plot_test)


#This endpoint renders data to the adminpage 
@app.route('/adminPage')
def adminpage():
    username = request.args.get('username')
    #using  the regex to identify the admin's institution
    item = username
    it = item[:item.find('@')-2]
    if re.search('01$', it):
        username = "01"
    elif re.search('02$', it):
        username = "02"
    elif re.search('03$', it):
        username == "03"
    #rendering the ranks based on the institutions
    if username == "01":
        file = "institute1.csv"
    elif username == "02":
        file = "institute2.csv"
    else:
        file = "institute3.csv"
    with open(file) as f:
        csv_ob = csv.reader(f)
        student_1 = ''
        student_2 = ''
        student_3 = ''
        for student_tuple in csv_ob:
            if(student_tuple[39] == "institute_rank"):
                continue
            if(int(student_tuple[39]) == 1):
                student_1 = student_tuple[3]
            if(int(student_tuple[39]) == 2):
                student_2 = student_tuple[3]
            if(int(student_tuple[39]) == 3):
                student_3 = student_tuple[3]
        rank01, rank02, rank03 = rank_computation()
        #Checking the Institution admin type
        item = username
        it = item[:item.find('@')-2]
        if re.search('01$', it):
            username = "01"
        elif re.search('02$', it):
            username = "02"
        elif re.search('03$', it):
            username == "03"
        #rendering the ranks based on the institutions
        if username == "01":
            rank = rank01
        elif username == "02":
            rank = rank02
        else:
            rank = rank03
    #Attendence Computation function
    cseds_avg,csebs_avg,civil_avg,ece_avg = attendence_computation(username)
    #admin plot-1
    df = pandas.read_csv(file)
    student_overall_test_score = df['Total_Average']
    quantify  = []
    for test_score in student_overall_test_score:
            student_present_performance = ''
            if test_score > 90 :
                    student_present_performance = 'Distinction'
            elif test_score > 75 and test_score <= 90:
                    student_present_performance = 'Good'
            elif test_score > 50 and test_score <= 75:
                    student_present_performance = 'Average'
            else:
                    student_present_performance = 'Poor'
            quantify.append(student_present_performance)
    quant_ser = pandas.Series(quantify)
    quantify_values = quant_ser.value_counts().values
    quantify_labels = quant_ser.value_counts().index
    quantify_fig = px.pie(values = quantify_values, names = list(quantify_labels))
    quantify_fig.update_layout(title='Pie chart for student performance')
    quantify_fig.update_traces(textposition='inside', textinfo='percent+label')
    pie_std_quantity = quantify_fig.to_json()
    #AdminPlotNo2
    df = pandas.read_csv(file)
    admins_count = df['Dept.'].value_counts()
    dept_index = list(admins_count.index)
    dept_values = admins_count.values
    dept_count = {'Department' : dept_index, 'Department count' : dept_values}
    tot_sub_fig = px.bar(dept_count, x='Department', y='Department count', title='Department insight')
    tot_sub_fig.update_layout(title='Department insight')
    plot_dept_count = tot_sub_fig.to_json()
    return render_template('adminPage.html',student_1 = student_1,student_2 = student_2,student_3 = student_3,rank = rank,cseds_avg = cseds_avg,csebs_avg = csebs_avg,civil_avg = civil_avg,ece_avg = ece_avg, pie_std_quantity = pie_std_quantity, plot_dept_count = plot_dept_count)

#This function computes the ranks of the institutes
def rank_computation():
    rank01 = 0
    rank02 = 0
    rank03 = 0
    with open("institute1.csv") as f:
        csv_ob = csv.reader(f)
        avg_marks01 = 0 
        for student_tuple in csv_ob:
            if(student_tuple[37] == "Total_Average"):
                continue
            avg_marks01 += float(student_tuple[37])
        avg_marks01 = avg_marks01 /10
    with open("institute2.csv") as f:
        csv_ob = csv.reader(f)
        avg_marks02 = 0 
        for student_tuple in csv_ob:
            if(student_tuple[37] == "Total_Average"):
                continue
            avg_marks02 += float(student_tuple[37])
        avg_marks02 = avg_marks02 /10
    with open("institute3.csv") as f:
        csv_ob = csv.reader(f)
        avg_marks03 = 0 
        for student_tuple in csv_ob:
            if(student_tuple[37] == "Total_Average"):
                continue
            avg_marks03 += float(student_tuple[37])
        avg_marks03 = avg_marks03 /10
    if (avg_marks01 > avg_marks02) and (avg_marks01>avg_marks03):
        rank01 = 1
        if(avg_marks02 > avg_marks03):
            rank02 = 2
            rank03 = 3
        else:
            rank02 = 3
            rank03 = 2
    if (avg_marks02 > avg_marks01) and (avg_marks02 > avg_marks03):
        rank02 = 1
        if(avg_marks01 > avg_marks03):
            rank01 = 2
            rank03 = 3
        else:
            rank01 = 3
            rank03 = 2
    if (avg_marks03 > avg_marks02) and (avg_marks03 > avg_marks01):
        rank03 = 1
        if(avg_marks02 > avg_marks02):
            rank02 = 2
            rank01 = 3
        else:
            rank02 = 3
            rank01 = 2
    return rank01,rank02,rank03

#this function calculates the attendence of all institutes
def attendence_computation(username):
    if username == "01":
        file = "institute1.csv"
    elif username == "02":
        file = "institute2.csv"
    else:
        file = "institute3.csv"
    cseds = []
    csebs = []
    civil = []
    ece  = []
    with open(file) as f:
        csv_ob = csv.reader(f)
        for student_tuple in csv_ob:
            if student_tuple[5] == 'CSEDS':
                cseds.append(float(student_tuple[6]))
            if student_tuple[5] == 'CSEBS':
                csebs.append(float(student_tuple[6]))
            if student_tuple[5] == 'CIVIL':
                civil.append(float(student_tuple[6]))
            if student_tuple[5] == 'ECE':
                ece.append(float(student_tuple[6]))
    cseds_avg = sum(cseds)/len(cseds)
    csebs_avg = sum(csebs)/len(csebs)
    civil_avg = sum(civil)/len(civil)
    ece_avg = sum(ece)/len(ece)
    return cseds_avg,csebs_avg,civil_avg,ece_avg


#This endpoint renders data to the superadmin page
@app.route('/superadmin')
def superadmin():
    total_df = pandas.read_csv('students_data.csv')
    attvsavg = px.line(total_df, y=['Attendence', 'Total_Average'])
    attvsavg.update_layout(title_text='Attendence vs Total_Average')
    attvsavg.update_layout(width=1100, height=400)
    attvsavg_plot = attvsavg.to_json()
    return render_template('superadmin.html',attvsavg_plot = attvsavg_plot)

#Running the flask application in debug mode
if __name__ == '__main__':
    app.debug = True
    app.run()