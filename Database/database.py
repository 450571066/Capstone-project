import pandas as pd
import MySQLdb as mysql
from sqlalchemy import create_engine
import hashlib

engine = create_engine("mysql://root:ll971220@localhost:3306/LSU")

database = mysql.connect(host="localhost", port=3306, user="root", password="ll971220", db="LSU")

df_pro = pd.read_csv('Professors.csv', encoding='utf-8')
df_stu = pd.read_csv('Students.csv', encoding='utf-8')
df_sec = pd.read_csv('Sections.csv', encoding='utf-8')
df_cap = pd.read_csv('Cap_sec.csv', encoding='utf-8')
df_team = pd.read_csv('Cap_team.csv', encoding='utf-8')

cursor = database.cursor()
connect = engine.connect()

'''
drop if exists
'''
#cursor.execute("DROP TABLE IF EXISTS LSU.Student")
cursor.execute("DROP TABLE IF EXISTS LSU.Zipcode")
#cursor.execute("DROP TABLE IF EXISTS LSU.Professor")
cursor.execute("DROP TABLE IF EXISTS LSU.Department")
cursor.execute("DROP TABLE IF EXISTS LSU.Course")
cursor.execute("DROP TABLE IF EXISTS LSU.Sections")
cursor.execute("DROP TABLE IF EXISTS LSU.Enrolls")
cursor.execute("DROP TABLE IF EXISTS LSU.Prof_teams")
cursor.execute("DROP TABLE IF EXISTS LSU.Prof_team_members")
cursor.execute("DROP TABLE IF EXISTS LSU.Homework")
cursor.execute("DROP TABLE IF EXISTS LSU.Homework_grades")
cursor.execute("DROP TABLE IF EXISTS LSU.Exams")
cursor.execute("DROP TABLE IF EXISTS LSU.Exam_grades")
cursor.execute("DROP TABLE IF EXISTS LSU.Capstone_section")
cursor.execute("DROP TABLE IF EXISTS LSU.Capstone_Team")
cursor.execute("DROP TABLE IF EXISTS LSU.Capstone_Team_Members")
cursor.execute("DROP TABLE IF EXISTS LSU.Capstone_grades")

'''
Creating Tables
'''

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Student (Semail CHAR(50), Spassword CHAR(100), Sname CHAR(50), "
               "Stu_age INT, Sgender CHAR(5), Smajor CHAR(50), Sstreet CHAR(50), Szipcode INT, PRIMARY KEY (Semail))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Zipcode (zipcode INT, city CHAR(50), state CHAR(20),"
               " PRIMARY KEY (zipcode))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Professor (email CHAR(50), password CHAR(100), name CHAR(20), "
               "age INT, gender CHAR(5), "
               "office_address CHAR(50), department CHAR(20), title CHAR(20), PRIMARY KEY (email))")                    #office address = office

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Department (dept_id CHAR(20), dept_name CHAR(20), dept_head CHAR(20), "  #dept_id = department, dept_name = department name, dept_head = name of the head
               "PRIMARY KEY (dept_id))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Course (course_id CHAR(20), course_name CHAR(50), "                      
               "course_description CHAR(100), PRIMARY KEY (course_id))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Sections (course_id CHAR(20), sec_no INT, section_type CHAR(20), "
               "limits INT, prof_team_id INT, PRIMARY KEY (course_id, sec_no))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Enrolls (student_email CHAR(50), course_id CHAR(20), section_no INT, "
               "PRIMARY KEY(student_email, course_id))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Prof_teams (team_id INT, PRIMARY KEY (team_id))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Prof_team_members (prof_email CHAR(50), team_id INT, "
               "PRIMARY KEY(prof_email))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Homework (course_id CHAR(20), sec_no INT, hw_no INT, "
               "hw_details CHAR(100), PRIMARY KEY(course_id, sec_no, hw_no))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Homework_grades (student_email CHAR(100), course_id CHAR(20), "
               "sec_no INT, hw_no INT, grade INT, PRIMARY KEY(student_email, course_id, sec_no, hw_no))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Exams (course_id CHAR(20), sec_no INT, exam_no INT, "
               "exam_details CHAR(100), PRIMARY KEY(course_id, sec_no, exam_no))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Exam_grades (student_email CHAR(50), course_id CHAR(20), sec_no INT, "
               "exam_no INT, grades INT, PRIMARY KEY(student_email, course_id, sec_no,exam_no))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Capstone_section (course_id CHAR(20), sec_no INT, project_no INT, "
               "sponsor_id CHAR(50), PRIMARY KEY(course_id, sec_no, project_no))")                                      #sponser_id = email of sponsor professor

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Capstone_Team (course_id CHAR(20), sec_no INT, team_id INT, "
               "project_no INT, PRIMARY KEY(course_id, sec_no, team_id))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Capstone_Team_Members(student_email CHAR(50), team_id INT, "
               "course_id CHAR(20), sec_no INT, PRIMARY KEY (student_email, course_id, sec_no))")

