import os
import sqlite3

# poistaa tietokannan alussa (kätevä moduulin testailussa)
os.remove("courses.db")

db = sqlite3.connect("courses.db")
db.isolation_level = None

# luo tietokantaan tarvittavat taulut
def create_tables():

    # teacher: id, name
    db.execute('''
    CREATE TABLE Teachers (
    id INTEGER PRIMARY KEY,
    name TEXT
    )
    ''')

    # student: name
    db.execute('''
    CREATE TABLE Students (
    id INTEGER PRIMARY KEY,
    name TEXT
    )
    ''')

    # course: name, credits
    db.execute('''
    CREATE TABLE Courses (
    id INTEGER PRIMARY KEY,
    name TEXT,
    credits INTEGER
    )
    ''')

    # credits: student_id, course_id, date, grade
    db.execute('''
    CREATE TABLE Credits (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    course_id INTEGER,
    date TEXT,
    grade INTEGER
    )
    ''')

    # TeacherCourses: teacher_id, course_id
    db.execute('''
    CREATE TABLE TeacherCourses (
    id INTEGER PRIMARY KEY,
    teacher_id INTEGER,
    course_id INTEGER
    )
    ''')

    # group: name
    db.execute('''
    CREATE TABLE Groups (
    id INTEGER PRIMARY KEY,
    name TEXT
    )
    ''')

    # TeachersInGroup: teacher_id, group_id
    db.execute('''
    CREATE TABLE TeachersInGroup (
    id INTEGER PRIMARY KEY,
    teacher_id INTEGER,
    group_id INTEGER
    )
    ''')

    # StudentsInGroup: student_id, group_id
    db.execute('''
    CREATE TABLE StudentsInGroup (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    group_id INTEGER
    )
    ''')




# lisää opettajan tietokantaan
def create_teacher(name):
    cur = db.execute('''
    INSERT INTO Teachers (name) VALUES (?)
    ''', [name])
    id = cur.lastrowid
    return id

# lisää kurssin tietokantaan
def create_course(name, credits, teacher_ids):
    cur = db.execute('''
    INSERT INTO Courses (name, credits) VALUES (?,?)
    ''', [name, credits])
    course_id = cur.lastrowid
    for teacher_id in teacher_ids:
        db.execute('''
        INSERT INTO TeacherCourses (teacher_id, course_id) VALUES (?, ?)
        ''', [teacher_id, course_id])
    return course_id

# lisää opiskelijan tietokantaan
def create_student(name):
    cur = db.execute('''
    INSERT INTO Students (name) VALUES (?)
    ''', [name])
    id = cur.lastrowid
    return id

# antaa opiskelijalle suorituksen kurssista
# huom. credits format = student_id, course_id, date, grade
def add_credits(student_id, course_id, date, grade):
    cur = db.execute('''
    INSERT INTO Credits (student_id, course_id, date, grade) VALUES (?,?,?,?)
    ''', [student_id, course_id, date, grade])
    id = cur.lastrowid
    return id

# lisää ryhmän tietokantaan
def create_group(name, teacher_ids, student_ids):
    cur = db.execute('''
    INSERT INTO Groups (name) VALUES (?)
    ''', [name])
    group_id = cur.lastrowid
    for teacher_id in teacher_ids:
        db.execute('''
        INSERT INTO TeachersInGroup (teacher_id, group_id) VALUES (?,?)
        ''', [teacher_id, group_id])
    for student_id in student_ids:
        db.execute('''
        INSERT INTO StudentsInGroup (student_id, group_id) VALUES (?,?)
        ''', [student_id, group_id])
    return group_id

# hakee kurssit, joissa opettaja opettaa (aakkosjärjestyksessä)
def courses_by_teacher(teacher_name):
    courses = db.execute('''
    SELECT C.name
    FROM Courses C, Teachers T, TeacherCourses TC
    WHERE
    C.id = TC.course_id AND
    T.id = TC.teacher_id AND
    T.name = ?
    GROUP BY
    C.name
    ORDER BY
    C.name
    ''', [teacher_name]).fetchall()
    courses = [c[0] for c in courses]
    return courses

# hakee opettajan antamien opintopisteiden määrän
def credits_by_teacher(teacher_name):
    credits = db.execute('''
    SELECT
        SUM(IFNULL(Courses.credits,0))
    FROM
        Teachers T
        LEFT JOIN TeacherCourses TC ON T.id = TC.teacher_id
        LEFT JOIN Credits ON TC.course_id = Credits.course_id
        LEFT JOIN Courses ON Courses.id = Credits.course_id
    WHERE
        T.name = ?
    ''', [teacher_name]).fetchone()[0]
    return credits

