from tkinter import *
from tkinter.messagebox import showerror, showinfo
from common import get_treeview

import commands

compulsory = {0: "否", 1: "是"}
course_status = {0: "未结课", 1: "已结课"}
take_status = {None: "进行中", 0: "未通过", 1: "已通过"}
enroll = {0: "添加成功", 1: "不能安排必修课", 2: "该开课已结束", 3: "员工已通过该课程", 4: "员工已在该开课中"}


class Manager:
    def __init__(self, id, connection):
        self.id = id
        self.dept_id = commands.get_manage_department(connection, self.id)[0]
        self.connection = connection

        self.root = Toplevel()

        self.course_view = None
        self.section_view = None
        self.faculty_view = None

    def start(self):
        upper_frame = Frame(self.root)
        lower_frame = Frame(self.root)

        # 上侧
        # 部门课程
        course_frame = LabelFrame(upper_frame, text="部门课程", padx=5, pady=5)
        course_frame.pack(padx=0, pady=10, side="left", fill="y", expand=True)

        self.course_view = get_treeview(course_frame,
                                        columns=["课程名称", "课程编号", "必修"],
                                        widths=[100, 60, 30],
                                        anchors=["w", "center", "center"])

        self.course_view.bind("<ButtonRelease-1>", self.refresh_section)

        # 课程开课
        section_frame = LabelFrame(upper_frame, text="课程开课", padx=5, pady=5)
        section_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)

        self.section_view = get_treeview(section_frame,
                                         columns=["序号", "状态"],
                                         widths=[50, 70],
                                         anchors=["center", "center"])

        # 选项
        option_frame = LabelFrame(upper_frame, text="员工操作", padx=5, pady=5)
        option_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)

        Button(option_frame, text="查看课程", command=self.check_score).pack(fill="x", expand=True)
        Button(option_frame, text="分配课程", command=self.enroll_section).pack(fill="x", expand=True)
        Button(option_frame, text="转移部门", command=self.transfer).pack(fill="x", expand=True)

        # 筛选
        filter_frame = LabelFrame(upper_frame, text="筛选", padx=5, pady=5)
        filter_frame.pack(padx=10, pady=10, side="left", fill="both", expand=True)
        button_frame = Frame(filter_frame)
        button_frame.pack(fill="both", expand=True)
        Button(button_frame, text="刷新", command=self.refresh_faculty).pack(fill="x", expand=True)
        Button(button_frame, text="课程修读筛选", command=lambda: self.filter_by_course(False)).pack(fill="x", expand=True)
        Button(button_frame, text="课程未修读筛选", command=lambda: self.filter_by_course(True)).pack(fill="x", expand=True)
        Button(button_frame, text="合格筛选", command=lambda: self.filter_by_pass(False)).pack(fill="x", expand=True)
        Button(button_frame, text="不合格筛选", command=lambda: self.filter_by_pass(True)).pack(fill="x", expand=True)

        # 下侧
        # 部门员工
        faculty_frame = LabelFrame(lower_frame, text="部门员工", padx=5, pady=5)
        faculty_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)

        self.faculty_view = get_treeview(faculty_frame,
                                         columns=["姓名", "员工号", "性别", "年龄", "入职日", "地址", "电话", "邮箱"],
                                         widths=[80, 100, 40, 40, 100, 80, 100, 150],
                                         anchors=["center", "center", "center", "center", "center", "w", "w", "w"])

        upper_frame.pack(side="top", fill="x", expand=True)
        lower_frame.pack(side="top", fill="x", expand=True)

        self.initialize()

        self.root.title("经理")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()

    def initialize(self):
        for course in commands.get_department_courses(self.connection, self.dept_id):
            self.course_view.insert("", "end", values=(course[0], course[1], compulsory[course[2]]))

        self.refresh_faculty()

    def refresh_section(self, event):
        try:
            selected = self.course_view.focus()
            course_id = self.course_view.item(selected)["values"][1]

            for item in self.section_view.get_children():
                self.section_view.delete(item)

            for sectionId, has_ended in commands.get_course_sections(self.connection, course_id):
                self.section_view.insert("", "end", values=(sectionId, course_status[has_ended]))
        except IndexError:
            pass

    def refresh_faculty(self):
        for item in self.faculty_view.get_children():
            self.faculty_view.delete(item)

        for faculty in commands.get_dept_faculty(self.connection, self.dept_id):
            self.faculty_view.insert("", "end", values=faculty)

    def filter_by_course(self, reverse=False):
        try:
            selected = self.course_view.focus()
            course_id = self.course_view.item(selected)["values"][1]

            for item in self.faculty_view.get_children():
                self.faculty_view.delete(item)

            for faculty in commands.get_dept_faculty_with_course(self.connection, self.dept_id, course_id, reverse):
                self.faculty_view.insert("", "end", values=faculty)
        except IndexError:
            showerror(title="操作失败", message="请选择课程")

    def filter_by_pass(self, reverse=False):
        try:
            selected = self.course_view.focus()
            course_id = self.course_view.item(selected)["values"][1]

            for item in self.faculty_view.get_children():
                self.faculty_view.delete(item)

            for faculty in commands.get_dept_faculty_with_pass(self.connection, self.dept_id, course_id, reverse):
                self.faculty_view.insert("", "end", values=faculty)
        except IndexError:
            showerror(title="操作失败", message="请选择课程")

    def check_score(self):
        try:
            selected = self.faculty_view.focus()
            faculty_id = self.faculty_view.item(selected)["values"][1]
            Score(self.connection, faculty_id).start()
        except IndexError:
            showerror(title="操作失败", message="请选择员工")

    def enroll_section(self):
        try:
            course_id = self.course_view.item(self.course_view.focus())["values"][1]
            section_id = self.section_view.item(self.section_view.focus())["values"][0]
            faculty_id = self.faculty_view.item(self.faculty_view.focus())["values"][1]

            flag, status = commands.enroll(self.connection, self.id, self.dept_id, course_id, section_id, faculty_id)

            if flag:
                if status[0] == 0:
                    self.connection.commit()
                showinfo(title="添加", message=enroll[status[0]])
            else:
                showerror(title="操作失败", message="添加失败")
        except IndexError:
            showerror(title="操作失败", message="请选择课程、开课和员工")

    def transfer(self):
        try:
            selected = self.faculty_view.focus()
            faculty_id = self.faculty_view.item(selected)["values"][1]
            Transfer(self.connection, self.id, self.dept_id, faculty_id).start()
        except IndexError:
            showerror(title="操作失败", message="请选择员工")


