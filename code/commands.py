import pymysql

table_dict = {0: "administrator", 1: "faculty", 2: "manager", 3: "instructor"}


def login(connection, id, role):
    cursor = connection.cursor()
    return cursor.execute(f"select facultyId from {table_dict[role]} where facultyId = {id}") == 1


def get_personal_information(connection, *args):
    cursor = connection.cursor()
    cursor.callproc("get_personal_information", args)
    return cursor.fetchone()


def modify_personal_information(connection, *args):
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"update faculty set address='{args[1]}', phoneNumber='{args[2]}', email='{args[3]}' where facultyId = {args[0]};")
        log(connection, args[0], "modify personal information")

        return True
    except pymysql.Error:
        return False


def get_departments(connection, *args):
    cursor = connection.cursor()
    cursor.execute("select departmentId, name from department order by departmentId")
    return cursor.fetchall()


def get_taken_courses(connection, *args):
    cursor = connection.cursor()
    cursor.callproc("get_taken_courses", args)
    return cursor.fetchall()


def get_teach_courses(connection, *args):
    cursor = connection.cursor()
    cursor.execute(f"select courseName, courseId from course where instructorId = {args[0]} order by courseId;")
    return cursor.fetchall()


def get_new_course_id(connection, *args):
    cursor = connection.cursor()
    cursor.execute(f"select max(courseId) + 1 from course")
    return cursor.fetchone()


def create_course(connection, *args):
    try:
        cursor = connection.cursor()
        cursor.execute(f"insert into course(courseId, courseName, instructorId, type, content) "
                       f"VALUES ({args[1]}, '{args[2]}', {args[3]}, '{args[4]}', '{args[5]}')")
        log(connection, args[0], f"create course with id {args[1]}")

        return True
    except pymysql.Error:
        return False


def get_course_information(connection, *args):
    cursor = connection.cursor()
    cursor.execute(
        f"select courseName, type, content, instructorId from course where courseId = {args[0]}")
    return cursor.fetchone()


def get_course_instructor(connection, *args):
    cursor = connection.cursor()
    cursor.execute(f"select instructorId from course where courseId = {args[0]} order by courseId;")
    return cursor.fetchone()


def get_course_availablility(connection, *args):
    cursor = connection.cursor()
    cursor.execute(f"select departmentId, compulsory from offers where courseId = {args[0]} order by departmentId")
    return cursor.fetchall()


def update_course(connection, *args):
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"update course set courseName = '{args[2]}', type = '{args[3]}', content = '{args[4]}' where courseId = {args[1]};")
        log(connection, args[0], f"update course with id {args[1]}")

        return True
    except pymysql.Error:
        return False


def modify_offers(connection, *args):
    try:
        cursor = connection.cursor()
        if args[2] == 0:
            cursor.execute(
                f"delete from offers where departmentId = {args[0]} and courseId = {args[1]};")
        else:
            compulsory = 1 if args[2] == 2 else 0
            cursor.execute(
                f"replace into offers(departmentId, courseId, compulsory) values({args[0]}, {args[1]}, {compulsory});")
        return True
    except pymysql.Error:
        return False


def get_course_sections(connection, *args):
    cursor = connection.cursor()
    cursor.execute(f"select sectionId, status from section where courseId = {args[0]} order by sectionId;")
    return cursor.fetchall()


def create_section(connection, *args):
    try:
        cursor = connection.cursor()
        cursor.callproc("create_section", args[1])
        log(connection, args[0], f"create section of course with id {args[1]}")

        return True
    except pymysql.Error:
        return False


def get_students(connection, *args):
    cursor = connection.cursor()
    cursor.callproc("get_students", args)
    return cursor.fetchall()


def end_section(connection, *args):
    cursor = connection.cursor()
    cursor.callproc("end_section", args[1:])
    result = cursor.fetchone()[0]
    log(connection, args[0], f"end section {args[2]} of course with id {args[1]}")

    return True if result else False


def get_students_with_score(connection, *args):
    cursor = connection.cursor()
    cursor.callproc("get_students_with_score", args)
    return cursor.fetchall()


def record_score(connection, *args):
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"update takes set score = {args[4]} where courseId = {args[1]} and sectionId = {args[2]} and facultyId = {args[3]};")
        log(connection, args[0], f"record score of {args[3]} on course {args[1]} section {args[2]}")

        return True
    except pymysql.Error:
        return False


def get_manage_department(connection, *args):
    cursor = connection.cursor()
    cursor.execute(f"select departmentId from manager where facultyId = {args[0]} order by departmentId;")
    return cursor.fetchone()


def get_department_courses(connection, *args):
    cursor = connection.cursor()
    cursor.callproc("get_department_courses", args)
    return cursor.fetchall()


def get_dept_faculty(connection, *args):
    cursor = connection.cursor()
    cursor.execute(
        f"select name, facultyId, gender, age, onboardTime, address, phoneNumber, email "
        f"from faculty where departmentId = {args[0]} order by facultyId;")
    return cursor.fetchall()


