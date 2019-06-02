from flask import *
import MySQLdb as mysql
import hashlib

app = Flask(__name__)
app.secret_key = "pipi"
database = mysql.connect(host="localhost", port=3306, user="root", password="ll971220", db="LSU")
cursor = database.cursor()

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        Pro_email = request.form.get('Pro_name')
        Pro_password = hashlib.sha256(str(request.form.get('Pro_password')).encode('utf-8')).hexdigest()
        Stu_email = request.form.get('Stu_name')
        Stu_password = hashlib.sha256(str(request.form.get("Stu_password")).encode('utf-8')).hexdigest()

        if Pro_email == 'admin@lionstate.edu' or Stu_email == 'admin@lionstate.edu':       #administer login
            session['admin'] = "admin@lionstate.edu"
            return redirect(url_for('admin'))

        cursor.execute("SELECT email, password FROM LSU.Professor")
        result = cursor.fetchall()
        for professor in result:
            if Pro_email == professor[0] and Pro_password == professor[1]:
                session['pro_email'] = Pro_email
                return redirect(url_for('professor'))

        cursor.execute("SELECT Semail, Spassword FROM LSU.Student")
        result = cursor.fetchall()
        for student in result:
            if Stu_email == student[0] and Stu_password == student[1]:
                session['stu_email'] = Stu_email
                cursor.execute("SELECT s.Sname FROM LSU.student s WHERE s.Semail = '%s'" % (Stu_email))
                stu = cursor.fetchone()
                return redirect(url_for('student'))
                #return redirect(url_for("student_info"))
        return redirect(url_for('error'))

    return render_template('index.html')


@app.route('/student', methods=['POST', 'GET'])
def student():
    return render_template('Student.html')


@app.route('/student/student_info', methods=['POST', 'GET'])
def student_info():
    stu_email = session['stu_email']
    cursor.execute("SELECT s.Sname FROM LSU.student s WHERE s.Semail = '%s'" % (stu_email))
    stu = cursor.fetchone()
    real_name = stu[0]

    cursor.execute("SELECT * FROM LSU.Student WHERE Semail = '%s'"% (stu_email))
    stu_info = cursor.fetchall()

    ret = ""
    if request.method == 'POST':
        old_password = hashlib.sha256(str(request.form.get('old_password')).encode('utf-8')).hexdigest()
        new_password1 = hashlib.sha256(str(request.form.get('new_password1')).encode('utf-8')).hexdigest()
        new_password2 = hashlib.sha256(str(request.form.get("new_password2")).encode('utf-8')).hexdigest()

        cursor.execute("SELECT s.spassword FROM LSU.Student s WHERE s.semail = '%s'" % (stu_email))
        result = cursor.fetchone()
        password = result[0]
        if password == old_password:
            if new_password1 == new_password2:
                cursor.execute("UPDATE LSU.Student SET spassword = %s WHERE semail = %s", (new_password1, stu_email))
                database.commit()
                ret = "Your new password is confirmed!"
                flash("Your new password is confirmed!")
            else:
                ret = "Please confirm your new password."
                flash("Please confirm your new password.")
        else:
            ret = "Please check your password and try again."
            flash("Please check your password and try again.")

    return render_template('student_info.html', stu = real_name, ret =ret, stu_info=stu_info)