# hakee opiskelijan suorittamat kurssit arvosanoineen (aakkosjärjestyksessä)
def courses_by_student(student_name):
    courses = db.execute('''
    SELECT Courses.name, Credits.grade
    FROM Courses, Credits, Students S
    WHERE
    Courses.id = Credits.course_id AND
    S.id = Credits.student_id AND
    S.name = ?
    GROUP BY
    Courses.name
    ORDER BY
    Courses.name
    ''', [student_name]).fetchall()
    return courses

# hakee tiettynä vuonna saatujen opintopisteiden määrän
def credits_by_year(year):
    credits = db.execute('''
    SELECT SUM(IFNULL(Courses.credits,0))
    FROM
        Courses LEFT JOIN Credits ON Courses.id = Credits.course_id
    WHERE
        SUBSTR(Credits.date,1,4) = ?
    ''', [str(year)]).fetchone()[0]
    return credits

# hakee kurssin arvosanojen jakauman (järjestyksessä arvosanat 1-5)
def grade_distribution(course_name):
    grades = dict.fromkeys([1, 2, 3, 4, 5])
    for grade in grades:
        count = db.execute('''
        SELECT
            COUNT(Credits.grade)
        FROM
            Courses LEFT JOIN Credits ON Courses.id = Credits.course_id
        WHERE
            Credits.grade = ? AND Courses.name = ?
        ''', [str(grade), course_name]).fetchone()[0]
        grades[grade] = count
    return grades

# hakee listan kursseista (nimi, opettajien määrä, suorittajien määrä) (aakkosjärjestyksessä)
def course_list():
    course_list = db.execute('''
    SELECT
        Courses.name, COUNT(DISTINCT TC.teacher_id), COUNT(DISTINCT Credits.student_id)
    FROM
        Courses
        LEFT JOIN Credits ON Courses.id = Credits.course_id
        LEFT JOIN TeacherCourses TC ON Courses.id = TC.course_id
    GROUP BY
        Courses.name
    ORDER BY
        Courses.name
    ''').fetchall()
    return course_list

# hakee listan opettajista kursseineen (aakkosjärjestyksessä opettajat ja kurssit)
def teacher_list():
    teachers = db.execute('SELECT DISTINCT T.name FROM Teachers T GROUP BY T.name ORDER BY T.name').fetchall()
    teachers = [teacher[0] for teacher in teachers]
    teacher_list = []
    teacher_course_list = db.execute('''
    SELECT
        T.name, C.name
    FROM
        Teachers T
        LEFT JOIN TeacherCourses TC ON T.id = TC.teacher_id
        LEFT JOIN Courses C on C.id = TC.course_id
    ''').fetchall()
    for teacher in teachers:
        courses = []
        for teacher_course in teacher_course_list:
            if teacher_course[0] == teacher:
                courses.append(teacher_course[1])
        courses.sort()
        teacher_list.append((teacher, courses))
    return teacher_list

# hakee ryhmässä olevat henkilöt (aakkosjärjestyksessä)
def group_people(group_name):
    teachers = db.execute('''
    SELECT
        T.name
    FROM
        Groups G, Teachers T, TeachersInGroup TG
    WHERE
        G.id = TG.group_id AND
        T.id = TG.teacher_id AND
        G.name = ?
    GROUP BY
        T.name
    ''', [group_name]).fetchall()
    students = db.execute('''
    SELECT
        S.name
    FROM
        Groups G, Students S, StudentsInGroup SG
    WHERE
        G.id = SG.group_id AND
        S.id = SG.student_id AND
        G.name = ?
    GROUP BY
        S.name
    ''', [group_name]).fetchall()
    teachers = [teacher[0] for teacher in teachers]
    students = [student[0] for student in students]
    teachers.extend(students)
    teachers.sort()
    return teachers

# hakee ryhmissä saatujen opintopisteiden määrät (aakkosjärjestyksessä)
def credits_in_groups():
    credits = db.execute('''
    SELECT
        G.name, SUM(IFNULL(Courses.credits,0))
    FROM
        Groups G
        LEFT JOIN StudentsInGroup SG ON G.id = SG.group_id
        LEFT JOIN Credits ON Credits.student_id = SG.student_id
        LEFT JOIN Courses ON Courses.id = Credits.course_id
    GROUP BY
        G.name
    ORDER BY
        G.name
    ''').fetchall()
    return credits

# hakee ryhmät, joissa on tietty opettaja ja opiskelija (aakkosjärjestyksessä)
def common_groups(teacher_name, student_name):
    groups = db.execute('''
    SELECT
        G.name
    FROM
        Groups G
        LEFT JOIN TeachersInGroup TG ON G.id = TG.group_id
        LEFT JOIN Teachers T ON T.id = TG.teacher_id
        LEFT JOIN StudentsInGroup SG ON G.id = SG.group_id
        LEFT JOIN Students S ON S.id = SG.student_id
    WHERE
        T.name = ? AND
        S.name = ?
    GROUP BY
        G.name
    ORDER BY
        G.name
    ''', [teacher_name, student_name]).fetchall()
    groups = [group[0] for group in groups]
    return groups