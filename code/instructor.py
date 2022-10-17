from tkinter import *
from tkinter.ttk import Separator
from tkinter.messagebox import showerror, showinfo
from common import get_treeview

import commands

status = {0: "未结课", 1: "已结课"}


class Instructor:
    def __init__(self, id, connection):
        self.id = id
        self.connection = connection

        self.root = Toplevel()

        self.course_view = None
        self.section_view = None

    def start(self):
        # 左侧为选项按钮，中间为课程信息，右侧为开课信息
        option_frame = LabelFrame(self.root, text="操作", padx=5, pady=5, width=100)
        course_frame = LabelFrame(self.root, text="课程信息", padx=5, pady=5)
        section_frame = LabelFrame(self.root, text="开课信息", padx=5, pady=5)

        # 左侧选项按钮
        Button(option_frame, text="刷新", command=self.refresh).pack(fill="x", expand=True)
        Button(option_frame, text="新建课程", command=self.create_course).pack(fill="x", expand=True)

        Separator(option_frame, orient=HORIZONTAL).pack(fill="x", expand=True, pady=2)

        Button(option_frame, text="修改课程", command=self.modify_course).pack(fill="x", expand=True)
        Button(option_frame, text="新建开课", command=self.create_section).pack(fill="x", expand=True)

        Separator(option_frame, orient=HORIZONTAL).pack(fill="x", expand=True, pady=2)

        Button(option_frame, text="查看学员", command=self.show_student).pack(fill="x", expand=True)
        Button(option_frame, text="结束开课", command=self.end_section).pack(fill="x", expand=True)
        Button(option_frame, text="批改考试", command=self.record_score).pack(fill="x", expand=True)

        # 中间课程信息
        self.course_view = get_treeview(course_frame,
                                        columns=["名称", "编号"],
                                        widths=[100, 60],
                                        anchors=["center", "center"])

        self.course_view.bind("<ButtonRelease-1>", self.show_section)

        # 右侧开课信息
        self.section_view = get_treeview(section_frame,
                                         columns=["序号", "状态"],
                                         widths=[50, 70],
                                         anchors=["center", "center"])

        # 显示界面
        self.refresh()

        option_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)
        course_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)
        section_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)

        self.root.title("教员")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()

    def refresh(self):
        for item in self.course_view.get_children():
            self.course_view.delete(item)

        for item in self.section_view.get_children():
            self.section_view.delete(item)

        for record in commands.get_teach_courses(self.connection, self.id):
            self.course_view.insert("", "end", values=record)

    def create_course(self):
        Course(self.id, self.connection).start()

    def modify_course(self):
        try:
            selected_course = self.course_view.focus()
            course_id = self.course_view.item(selected_course)["values"][1]
            Course(self.id, self.connection, course_id).start()
        except IndexError:
            showerror(title="操作失败", message="请选择课程")

    def show_section(self, event):
        try:
            selected = self.course_view.focus()
            course_id = self.course_view.item(selected)["values"][1]

            for item in self.section_view.get_children():
                self.section_view.delete(item)

            for sectionId, has_ended in commands.get_course_sections(self.connection, course_id):
                self.section_view.insert("", "end", values=(sectionId, status[has_ended]))
        except IndexError:
            showerror(title="操作失败", message="请选择课程")

    def create_section(self):
        try:
            selected = self.course_view.focus()
            course_id = self.course_view.item(selected)["values"][1]

            if commands.create_section(self.connection, self.id, course_id):
                self.connection.commit()
                showinfo(title="开课", message="开课成功")
                self.show_section(None)
        except IndexError:
            showerror(title="操作失败", message="请选择课程")

    def show_student(self):
        try:
            values = self.get_selected_values()
            ShowStudent(self.connection, values[0], values[1]).start()
        except IndexError:
            showerror(title="操作失败", message="请选择开课")

    def end_section(self):
        try:
            values = self.get_selected_values()
            if commands.end_section(self.connection, self.id, values[0], values[1]):
                self.connection.commit()
                showinfo(title="结课", message="结课成功")
                self.show_section(None)
            else:
                showerror(title="结课", message="该课程已结课")
        except IndexError:
            showerror(title="操作失败", message="请选择开课")

    def record_score(self):
        try:
            selected_section = self.section_view.focus()
            has_ended = self.section_view.item(selected_section)["values"][1]
            if has_ended == "未结课":
                showerror(title="操作失败", message="课程未结束")
            else:
                values = self.get_selected_values()
                RecordScore(self.connection, values[0], values[1]).start()
        except IndexError:
            showerror(title="操作失败", message="请选择开课")

    # 顺序为名称、编号、序号、状态
    def get_selected_values(self):
        selected_course = self.course_view.focus()
        course_id = self.course_view.item(selected_course)["values"][1]
        selected_section = self.section_view.focus()
        section_id = self.section_view.item(selected_section)["values"][0]
        return course_id, section_id


class ShowStudent:
    def __init__(self, connection, course_id, section_id):
        self.connection = connection
        self.course_id = course_id
        self.section_id = section_id

        self.root = Toplevel()

    def start(self):
        student_frame = LabelFrame(self.root, text="学员信息", padx=5, pady=5)

        student_view = get_treeview(student_frame,
                                    columns=["姓名", "部门", "员工号", "性别", "年龄", "入职日", "地址", "电话", "邮箱"],
                                    widths=[80, 100, 100, 40, 40, 100, 80, 100, 150],
                                    anchors=["center", "center", "center", "center", "center", "center", "w", "w", "w"])

        for student in commands.get_students(self.connection, self.course_id, self.section_id):
            student_view.insert("", "end", values=student)

        student_frame.pack(padx=10, pady=10)

        self.root.title(f"{self.course_id}.{self.section_id}")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()