@app.route('/student/student_courses', methods=['POST', 'GET'])
def student_course():
    stu_email = session['stu_email']
    cursor.execute("SELECT s.Sname FROM LSU.student s WHERE s.Semail = '%s'" % (stu_email))
    stu = cursor.fetchone()
    real_name = stu[0]

    len_reg = cursor.execute("SELECT DISTINCT c.course_id, s.sec_no, c.course_description, p.name, p.email,p.office_address "
                             "FROM LSU.Sections s, LSU.Prof_team_members pt, LSU.Course c, LSU.Professor p, "
                             "LSU.Enrolls e "
                             "WHERE s.course_id = c.course_id AND "
                             "s.course_id = e.course_id AND "
                             "s.sec_no = e.section_no AND "
                             "s.section_type != %s AND "
                             "p.email = pt.prof_email AND "
                             "s.prof_team_id = pt.team_id AND "
                             "e.student_email = %s" , ('Cap', stu_email))
    reg_info = cursor.fetchall()

    len_cap = cursor.execute("SELECT DISTINCT c.course_id, s.sec_no, ct.team_id, c.course_description, p.name, p.email,p.office_address "
                             "FROM LSU.Sections s, LSU.Prof_team_members pt, LSU.Course c, LSU.Professor p, "
                             "LSU.Enrolls e , LSU.capstone_team_members ct "
                             "WHERE s.course_id = c.course_id AND "
                             "s.course_id = e.course_id AND "
                             "ct.course_id = s.course_id AND "
                             "ct.sec_no = s.sec_no AND "
                             "ct.student_email = e.student_email AND "
                             "s.sec_no = e.section_no AND "
                             "s.section_type = %s AND "
                             "p.email = pt.prof_email AND "
                             "s.prof_team_id = pt.team_id AND "
                             "e.student_email = %s" , ('Cap', stu_email))
    cap_info = cursor.fetchall()
    i = 0
    cap_team = [0]*10
    team_mem = [0]*10
    team_id = [0]*10
    team_mem_null = 1
    for row in cap_info:
        a = row[0]
        b = row[1]
        cursor.execute("SELECT team_id FROM lsu.capstone_team_members WHERE student_email = %s AND "
                           "course_id = %s AND sec_no = %s", (stu_email, a, b))
        stu_team = cursor.fetchone()[0]
        c = cursor.execute("SELECT team_id FROM lsu.capstone_team_members WHERE "
                           "course_id = %s AND sec_no = %s", (a, b))
        if c != 0:
            team_id[i] = cursor.fetchall()[0][0]
            team_mem[i] = cursor.execute(
                "SELECT  DISTINCT stu.sname, stu.semail, cap.team_id "
                "FROM LSU.student stu, LSU.Sections s, LSU.Course c, "
                "LSU.capstone_team_members cap "
                "WHERE stu.semail = cap.student_email AND s.course_id = c.course_id "
                "AND s.course_id = cap.course_id AND "
                "s.sec_no = cap.sec_no AND "
                "s.course_id = %s AND "
                "stu.sname != %s AND "
                "s.sec_no = cap.sec_no  AND "
                "s.sec_no = %s AND cap.team_id = %s", (a, real_name, b, stu_team))
            cap_temp = cursor.fetchall()
            if cap_temp not in cap_team:
                cap_team[i] = cap_temp
                i = i + 1
            team_mem_null = 0

    cursor.execute("SELECT h.course_id, h.sec_no, h.hw_no, h.hw_details, hg.grade "
                   "FROM LSU.homework_grades hg, LSU.homework h "
                   "WHERE hg.student_email = '%s' AND hg.course_id = h.course_id AND "
                   "hg.sec_no = h.sec_no AND hg.hw_no = h.hw_no" %(stu_email))
    all_homeworks = cursor.fetchall()

    class_homework_grades = [0] * 100
    a = 0
    for row in all_homeworks:
        cursor.execute("SELECT DISTINCT hg.course_id, hg.sec_no, hg.hw_no, AVG(hg.grade), MAX(hg.grade), MIN(hg.grade) FROM  LSU.homework_grades hg WHERE hg.course_id = %s AND hg.sec_no = %s GROUP BY hg.hw_no", (row[0], row[1]))
        grade = cursor.fetchall()
        if grade not in class_homework_grades:
            class_homework_grades[a] = grade
            a = a + 1

    cursor.execute("SELECT e.course_id, e.sec_no, e.exam_no, e.exam_details, eg.grades "
                   "FROM LSU.exam_grades eg, LSU.exams e "
                   "WHERE eg.student_email = %s AND eg.course_id = e.course_id AND "
                   "eg.sec_no = e.sec_no AND eg.exam_no = e.exam_no AND e.exam_details != %s" ,(stu_email, 'nan'))
    all_exams = cursor.fetchall()
    class_exam_grades = [0] * 100
    b = 0
    for row in all_exams:
        cursor.execute("SELECT eg.course_id, eg.sec_no, AVG(eg.grades), MAX(eg.grades), MIN(eg.grades) "
                       "FROM  LSU.Exam_grades eg "
                       "WHERE eg.course_id = %s AND eg.sec_no = %s ", (row[0], row[1]))
        class_exam_grades[b] = cursor.fetchone()
        b = b + 1

    cursor.execute("SELECT cg.course_id, cg.sec_no, cg.team_id, cg.grade "
                   "FROM lsu.capstone_grades cg, lsu.enrolls e "
                   "WHERE e.course_id = cg.course_id AND e.section_no = cg.sec_no AND "
                   "e.student_email = '%s' " % (stu_email))
    stu_cap_grade = cursor.fetchall()

    cursor.execute("SELECT h.course_id, h.sec_no, SUM(h.grade), COUNT(h.grade) "
                   "FROM  lsu.homework_grades h "
                   "WHERE  h.student_email = '%s' "
                   "GROUP BY h.course_id, h.sec_no" % (stu_email))
    stu_homework_grade = cursor.fetchall()

    cursor.execute("SELECT e.course_id, e.sec_no, SUM(e.grades), COUNT(e.grades) "
                   "FROM  lsu.exam_grades e "
                   "WHERE  e.student_email = '%s' "
                   "GROUP BY e.course_id, e.sec_no" % (stu_email))
    stu_exam_grade = cursor.fetchall()


    letter_grade = []
    for row in stu_homework_grade:
        for row2 in stu_exam_grade:
            if row[0] == row2[0] and row[1] == row2[1]:
                if row2[2] == 0:
                    for row3 in stu_cap_grade:
                        if row[0] == row3[0] and row[1] == row3[1]:
                            if row3[3]!=0 and row[3]!=0:
                                x = row[2]/row[3]/2
                                y = row3[3]/2
                                z = float(x) + float(y)
                                if z >= 90:
                                    letter = 'A'
                                elif z >= 80:
                                    letter = 'B'
                                elif z >= 70:
                                    letter = 'C'
                                elif z >= 60:
                                    letter = 'D'
                                else:
                                    letter = 'F'


                                letter_grade.append([row[0], row[1], letter])
                else:
                    x = row[2] / row[3] / 2
                    y = row2[2] / 2 # / row2[3] / 2
                    z = float(x) + float(y)
                    if z > 90:
                        letter = 'A'
                    elif z > 80:
                        letter = 'B'
                    elif z > 70:
                        letter = 'C'
                    elif z > 60:
                        letter = 'D'
                    else:
                        letter = 'F'

    return render_template('Student_class.html',  stu = real_name, reg=reg_info, cap=cap_info, len_cap = len_cap,
                           len_reg = len_reg, cap_team = cap_team, i = i, team_mem = team_mem, team_id = team_id,
                           team_mem_null = team_mem_null, all_exams = all_exams, all_homeworks = all_homeworks,
                           stu_cap_grade = stu_cap_grade, class_homework_grades = class_homework_grades, a = a,
                           class_exam_grades = class_exam_grades, b = b, letter_grade = letter_grade)