def get_dept_faculty_with_course(connection, *args):
    cursor = connection.cursor()
    cursor.execute(f"select name, facultyId, gender, age, onboardTime, address, phoneNumber, email "
                   f"from faculty where departmentId = {args[0]} and facultyId {'not' if args[2] else ''} "
                   f"in (select facultyId from takes where courseId = {args[1]}) order by facultyId")
    return cursor.fetchall()


def get_dept_faculty_with_pass(connection, *args):
    cursor = connection.cursor()
    cursor.execute(f"select name, facultyId, gender, age, onboardTime, address, phoneNumber, email "
                   f"from faculty where departmentId = {args[0]} and facultyId {'not' if args[2] else ''} "
                   f"in (select facultyId from takes where courseId = {args[1]} and pass = 1) order by facultyId")
    return cursor.fetchall()


def get_faculty(connection, *args):
    cursor = connection.cursor()
    cursor.execute(
        f"select facultyId, faculty.name, department.name, gender, age, onboardTime, address, phoneNumber, email "
        f"from faculty join department on faculty.departmentId = department.departmentId")
    return cursor.fetchall()


def get_dept_id(connection, *args):
    cursor = connection.cursor()
    cursor.execute(f"select departmentId from department where name = '{args[0]}';")
    return cursor.fetchone()


def add_user(connection, *args):
    try:
        id = args[0]
        args = args[1]
        dept = get_dept_id(connection, args[1])[0]

        cursor = connection.cursor()
        cursor.execute(
            f"insert into faculty(facultyId, departmentId, name, gender, age, onboardTime, address, phoneNumber, email) "
            f"values ({args[0]}, {dept}, '{args[2]}', '{args[3]}', {args[4]}, '{args[5]}', '{args[6]}', '{args[7]}', '{args[8]}');")
        log(connection, id, f"add user {args[0]}")

        return True
    except pymysql.Error:
        return False


def modify_user(connection, *args):
    try:
        id = args[0]
        faculty_id = args[1]
        args = args[2]
        dept = get_dept_id(connection, args[1])[0]

        cursor = connection.cursor()
        cursor.execute(
            f"update faculty set facultyId = {args[0]}, departmentId={dept}, name='{args[2]}', gender='{args[3]}',"
            f"age={args[4]}, onboardTime='{args[5]}', address='{args[6]}', phoneNumber='{args[7]}', email='{args[8]}' "
            f"where facultyId = {faculty_id};")
        log(connection, id, f"modify user {faculty_id}")

        return True
    except pymysql.Error:
        return False


def delete_user(connection, *args):
    try:
        cursor = connection.cursor()
        cursor.execute(f"delete from faculty where facultyId = {args[1]};")
        log(connection, args[0], f"delete user {args[1]}")

        return True
    except pymysql.Error:
        return False


def get_instructors(connection, *args):
    cursor = connection.cursor()
    cursor.execute(f"select facultyId, name from instructor natural join faculty")
    return cursor.fetchall()


def modify_course(connection, *args):
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"update course set courseName = '{args[2]}', instructorId = {args[3]}, type = '{args[4]}', content = '{args[5]}' where courseId = {args[1]};")
        log(connection, args[0], f"modify course {args[1]}")

        return True
    except pymysql.Error:
        return False


def get_courses(connection, *args):
    cursor = connection.cursor()
    cursor.execute("select courseName, courseId, name from course join "
                   "(select facultyId, name from instructor natural join faculty) as instructor "
                   "on instructorId = facultyId")
    return cursor.fetchall()


def enroll(connection, *args):
    cursor = connection.cursor()

    try:
        cursor.callproc("enroll", args[1:])
        result = cursor.fetchone()
        log(connection, args[0], f"enroll {args[4]} on course {args[2]} section {args[3]}")

        return True, result
    except pymysql.Error:
        return False, None


def get_unfinished_courses(connection, *args):
    cursor = connection.cursor()
    cursor.callproc("get_unfinished_courses", args)
    return cursor.fetchall()


def get_expected_courses(connection, *args):
    cursor = connection.cursor()
    cursor.callproc("get_expected_courses", args)
    return cursor.fetchall()


def transfer(connection, *args):
    try:
        cursor = connection.cursor()
        cursor.execute(f"update faculty set departmentId = {args[2]} where facultyId = {args[1]}")
        log(connection, args[0], f"transfer {args[1]} to department {args[2]}")

        return True
    except pymysql.Error:
        return False


def get_log(connection, *args):
    cursor = connection.cursor()
    cursor.execute("select * from log")
    return cursor.fetchall()


def log(connection, *args):
    cursor = connection.cursor()
    cursor.execute(f"insert into log(user, action, date) values({args[0]}, '{args[1]}', CURDATE())")