class Score:
    def __init__(self, connection, id):
        self.connection = connection
        self.id = id

        self.root = Toplevel()

    def start(self):
        course_frame = LabelFrame(self.root, text="已修课程", padx=5, pady=5)
        course_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)

        take_view = get_treeview(course_frame,
                                 columns=["课程名称", "序号", "状态", "成绩"],
                                 widths=[100, 50, 70, 50],
                                 anchors=["w", "center", "center", "center"])

        records = ((course, sectionId, take_status[passed], score if score is not None else "-") for
                   course, sectionId, passed, score in
                   commands.get_taken_courses(self.connection, self.id))
        for record in records:
            take_view.insert("", "end", values=record)

        self.root.title("成绩")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()


class Transfer:
    def __init__(self, connection, id, dept_id, faculty_id):
        self.connection = connection
        self.id = id
        self.dept_id = dept_id
        self.faculty_id = faculty_id
        self.unfinish_courses = None

        self.root = Toplevel()

        self.dept_view = None
        self.expect_view = None

    def start(self):
        self.unfinish_courses = commands.get_unfinished_courses(self.connection, self.faculty_id)

        upper_frame = Frame(self.root)
        lower_frame = Frame(self.root)

        # 未完成课程
        unfinish_frame = LabelFrame(upper_frame, text="未完成课程", padx=5, pady=5)

        unfinish_view = get_treeview(unfinish_frame,
                                     columns=["课程名称", "状态"],
                                     widths=[100, 60],
                                     anchors=["center", "center"])
        for name, passed in self.unfinish_courses:
            unfinish_view.insert("", "end", values=[name, take_status[passed]])

        # 转移部门
        dept_frame = LabelFrame(upper_frame, text="新部门", padx=5, pady=5)

        self.dept_view = get_treeview(dept_frame, columns=["部门名称"], widths=[100], anchors=["center"])
        for dept_id, dept_name in commands.get_departments(self.connection):
            if dept_id != self.dept_id:
                self.dept_view.insert("", "end", values=[dept_name])

        self.dept_view.bind("<ButtonRelease-1>", self.refresh_expect)

        # 待修读课程
        expect_frame = LabelFrame(upper_frame, text="待修读课程", padx=5, pady=5)

        self.expect_view = get_treeview(expect_frame, columns=["课程名称"], widths=[100], anchors=["center"])

        # 提交按钮
        Button(lower_frame, text="确认转移", command=self.transfer).pack()
        # 显示界面
        unfinish_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)
        dept_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)
        expect_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)

        upper_frame.pack(side="top", fill="x", expand=True)
        lower_frame.pack(side="top", pady=10, fill="x", expand=True)

        self.root.title("转移部门")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()

    def refresh_expect(self, event):
        try:
            selected = self.dept_view.focus()
            dept_name = self.dept_view.item(selected)["values"][0]
            dept_id = commands.get_dept_id(self.connection, dept_name)

            for item in self.expect_view.get_children():
                self.expect_view.delete(item)

            for course in commands.get_expected_courses(self.connection, self.faculty_id, dept_id):
                self.expect_view.insert("", "end", values=course)
        except IndexError:
            pass

    def transfer(self):
        if len(self.unfinish_courses) > 0:
            showerror(title="转移部门", message="请先完成所有课程")
        else:
            selected = self.dept_view.focus()
            dept_name = self.dept_view.item(selected)["values"][0]
            dept_id = commands.get_dept_id(self.connection, dept_name)[0]

            if commands.transfer(self.connection, self.id, self.faculty_id, dept_id):
                self.connection.commit()
                self.root.destroy()
                showinfo(title="转移部门", message="转移成功")
            else:
                showerror(title="转移部门", message="转移失败")