@app.route('/admin', methods=['POST', 'GET'])
def admin():
    admin = session['admin']
    return render_template('admin.html')


@app.route('/admin/manage', methods=['POST', 'GET'])
def manage():
    admin = session['admin']
    cursor.execute("SELECT s.course_id, c.course_name, s.sec_no, s.section_type, s.limits, p.name, p.email "
                   "FROM LSU.Professor p, LSU.Course c, LSU.sections s, LSU.Prof_team_members pt "
                   "WHERE p.email = pt.prof_email AND c.course_id = s.course_id AND s.prof_team_id = pt.team_id")
    course = cursor.fetchall()
    cursor.execute("SELECT p.name, pt.team_id FROM LSU.Professor p, LSU.prof_team_members pt WHERE pt.prof_email = p.email")
    pro = cursor.fetchall()

    cursor.execute("SELECT s.course_id, s.sec_no "
                   "FROM LSU.sections s "
                   "WHERE s.prof_team_id IN"
                   "    (SELECT s.prof_team_id"
                   "    FROM LSU.sections s"
                   "    GROUP BY s.prof_team_id "
                   "    HAVING COUNT(s.prof_team_id) > 1);")
    sec = cursor.fetchall()

    cursor.execute("SELECT s.course_id, s.sec_no "
                   "FROM LSU.sections s "
                   "WHERE s.sec_no != 0")
    all_Sec = cursor.fetchall()

    cursor.execute("SELECT s.sname, s.semail FROM LSU.Student s")
    stu = cursor.fetchall()

    cursor.execute("SELECT s.course_id, s.sec_no, p.email "
                   "FROM LSU.Sections s, LSU.Prof_team_members pt, LSU.professor p "
                   "WHERE pt.team_id = s.prof_team_id AND p.email = pt.prof_email "
                   "AND s.section_type = '%s'" % ('Cap'))
    Cap_professors = cursor.fetchall()

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        course_name = request.form.get('course_name')
        course_description = request.form.get('course_description')
        sec_no = request.form.get('sec_no')
        Stype = request.form.get('type')
        course_limit = request.form.get('course_limit')
        team_id = request.form.get('pro')
        drop = request.form.get('drop')
        student = request.form.get('student')
        course_select = request.form.get('course_select')
        project_id = request.form.get('project_id')
        Assign_project = request.form.get('Assign_project')
        course_info = request.form.get('course_info')

        if request.form.get('add') == 'add':
            if Stype != "null" and pro != "null":
                if Stype == 'Reg':
                    cursor.execute("INSERT IGNORE INTO LSU.Course VALUES(%s, %s, %s)",
                                   (course_id, course_name, course_description))
                    b1 = cursor.execute("INSERT IGNORE INTO LSU.Sections VALUES(%s,%s,%s,%s,%s)",
                                        (course_id, sec_no, Stype, course_limit, team_id))
                    if b1 != 0:
                        flash("The course " + course_name+ " has been added!")
                    else:
                        flash("The course has already exist")
                elif Stype == 'Cap':
                    cursor.execute("INSERT IGNORE INTO LSU.Course VALUES(%s, %s, %s)",
                                   (course_id, course_name, course_description))
                    b1 = cursor.execute("INSERT IGNORE INTO LSU.Sections VALUES(%s,%s,%s,%s,%s)",
                                        (course_id, sec_no, Stype, course_limit, team_id))

                    if b1 != 0:
                        flash("The course " + course_name + " has been added!")
                    else:
                        flash("The course has already exist")

                database.commit()
                return redirect(url_for('manage'))
            else:
                flash("Please select a valid professor and type")

        if Assign_project == 'Assign':
            if course_info != 'null':
                course_infoarr = course_info.split('#', 2)
                course_id = course_infoarr[0]
                sec_no = course_infoarr[1]
                pro_email = course_infoarr[2]
                if project_id != '0':
                    a = cursor.execute("INSERT IGNORE INTO LSU.capstone_section VALUES(%s, %s, %s, %s)", (course_id, sec_no, project_id, pro_email))
                    if a != 0:
                        flash("The project " + project_id + " has been added successfully!")
                        database.commit()
                    else:
                        flash("The project " + project_id + " already existed.")
            else:
                flash("Please select a valid section")

        if request.form.get('remove') == 'remove':
            if drop != 'null':
                droparr = drop.split('#', 1)
                drop_course = droparr[0]
                drop_sec = droparr[1]
                cursor.execute("SELECT s.prof_team_id FROM LSU.sections s "
                               "WHERE s.course_id = %s AND s.sec_no = %s",
                               (drop_course, drop_sec))
                drop_pro = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM LSU.Sections WHERE prof_team_id = '%s'"%
                               (drop_pro))
                d = cursor.fetchone()[0]
                if d == 1:
                    cursor.execute("DELETE FROM LSU.Course WHERE course_id = '%s'"%(drop_course))

                c = cursor.execute("DELETE FROM LSU.Sections WHERE course_id = %s AND sec_no = %s", (drop_course, drop_sec))

                cursor.execute("DELETE FROM LSU.enrolls WHERE course_id = %s AND section_no = %s",
                                   (drop_course, drop_sec))
                cursor.execute("DELETE FROM LSU.Homework_grades WHERE course_id = %s AND sec_no = %s",
                               (drop_course, drop_sec))
                cursor.execute("DELETE FROM LSU.Exam_grades WHERE course_id = %s AND sec_no = %s",
                               (drop_course, drop_sec))
                cursor.execute("DELETE FROM LSU.capstone_grades WHERE course_id = %s AND sec_no = %s",
                               (drop_course, drop_sec))
                cursor.execute("DELETE FROM LSU.capstone_section WHERE course_id = %s AND sec_no = %s",
                               (drop_course, drop_sec))
                cursor.execute("DELETE FROM LSU.capstone_team WHERE course_id = %s AND sec_no = %s",
                               (drop_course, drop_sec))
                cursor.execute("DELETE FROM LSU.capstone_team_members WHERE course_id = %s AND sec_no = %s",
                               (drop_course, drop_sec))

                database.commit()
                if c != 0:
                    flash("The course " + drop_course + " has been removed!")
                else:
                    flash("There is no such Course: " + drop_course)
                return redirect(url_for('manage'))
            else:
                flash("Please select a valid course")

        if request.form.get('enroll') == 'enroll':
            if course_select != 'null' and student != 'null':
                course_selectarr = course_select.split('#', 1)
                enroll_course =course_selectarr[0]
                enroll_sec = course_selectarr[1]
                cursor.execute("SELECT COUNT(*) FROM LSU.enrolls WHERE course_id = %s AND section_no = %s", (enroll_course, enroll_sec))
                enroll_now = cursor.fetchone()[0]
                cursor.execute("SELECT limits FROM LSU.sections WHERE course_id = %s AND sec_no = %s", (enroll_course, enroll_sec))
                total_limit = cursor.fetchone()[0]
                if total_limit > enroll_now:
                    a = 0
                    b = 0
                    c = 0
                    a = cursor.execute("INSERT IGNORE INTO LSU.enrolls VALUES(%s, %s, %s)", (student, enroll_course,enroll_sec))
                    b = cursor.execute("INSERT IGNORE INTO LSU.Homework_grades VALUES(%s, %s, %s, %s, %s)", (student, enroll_course,enroll_sec, '1', '0'))
                    cursor.execute("SELECT section_type FROM LSU.sections WHERE course_id = %s AND sec_no = %s", (enroll_course, enroll_sec))
                    d = cursor.fetchone()[0]
                    if d == 'Cap':
                        c = cursor.execute("INSERT IGNORE INTO LSU.Exam_grades VALUES(%s, %s, %s, %s, %s)",
                                           (student, enroll_course, enroll_sec, '0', '0'))
                        cursor.execute("INSERT IGNORE INTO LSU.enrolls VALUES(%s, %s, %s)",
                                       (student, enroll_course, enroll_sec))
                        cursor.execute("INSERT IGNORE INTO LSU.capstone_team_members VALUES(%s, %s, %s, %s)",
                                       (student, 'null', enroll_course, enroll_sec))
                    else:
                        c = cursor.execute("INSERT IGNORE INTO LSU.Exam_grades VALUES(%s, %s, %s, %s, %s)", (student, enroll_course,enroll_sec, '1', '0'))
                    database.commit()
                    if a!= 0 and b!= 0 and c!=0:
                        flash("The student has been enrolled successfully in "+enroll_course)
                    else:
                        flash("The student has already been in this course.")
                else:
                    flash("The course is full, enroll failed")
            else:
                flash("Please select a valid student and a course")

    return render_template('manage.html', course = course, pro = pro, sec =sec, stu=stu, all_Sec = all_Sec,
                           Cap_professors = Cap_professors)