cursor.execute("CREATE TABLE IF NOT EXISTS LSU.Capstone_grades (course_id CHAR(20), sec_no INT, team_id INT, "
               "grade INT, PRIMARY KEY(course_id, sec_no, team_id))")



'''
Inserting Data into Tables
'''


for a, b, c, d, e, f, g, h in zip(df_stu['Email'].values, df_stu['Password'].values, df_stu['Full Name'].values, df_stu['Age'].values,
                                  df_stu['Gender'].values, df_stu['Major'].values, df_stu['Street'].values, df_stu['Zip'].values):
    cursor.execute("INSERT IGNORE INTO LSU.Student (Semail, Spassword, Sname, Stu_age, Sgender, Smajor, Sstreet, Szipcode) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" , (a,hashlib.sha256(str(b).encode('utf-8')).hexdigest(), c, d, e, f, g, h))

for a, b, c in zip(df_stu['Zip'], df_stu['City'], df_stu['State']):
    cursor.execute("INSERT IGNORE INTO LSU.Zipcode (zipcode, city, state) VALUES ('%d', '%s', '%s')" % (a, b, c))

for a,b,c,d,e,f,g,h in zip(df_pro['Email'], df_pro['Password'], df_pro['Name'], df_pro['Age'], df_pro['Gender'], df_pro['Office'], df_pro['Department Name'], df_pro['Title']):
    cursor.execute("INSERT IGNORE INTO LSU.Professor (email, password, name, age, gender, office_address, department, title) VALUES ('%s', '%s', '%s', '%d', '%s', '%s', '%s', '%s')" %(a, hashlib.sha256(str(b).encode('utf-8')).hexdigest(),c,d,e,f,g,h))

for a, b, c, d in zip(df_pro['Department'], df_pro['Department Name'], df_pro['Name'], df_pro['Title']):
    if d == 'Head':
        cursor.execute("INSERT IGNORE INTO LSU.Department (dept_id, dept_name, dept_head) VALUES ('%s', '%s', '%s')" % (a, b, c))
        
for a, b, c in zip(df_stu['Courses 1'], df_stu['Course 1 Name'], df_stu['Course 1 Details']):
    cursor.execute("INSERT IGNORE INTO LSU.Course (course_id, course_name, course_description) VALUES ('%s', '%s', '%s')" % (a, b, c))
for a, b, c in zip(df_stu['Courses 2'], df_stu['Course 2 Name'], df_stu['Course 2 Details']):
    cursor.execute("INSERT IGNORE INTO LSU.Course (course_id, course_name, course_description) VALUES ('%s', '%s', '%s')" % (a, b, c))
for a, b, c in zip(df_stu['Courses 3'], df_stu['Course 3 Name'], df_stu['Course 3 Details']):
    cursor.execute("INSERT IGNORE INTO LSU.Course (course_id, course_name, course_description) VALUES ('%s', '%s', '%s')" % (a, b, c))
    
for a, b, c, d in zip(df_stu['Courses 1'], df_stu['Course 1 Section'], df_stu['Course 1 Type'], df_stu['Course 1 Section Limit']):
    for e, f in zip(df_pro['Teaching'], df_pro['Team ID']):
        if e == a:
            cursor.execute("INSERT IGNORE INTO LSU.Sections (course_id, sec_no, section_type, limits, prof_team_id) VALUES ('%s', '%d', '%s', '%d', '%d')" % (a, b, c, d, f))
for a, b, c, d in zip(df_stu['Courses 2'], df_stu['Course 2 Section'], df_stu['Course 2 Type'], df_stu['Course 2 Section Limit']):
    for e, f in zip(df_pro['Teaching'], df_pro['Team ID']):
        if e == a:
            cursor.execute("INSERT IGNORE INTO LSU.Sections (course_id, sec_no, section_type, limits, prof_team_id) VALUES ('%s', '%d', '%s', '%d', '%d')" % (a, b, c, d, f))