class RecordScore:
    def __init__(self, connection, course_id, section_id):
        self.connection = connection
        self.course_id = course_id
        self.section_id = section_id

        self.root = Toplevel()
        self.score_view = None

        self.id = StringVar()
        self.score = IntVar()

    def start(self):
        # 上侧为信息展示，下侧为成绩登记
        score_frame = LabelFrame(self.root, text="考试成绩", padx=5, pady=5)
        record_frame = LabelFrame(self.root, text="登记成绩", padx=5, pady=5)

        # 上侧信息展示
        self.score_view = get_treeview(score_frame,
                                       columns=["姓名", "员工号", "成绩"],
                                       widths=[100, 120, 80],
                                       anchors=["center", "center", "center"])

        # 下侧成绩登记
        Label(record_frame, text="员工号：").pack(side="left")
        Entry(record_frame, textvariable=self.id, width=10).pack(side="left", fill="x", expand=True)
        Label(record_frame, text="成绩：").pack(side="left")
        Entry(record_frame, textvariable=self.score, width=5).pack(side="left")
        Button(record_frame, text="确认", command=self.submit).pack(side="left")

        self.refresh()

        score_frame.pack(padx=10, pady=10, fill="x", expand=True)
        record_frame.pack(padx=10, pady=10, fill="x", expand=True)

        self.root.title(f"{self.course_id}.{self.section_id}")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()

    def submit(self):
        faculty_id = self.id.get()
        score = self.score.get()

        if commands.record_score(self.connection, self.id, self.course_id, self.section_id, faculty_id, score):
            self.connection.commit()
            showinfo(title="修改成绩", message="修改成功")
            self.refresh()
        else:
            showerror(title="修改成绩", message="修改失败")

    def refresh(self):
        for item in self.score_view.get_children():
            self.score_view.delete(item)

        for student in commands.get_students_with_score(self.connection, self.course_id, self.section_id):
            self.score_view.insert("", "end",
                                   values=(student[0], student[1], student[2] if student[2] is not None else "-"))


class Course:
    def __init__(self, id, connection, course_id=None):
        self.id = id
        self.connection = connection
        self.course_id = course_id
        self.action = "新建" if self.course_id is None else "修改"

        self.root = Toplevel()

        self.text = None
        self.course_name = StringVar()
        self.course_type = StringVar()

        self.offers = {}

    def start(self):
        # 左侧为课程信息，右侧为部门开放情况
        course_frame = LabelFrame(self.root, text="课程信息", padx=5, pady=5)
        offer_frame = LabelFrame(self.root, text="部门设置", padx=5, pady=5)

        # 左侧课程信息
        information_frame = Frame(course_frame)
        information_frame.pack(fill="x", expand=True)

        Label(information_frame, text="%-9s" % "课程名称").grid(row=0, column=0)
        Entry(information_frame, textvariable=self.course_name, width=20).grid(row=0, column=1)
        Label(information_frame, text="%-9s" % "课程类型").grid(row=1, column=0)
        Entry(information_frame, textvariable=self.course_type, width=20).grid(row=1, column=1)
        Label(information_frame, text="%-9s" % "课程简介").grid(row=2, column=0)

        self.text = Text(course_frame, width=33, height=10, wrap=WORD)
        self.text.pack(padx=10, pady=10)
        Button(course_frame, text="确认", command=self.submit).pack()

        # 右侧部门开放情况
        for index, (dept_id, dept_name) in enumerate(commands.get_departments(self.connection)):
            var = IntVar()
            self.offers[dept_id] = var
            Label(offer_frame, text="%-10s" % dept_name).grid(row=index, column=0, sticky="w")
            Radiobutton(offer_frame, text="不开放", variable=var, value=0).grid(row=index, column=1)
            Radiobutton(offer_frame, text="选修", variable=var, value=1).grid(row=index, column=2)
            Radiobutton(offer_frame, text="必修", variable=var, value=2).grid(row=index, column=3)

        if self.course_id is not None:
            values = commands.get_course_information(self.connection, self.course_id)
            self.course_name.set(values[0])
            self.course_type.set(values[1])
            self.text.delete("0.0", "end")
            self.text.insert("0.0", values[2])

            for dept_id, compulsory in commands.get_course_availablility(self.connection, self.course_id):
                self.offers[dept_id].set(2 if compulsory else 1)

        # 显示界面
        course_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)
        offer_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)

        self.root.title(f"{self.action}课程")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()

    def submit(self):
        name = self.course_name.get()
        type = self.course_type.get()
        content = self.text.get("0.0", "end")

        if self.course_id is None:
            self.course_id = commands.get_new_course_id(self.connection)[0]
            flag = commands.create_course(self.connection, self.id, self.course_id, name, self.id, type, content)
        else:
            flag = commands.update_course(self.connection, self.id, self.course_id, name, type, content)

        for dept_id, var in self.offers.items():
            if not flag:
                break
            flag = commands.modify_offers(self.connection, dept_id, self.course_id, var.get())

        if flag:
            self.connection.commit()
            showinfo(title=self.action, message=f"{self.action}成功")
        else:
            showerror(title=self.action, message=f"{self.action}失败")