@app.route('/Professor', methods=['POST', 'GET'])
def professor():
    pro_email = session['pro_email']
    return render_template('Professor.html')


@app.route('/Professor/Pro_info', methods=['POST', 'GET'])
def professor_info():
    pro_email = session['pro_email']
    cursor.execute("SELECT name FROM LSU.Professor WHERE email = '%s'" % (pro_email))
    pro_name = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM LSU.Professor WHERE email = '%s'"% (pro_email))
    pro_info = cursor.fetchall()

    ret = ""
    if request.method == 'POST':
        old_password = hashlib.sha256(str(request.form.get('pro_old_password')).encode('utf-8')).hexdigest()
        new_password1 = hashlib.sha256(str(request.form.get('pro_new_password1')).encode('utf-8')).hexdigest()
        new_password2 = hashlib.sha256(str(request.form.get("pro_new_password2")).encode('utf-8')).hexdigest()

        cursor.execute("SELECT password FROM LSU.professor WHERE email = '%s'" % (pro_email))
        password = cursor.fetchone()[0]
        if password == old_password:
            if new_password1 == new_password2:
                cursor.execute("UPDATE LSU.Professor SET password = %s WHERE email = %s", (new_password1, pro_email))
                database.commit()
                ret = "Your new password is confirmed!"
                flash("Your new password is confirmed!")
            else:
                ret = "Please confirm your new password."
                flash("Please confirm your new password.")
        else:
            ret = "Please check your password and try again."
            flash("Please check your password and try again.")

    return render_template('Pro_info.html', pro_name = pro_name, pro_info = pro_info, ret = ret)