for a, b, c, d in zip(df_stu['Courses 3'], df_stu['Course 3 Section'], df_stu['Course 3 Type'], df_stu['Course 3 Section Limit']):
    for e, f in zip(df_pro['Teaching'], df_pro['Team ID']):
        if e == a:
            cursor.execute("INSERT IGNORE INTO LSU.Sections (course_id, sec_no, section_type, limits, prof_team_id) VALUES ('%s', '%d', '%s', '%d', '%d')" % (a, b, c, d, f))

for a, b, c in zip(df_stu['Email'], df_stu['Courses 1'], df_stu['Course 1 Section']):
    cursor.execute("INSERT IGNORE INTO LSU.Enrolls (student_email, course_id, section_no) VALUES (%s, %s, %s)", (a, b, c))
for a, b, c in zip(df_stu['Email'], df_stu['Courses 2'], df_stu['Course 2 Section']):
    cursor.execute("INSERT IGNORE INTO LSU.Enrolls (student_email, course_id, section_no) VALUES (%s, %s, %s)", (a, b, c))
for a, b, c in zip(df_stu['Email'], df_stu['Courses 3'], df_stu['Course 3 Section']):
    cursor.execute("INSERT IGNORE INTO LSU.Enrolls (student_email, course_id, section_no) VALUES (%s, %s, %s)", (a, b, c))

for i in df_pro['Team ID'].values:
    cursor.execute("INSERT IGNORE INTO LSU.Prof_teams (team_id) VALUES('%d')" % (i))

for i, j in zip(df_pro['Team ID'].values, df_pro['Email'].values):
    cursor.execute("INSERT IGNORE INTO LSU.Prof_team_members (prof_email, team_id) VALUES('%s', '%d')" % (j, i))

for a, b, c, d in zip(df_stu['Courses 1'], df_stu['Course 1 Section'], df_stu['Course 1 HW_No'], df_stu['Course 1 HW_Details']):
    cursor.execute("INSERT IGNORE INTO LSU.Homework (course_id, sec_no, hw_no, hw_details) VALUES ('%s', '%s', '%d', '%s')" % (a, b, c, d))
for a, b, c, d in zip(df_stu['Courses 2'], df_stu['Course 2 Section'], df_stu['Course 2 HW_No'], df_stu['Course 2 HW_Details']):
    cursor.execute("INSERT IGNORE INTO LSU.Homework (course_id, sec_no, hw_no, hw_details) VALUES ('%s', '%s', '%d', '%s')" % (a, b, c, d))
for a, b, c, d in zip(df_stu['Courses 3'], df_stu['Course 3 Section'], df_stu['Course 3 HW_No'], df_stu['Course 3 HW_Details']):
    cursor.execute("INSERT IGNORE INTO LSU.Homework (course_id, sec_no, hw_no, hw_details) VALUES ('%s', '%s', '%d', '%s')" % (a, b, c, d))

for a, b, c, d, e in zip(df_stu['Email'], df_stu['Courses 1'], df_stu['Course 1 Section'], df_stu['Course 1 HW_No'], df_stu['Course 1 HW_Grade']):
    cursor.execute("INSERT IGNORE INTO LSU.Homework_grades (student_email, course_id, sec_no, hw_no, grade) VALUES (%s, %s, %s, %s, %s)" , (a, b, c, d, e))
for a, b, c, d, e in zip(df_stu['Email'], df_stu['Courses 2'], df_stu['Course 2 Section'], df_stu['Course 2 HW_No'], df_stu['Course 2 HW_Grade']):
    cursor.execute("INSERT IGNORE INTO LSU.Homework_grades (student_email, course_id, sec_no, hw_no, grade) VALUES (%s, %s, %s, %s, %s)" , (a, b, c, d, e))
for a, b, c, d, e in zip(df_stu['Email'], df_stu['Courses 3'], df_stu['Course 3 Section'], df_stu['Course 3 HW_No'], df_stu['Course 3 HW_Grade']):
    cursor.execute("INSERT IGNORE INTO LSU.Homework_grades (student_email, course_id, sec_no, hw_no, grade) VALUES (%s, %s, %s, %s, %s)" , (a, b, c, d, e))

for a, b, c, d in zip(df_stu['Courses 1'], df_stu['Course 1 Section'], df_stu['Course 1 EXAM_No'], df_stu['Course 1 Exam_Details']):
    cursor.execute("INSERT IGNORE INTO LSU.Exams (course_id, sec_no, exam_no, exam_details) VALUES ('%s', '%s', '%s', '%s')" % (a, b, c, d))