@app.route('/Professor/Pro_manage', methods=['POST', 'GET'])
def pro_manage():
    pro_email = session['pro_email']
    cursor.execute("SELECT name FROM LSU.Professor WHERE email = '%s'" % (pro_email))
    pro_name = cursor.fetchone()[0]
    cursor.execute("SELECT s.course_id, c.course_name, s.sec_no, s.section_type, s.limits "
                   "FROM LSU.Course c, LSU.Sections s, LSU.Prof_team_members p "
                   "WHERE c.course_id = s.course_id AND s.prof_team_id = p.team_id AND"
                   "      p.prof_email = '%s'" % (pro_email))
    pro_course = cursor.fetchall()

    cursor.execute("SELECT s.course_id, s.sec_no FROM LSU.Sections s, LSU.prof_team_members p "
                   "WHERE s.prof_team_id = p.team_id AND p.prof_email = '%s'" % (pro_email))
    all_sec = cursor.fetchall()
    stu_in_course = [0]*100
    all_homeworks = [0]*100
    all_exams = [0]*100
    i = 0
    for row in all_sec:
        cursor.execute("SELECT st.sname, st.semail, s.course_id, s.sec_no "
                       "FROM LSU.Student st, LSU.Sections s, LSU.Enrolls e, LSU.Prof_team_members pt "
                       "WHERE st.semail = e.student_email AND s.course_id = e.course_id AND "
                       "s.sec_no = e.section_no AND s.prof_team_id = pt.team_id AND pt.prof_email = %s AND "
                       "s.course_id = %s AND s.sec_no = %s" , (pro_email, row[0], row[1]))
        stu_in_course[i] = cursor.fetchall()
        cursor.execute("SELECT s.sname, hg.course_id, hg.sec_no, hg.hw_no, hg.grade "
                       "FROM LSU.student s, LSU.homework_grades hg, LSU.homework h "
                       "WHERE hg.course_id = h.course_id AND hg.sec_no = h.sec_no AND hg.hw_no = h.hw_no AND s.semail = hg.student_email AND "
                       "hg.course_id = %s AND hg.sec_no = %s", (row[0], row[1]))
        all_homeworks[i] = cursor.fetchall()
        cursor.execute("SELECT s.sname, eg.course_id, eg.sec_no, eg.exam_no, eg.grades "
                       "FROM LSU.student s, LSU.exam_grades eg, LSU.exams e "
                       "WHERE eg.course_id = e.course_id AND eg.sec_no = e.sec_no AND eg.exam_no = e.exam_no AND s.semail = eg.student_email AND "
                       "eg.course_id = %s AND eg.sec_no = %s", (row[0], row[1]))
        all_exams[i] = cursor.fetchall()
        i = i + 1

    cursor.execute("SELECT  DISTINCT st.sname, st.semail FROM LSU.Student st, LSU.Sections s, LSU.Enrolls e, LSU.Prof_team_members p WHERE st.semail = e.student_email AND s.course_id = e.course_id AND s.sec_no = e.section_no AND s.prof_team_id = p.team_id AND p.prof_email = '%s'" % (pro_email))
    stu_in_pro = cursor.fetchall()

    cursor.execute("SELECT s.course_id, s.sec_no "
                   "FROM LSU.Sections s, LSU.Prof_team_members p "
                   "WHERE p.team_id = s.prof_team_id AND p.prof_email = '%s'" %(pro_email))
    course_pro = cursor.fetchall()

    cursor.execute("SELECT s.course_id, s.sec_no, hw_no "
                   "FROM LSU.Sections s, LSU.Prof_team_members p, LSU.Homework h "
                   "WHERE p.team_id = s.prof_team_id AND "
                   "s.course_id = h.course_id AND h.sec_no = s.sec_no AND p.prof_email = '%s'" %(pro_email))
    course_hw = cursor.fetchall()

    cursor.execute("SELECT s.course_id, s.sec_no, e.exam_no "
                   "FROM LSU.Sections s, LSU.Prof_team_members p, LSU.exams e "
                   "WHERE p.team_id = s.prof_team_id AND "
                   "s.course_id = e.course_id AND e.sec_no = s.sec_no AND p.prof_email = '%s'" % (pro_email))
    course_exam = cursor.fetchall()

    cursor.execute("SELECT DISTINCT s.sname, s.semail "
                   "FROM LSU.Student s, LSU.sections sc, LSU.Enrolls e, LSU.Prof_team_members p "
                   "WHERE s.semail = e.student_email AND sc.course_id = e.course_id AND "
                   "sc.sec_no = e.section_no AND sc.prof_team_id = p.team_id AND "
                   "sc.section_type = %s AND p.prof_email = %s", ('Cap', pro_email))
    stu_in_cap = cursor.fetchall()

    cursor.execute("SELECT s.course_id, s.sec_no "
                   "FROM LSU.Sections s, LSU.Prof_team_members p "
                   "WHERE p.team_id = s.prof_team_id AND p.prof_email = %s AND "
                   "s.section_type = %s" , (pro_email, 'Cap'))
    Cap_course_pro = cursor.fetchall()

    cursor.execute("SELECT DISTINCT project_no FROM LSU.Capstone_section WHERE sponsor_id = '%s'" % (pro_email))
    project_no_pro = cursor.fetchall()

    cursor.execute("SELECT DISTINCT ct.team_id "
                    "FROM LSU.capstone_team ct, LSU.Capstone_section cs "
                    "WHERE cs.course_id = ct.course_id AND cs.sec_no = ct.sec_no AND cs.sponsor_id = '%s'" % (pro_email))
    pro_Cap_team = cursor.fetchall()

    cursor.execute("SELECT s.course_id, s.sec_no, ct.team_id "
                   "FROM LSU.Sections s, LSU.Prof_team_members p, LSU.capstone_team ct, LSU.Capstone_section cs "
                   "WHERE p.team_id = s.prof_team_id AND p.prof_email = %s AND "
                   "cs.course_id = ct.course_id AND cs.sec_no = ct.sec_no AND "
                   "cs.course_id = s.course_id AND cs.sec_no = s.sec_no AND "
                   "ct.project_no = cs.project_no AND "
                   "s.section_type = %s", (pro_email, 'Cap'))
    Pro_team_sec = cursor.fetchall()

    cursor.execute("SELECT DISTINCT g.course_id, g.sec_no, g.team_id, g.grade "
                   "FROM lsu.capstone_grades g, lsu.capstone_section s "
                   "WHERE g.course_id = s.course_id AND g.sec_no = s.sec_no AND "
                   "s.sponsor_id = '%s'" % (pro_email))
    Cap_grade = cursor.fetchall()

    if request.method == 'POST':
        course_info = request.form.get('course')
        hw_description = request.form.get('hw_description')
        hw_no = request.form.get('hw_number')
        add_homework = request.form.get('add_homework')
        exam_description = request.form.get('exam_description')
        exam_no = request.form.get('exam_number')
        add_Exam = request.form.get('add_Exam')
        submit_homework = request.form.get('submit_homework')
        hw_grade = request.form.get('hw_grade')
        choose_student = request.form.get('choose_student')
        addScore = request.form.get('addScore')
        submit_exam = request.form.get('submit_exam')
        addExScore = request.form.get('addExScore')
        exam_grade = request.form.get('exam_grade')
        Ex_choose_student = request.form.get('Ex_choose_student')
        checkStu = request.form.getlist('checkStu')
        addToTeam = request.form.get('addToTeam')
        course_add_team = request.form.get('course_add_team')
        team_id = request.form.get('team_id')
        addTeamID = request.form.get('addTeamID')
        project_no = request.form.get('project_no')
        team_info = request.form.get('team_info')
        addCapScore = request.form.get('addCapScore')
        cap_team_info = request.form.get('cap_team_info')
        cap_grade = request.form.get('cap_grade')


        if add_homework == 'Add Homework':
            if course_info != 'null':
                course_infoarr = course_info.split('#', 1)
                hw_course_id = course_infoarr[0]
                hw_sec = course_infoarr[1]
                a = cursor.execute("INSERT IGNORE INTO LSU.homework VALUES(%s, %s, %s, %s)", (hw_course_id, hw_sec, hw_no, hw_description))
                if a != 0:
                    cursor.execute(
                        "SELECT e.student_email FROM LSU.Enrolls e WHERE e.course_id = %s AND e.section_no = %s",
                        (hw_course_id, hw_sec))
                    all_stu = cursor.fetchall()
                    for stu in all_stu:
                        cursor.execute("INSERT IGNORE INTO LSU.homework_grades VALUES(%s, %s, %s, %s, %s)", (stu[0], hw_course_id,hw_sec,hw_no, '0'))
                    flash("The new homework has been added successfully")
                    database.commit()
                else:
                    flash("The homework have already exited")
            else:
                flash("Please select a valid course")
            return redirect(url_for('pro_manage'))

        if add_Exam == 'Add Exam':
            if course_info != 'null':
                course_infoarr = course_info.split('#', 1)
                exam_course_id = course_infoarr[0]
                exam_sec = course_infoarr[1]
                a = cursor.execute("INSERT IGNORE INTO LSU.exams VALUES(%s, %s, %s, %s)",
                                   (exam_course_id, exam_sec, exam_no, exam_description))
                if a != 0:
                    cursor.execute(
                        "SELECT e.student_email FROM LSU.Enrolls e WHERE e.course_id = %s AND e.section_no = %s",
                        (exam_course_id, exam_sec))
                    all_stu = cursor.fetchall()
                    for stu in all_stu:
                        cursor.execute("INSERT IGNORE INTO LSU.exam_grades VALUES(%s, %s, %s, %s, %s)",
                                       (stu[0], exam_course_id,exam_sec,exam_no, '0'))
                    flash("The new Exam has been added successfully")
                    database.commit()
                else:
                    flash("The Exam have already exited")
            else:
                flash("Please select a valid course")

            return redirect(url_for('pro_manage'))

        if addScore == 'Add Homework Score':
            if submit_homework != 'null' and choose_student != 'null':
                hw_gradearr = submit_homework.split('#', 2)
                hw_score_course_id = hw_gradearr[0]
                hw_score_sec = hw_gradearr[1]
                hw_score_num = hw_gradearr[2]
                choose_studentarr = choose_student.split('#', 1)
                stu_name = choose_studentarr[1]
                stu_email = choose_studentarr[0]
                a = cursor.execute("UPDATE LSU.homework_grades SET grade = %s WHERE course_id = %s AND "
                                   "sec_no = %s AND hw_no = %s AND student_email = %s",
                                   (hw_grade, hw_score_course_id, hw_score_sec, hw_score_num, stu_email ))
                if a == 1:
                    flash("The score is submitted!")
                    database.commit()
                else:
                    flash("The student " + stu_name +" is not in " + hw_score_course_id + " section " + hw_score_sec)
            else:
                flash("Please select a valid homework and a student")
            return redirect(url_for('pro_manage'))

        if addExScore == 'Add Exam Score':
            if submit_exam != 'null' and Ex_choose_student != 'null':
                submit_examarr = submit_exam.split('#', 2)
                hw_score_course_id = submit_examarr[0]
                hw_score_sec = submit_examarr[1]
                hw_score_num = submit_examarr[2]
                Ex_choose_studentarr = Ex_choose_student.split('#', 1)
                stu_name = Ex_choose_studentarr[1]
                stu_email = Ex_choose_studentarr[0]
                a = cursor.execute("UPDATE LSU.exam_grades SET grades = %s WHERE course_id = %s AND sec_no = %s AND exam_no = %s AND student_email = %s",
                                   (exam_grade, hw_score_course_id, hw_score_sec, hw_score_num, stu_email ))
                if a == 1:
                    flash("The score is submitted!")
                    database.commit()
                else:
                    flash("The student " + stu_name +" is not in " + hw_score_course_id + " section " + hw_score_sec)
            else:
                flash("Please select a valid exam and a student")
            return redirect(url_for('pro_manage'))

        if addTeamID ==  'Add Team ID':
            if course_add_team != 'null' and project_no != 'null':
                course_add_teamarr = course_add_team.split('#', 1)
                course_id = course_add_teamarr[0]
                sec_no = course_add_teamarr[1]
                a = cursor.execute("INSERT IGNORE INTO LSU.capstone_team VALUES (%s, %s, %s, %s)", (course_id, sec_no, team_id, project_no))
                b = cursor.execute("INSERT IGNORE INTO LSU.capstone_grades VALUES (%s, %s, %s, %s)", (course_id, sec_no, team_id, '0'))
                if a != 0 and b != 0:
                    flash("The team #" + team_id + " has been added successfully!")
                    database.commit()
                else:
                    flash("The team #" + team_id + " already exists.")
            else:
                flash("Please select a project.")
            return redirect(url_for('pro_manage'))

        if addToTeam == 'Add':
            if len(checkStu) != 0:
                if team_info != 'null':
                    team_infoarr = team_info.split('#', 2)
                    course_id = team_infoarr[0]
                    sec_no = team_infoarr[1]
                    team_no = team_infoarr[2]
                    for student_email in checkStu:
                        a = cursor.execute("UPDATE lsu.capstone_team_members SET team_id = %s "
                                           "WHERE student_email = %s AND course_id = %s AND sec_no = %s",
                                            (team_no, student_email, course_id, sec_no))
                        cursor.execute("SELECT sname FROM LSU.student WHERE semail = '%s'" % (student_email))
                        name = cursor.fetchone()[0]
                        if a == 1:
                            flash("The student " + name + " has been added to team " + team_no + " in course " + course_id + " section: " + sec_no)
                            database.commit()
                        else:
                            flash("The student " + name + " is not in course " + course_id + " section: " + sec_no +
                                  ". Or the student is already in the team.")
                else:
                    flash("Please select a valid team")
            else:
                flash("Please select at least one student")
            return redirect(url_for('pro_manage'))

        if addCapScore == 'Submit':
            if cap_team_info != 'null':
                cap_team_infoarr = cap_team_info.split('#', 2)
                course_id = cap_team_infoarr[0]
                sec_no = cap_team_infoarr[1]
                team_no = cap_team_infoarr[2]
                a = cursor.execute("UPDATE LSU.capstone_grades SET grade = %s "
                                   "WHERE team_id = %s AND course_id = %s AND sec_no = %s",
                                   (cap_grade, team_no, course_id, sec_no))
                if a == 1:
                    flash(
                        "The team " + team_no + " in course " + course_id + " section: " + sec_no+ " has been graded. The grade is " + cap_grade )
                    database.commit()
                else:
                    flash("The team " + team_no + " in course " + course_id + " section: " + sec_no + " is not exist")
            else:
                flash("Please select a valid team")
            return redirect(url_for('pro_manage'))

    return render_template('Pro_manage.html', pro_name = pro_name, pro_course = pro_course,
                           stu_in_course = stu_in_course, i = i, course_pro = course_pro,
                           all_homeworks = all_homeworks, all_exams = all_exams, course_hw = course_hw,
                           stu_in_pro = stu_in_pro, course_exam = course_exam, stu_in_cap = stu_in_cap,
                           Cap_course_pro = Cap_course_pro, project_no_pro = project_no_pro,
                           pro_Cap_team = pro_Cap_team, Pro_team_sec = Pro_team_sec, Cap_grade = Cap_grade)


@app.route('/Error', methods=['POST', 'GET'])
def error():
    return render_template('Error.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('stu_email', None)
    session.pop('admin', None)
    session.pop('pro_email', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)