for a, b, c, d in zip(df_stu['Courses 2'], df_stu['Course 2 Section'], df_stu['Course 2 EXAM_No'], df_stu['Course 2 Exam_Details']):
    cursor.execute("INSERT IGNORE INTO LSU.Exams (course_id, sec_no, exam_no, exam_details) VALUES ('%s', '%s', '%s', '%s')" % (a, b, c, d))
for a, b, c, d in zip(df_stu['Courses 3'], df_stu['Course 3 Section'], df_stu['Course 3 EXAM_No'], df_stu['Course 3 Exam_Details']):
    cursor.execute("INSERT IGNORE INTO LSU.Exams (course_id, sec_no, exam_no, exam_details) VALUES ('%s', '%s', '%s', '%s')" % (a, b, c, d))

for a, b, c, d, e in zip(df_stu['Email'].values, df_stu['Courses 1'].values, df_stu['Course 1 Section'].values, df_stu['Course 1 EXAM_No'].values, df_stu['Course 1 EXAM_Grade'].values):
    cursor.execute("INSERT IGNORE INTO LSU.Exam_grades (student_email, course_id, sec_no, exam_no, grades) VALUES (%s, %s, %s, %s, %s)", (a, b, c, d, e))
for a, b, c, d, e in zip(df_stu['Email'].values, df_stu['Courses 2'].values, df_stu['Course 2 Section'].values, df_stu['Course 2 EXAM_No'].values, df_stu['Course 2 EXAM_Grade'].values):
    cursor.execute("INSERT IGNORE INTO LSU.Exam_grades (student_email, course_id, sec_no, exam_no, grades) VALUES (%s, %s, %s, %s, %s)", (a, b, c, d, e))
for a, b, c, d, e in zip(df_stu['Email'].values, df_stu['Courses 3'].values, df_stu['Course 3 Section'].values, df_stu['Course 3 EXAM_No'].values, df_stu['Course 3 EXAM_Grade'].values):
    cursor.execute("INSERT IGNORE INTO LSU.Exam_grades (student_email, course_id, sec_no, exam_no, grades) VALUES (%s, %s, %s, %s, %s)", (a, b, c, d, e))

arr = ['','','','','','','','','','','','','','','','','','']
num = 0
for a, b, c in zip(df_sec['course_id'], df_sec['sec_no'], df_sec['section_type']):
    if c == 'Cap':
        if a not in arr:
            arr[num] = a
            num = num + 1
for a, b, c in zip(df_sec['course_id'], df_sec['sec_no'], df_sec['section_type']):
        for d, e in zip(df_pro['Teaching'], df_pro['Email']):
            if d == a and c == 'Cap':
                cursor.execute("INSERT IGNORE INTO LSU.Capstone_section (course_id, sec_no, project_no, sponsor_id) VALUES ('%s', '%s', '%d', '%s')" % (a, b, arr.index(a) + 1, e))


n = 0
cursor.execute("SELECT course_id, sec_no, project_no FROM LSU.Capstone_section")
sec = cursor.fetchall()
for i in sec:
    n = n + 1
    cursor.execute("INSERT IGNORE INTO LSU.Capstone_Team (course_id, sec_no, team_id, project_no) VALUES ('%s', '%s', '%s', '%s')" % (i[0], i[1], n, i[2]))


cursor.execute("SELECT student_email, course_id, section_no FROM LSU.Enrolls")
enroll = cursor.fetchall()
cursor.execute("SELECT course_id, sec_no, team_id FROM LSU.Capstone_Team")
team = cursor.fetchall()
for i in enroll:
    for j in team:
        if i[1] == j[0] and i[2] == j[1]:
            cursor.execute("INSERT IGNORE INTO LSU.Capstone_Team_Members (student_email, team_id, course_id, sec_no) VALUES (%s, %s, %s, %s)" , (i[0], j[2], i[1], i[2]))


cursor.execute("SELECT course_id, sec_no, team_id FROM Capstone_Team")
grade = cursor.fetchall()
for i in grade:
    cursor.execute("INSERT IGNORE INTO LSU.Capstone_grades (course_id, sec_no, team_id, grade) VALUES ('%s', '%s', '%s', '%s')" % (i[0], i[1], i[2], None))


database.commit()


database.close()


