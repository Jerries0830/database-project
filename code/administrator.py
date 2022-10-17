from tkinter import *
from tkinter.ttk import Combobox, Separator
from tkinter.messagebox import showinfo, showerror
from common import get_treeview
from faculty import Faculty
import commands


class Administrator:
    def __init__(self, id, connection):
        self.id = id
        self.connection = connection

        self.root = Toplevel()
        self.frames = []

        self.user_view = None
        self.course_view = None
        self.section_view = None
        self.log_view = None

    def start(self):
        # 上方按钮
        control_frame = Frame(self.root, padx=5, pady=0)
        control_frame.pack(padx=5, pady=5, side="top", fill="x", expand=True)

        Button(control_frame, text="查看用户", command=lambda: self.show(0)).pack(side="left")
        Button(control_frame, text="查看课程", command=lambda: self.show(1)).pack(side="left")
        Button(control_frame, text="查看日志", command=lambda: self.show(2)).pack(side="left")

        user_frame = self.initialize_user_frame()
        course_frame = self.initialize_course_frame()
        log_frame = self.initialize_log_frame()

        self.frames.append(user_frame)
        self.frames.append(course_frame)
        self.frames.append(log_frame)

        self.refresh()
        self.show(0)

        self.root.title("管理员")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()

    def initialize_user_frame(self):
        user_frame = Frame(self.root, padx=5, pady=5)

        user_option_frame = LabelFrame(user_frame, text="操作", padx=5, pady=5)
        user_option_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)

        Button(user_option_frame, text="刷新", command=self.refresh_user).pack(fill="x", expand=True)
        Button(user_option_frame, text="增加用户", command=self.add_user).pack(fill="x", expand=True)
        Button(user_option_frame, text="查看用户", command=self.modify_user).pack(fill="x", expand=True)
        Button(user_option_frame, text="删除用户", command=self.delete_user).pack(fill="x", expand=True)

        user_information_frame = LabelFrame(user_frame, text="查看用户", padx=5, pady=5)
        user_information_frame.pack(padx=0, pady=10, side="left", fill="y", expand=True)

        self.user_view = get_treeview(user_information_frame,
                                      columns=["员工号", "姓名", "部门", "性别", "年龄", "入职日", "地址", "电话", "邮箱"],
                                      widths=[100, 80, 100, 40, 40, 100, 80, 100, 150],
                                      anchors=["center", "center", "center", "center", "center", "center", "w", "w",
                                               "w"])

        return user_frame

    def initialize_course_frame(self):
        course_frame = Frame(self.root, padx=5, pady=0)

        option_frame = LabelFrame(course_frame, text="操作", padx=5, pady=5, width=100)
        option_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)

        Button(option_frame, text="刷新", command=self.refresh_course).pack(fill="x", expand=True)
        Button(option_frame, text="新建课程", command=self.create_course).pack(fill="x", expand=True)
        Button(option_frame, text="修改课程", command=self.modify_course).pack(fill="x", expand=True)
        Button(option_frame, text="删除课程").pack(fill="x", expand=True)

        list_frame = LabelFrame(course_frame, text="课程信息", padx=5, pady=5)
        list_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)

        self.course_view = get_treeview(list_frame,
                                        columns=["名称", "编号", "教师"],
                                        widths=[100, 60, 80],
                                        anchors=["center", "center", "center"])

        return course_frame

    def initialize_log_frame(self):
        log_frame = Frame(self.root, padx=5, pady=0)

        self.log_view = get_treeview(log_frame,
                                     columns=["序号", "员工号", "操作", "日期"],
                                     widths=[50, 100, 240, 80],
                                     anchors=["center", "center", "w", "center"])

        return log_frame

    def show(self, index):
        for frame in self.frames:
            frame.pack_forget()

        self.frames[index].pack(padx=5, pady=5, side="top", fill="y", expand=True)

    def refresh(self):
        self.refresh_user()
        self.refresh_course()
        self.refresh_log()

    # 查看用户
    def refresh_user(self):
        for item in self.user_view.get_children():
            self.user_view.delete(item)

        for faculty in commands.get_faculty(self.connection):
            self.user_view.insert("", "end", values=faculty)

    def add_user(self):
        FacultyAdmin(self.connection, self.id).start()

    def check_user(self):
        try:
            selected = self.user_view.focus()
            user_id = self.user_view.item(selected)["values"][0]
            Faculty(user_id, self.connection).start()
        except IndexError:
            showerror(title="操作失败", message="请选择用户")

    def modify_user(self):
        try:
            selected = self.user_view.focus()
            user_id = self.user_view.item(selected)["values"][0]
            FacultyAdmin(self.connection, self.id, user_id).start()
        except IndexError:
            showerror(title="操作失败", message="请选择用户")

    def delete_user(self):
        try:
            selected = self.user_view.focus()
            user_id = self.user_view.item(selected)["values"][0]

            if commands.delete_user(self.connection, self.id, user_id):
                self.connection.commit()
                self.refresh_user()
                showinfo(title="删除用户", message=f"删除成功")
            else:
                showerror(title="删除用户", message=f"删除失败")
        except IndexError:
            showerror(title="操作失败", message="请选择用户")

    # 查看课程
    def refresh_course(self):
        for item in self.course_view.get_children():
            self.course_view.delete(item)

        for record in commands.get_courses(self.connection, self.id):
            self.course_view.insert("", "end", values=record)

    def create_course(self):
        CourseAdmin(self.connection, self.id).start()

    def modify_course(self):
        try:
            selected_course = self.course_view.focus()
            course_id = self.course_view.item(selected_course)["values"][1]
            CourseAdmin(self.connection, course_id).start()
        except IndexError:
            showerror(title="操作失败", message="请选择课程")

    # 查看日志
    def refresh_log(self):
        for item in self.log_view.get_children():
            self.log_view.delete(item)

        for record in commands.get_log(self.connection):
            self.log_view.insert("", "end", values=record)


class FacultyAdmin:
    def __init__(self, connection, id, faculty_id=None):
        self.connection = connection
        self.id = id
        self.faculty_id = faculty_id
        self.is_modify = self.faculty_id is not None
        self.action = "修改" if self.is_modify else "增加"

        self.root = Toplevel()

        self.content = []

    def start(self):
        information_frame = LabelFrame(self.root, text="个人信息", padx=5, pady=5)
        information_frame.pack(padx=10, pady=10, side="left", fill='y', expand=True)

        raw_labels = ["员工号", "部门", "姓名", "性别", "年龄", "入职日", "地址", "电话", "邮箱"]
        labels = ["%-9s" % raw_label for raw_label in raw_labels]

        faculty_id = StringVar()
        Label(information_frame, text=labels[0]).grid(row=0, column=0, sticky='w')
        Entry(information_frame, textvariable=faculty_id).grid(row=0, column=1, sticky='w')
        self.content.append(faculty_id)

        dept_names = [dept_name for _, dept_name in commands.get_departments(self.connection)]
        Label(information_frame, text=labels[1]).grid(row=1, column=0, sticky='w')
        department = Combobox(information_frame, values=dept_names)
        department.grid(row=1, column=1, sticky='w')
        self.content.append(department)

        name = StringVar()
        Label(information_frame, text=labels[2]).grid(row=2, column=0, sticky='w')
        Entry(information_frame, textvariable=name).grid(row=2, column=1, sticky='w')
        self.content.append(name)

        Label(information_frame, text=labels[3]).grid(row=3, column=0, sticky='w')
        department = Combobox(information_frame, values=["男", "女"])
        department.grid(row=3, column=1, sticky='w')
        self.content.append(department)

        for i in range(4, 9):
            var = StringVar()
            Label(information_frame, text=labels[i]).grid(row=i, column=0, sticky='w')
            Entry(information_frame, textvariable=var).grid(row=i, column=1, sticky='w')
            self.content.append(var)

        # 确认按钮
        confirm_button = Button(information_frame, text=self.action, width=27, command=self.submit)
        confirm_button.grid(row=9, column=0, columnspan=2, sticky='w')

        # 如果修改信息，展示原信息并展示已修课程
        if self.is_modify:
            for index, information in enumerate(commands.get_personal_information(self.connection, self.faculty_id)):
                self.content[index].set(information)

            course_frame = LabelFrame(self.root, text="已修课程", padx=5, pady=5)
            course_frame.pack(padx=10, pady=10, side="left", fill='y', expand=True)

            take_view = get_treeview(course_frame,
                                     columns=["课程名称", "序号", "状态", "成绩"],
                                     widths=[100, 50, 70, 50],
                                     anchors=["w", "center", "center", "center"])

            status = {None: "进行中", 0: "未通过", 1: "已通过"}
            records = ((course, sectionId, status[passed], score if score is not None else "-") for
                       course, sectionId, passed, score in
                       commands.get_taken_courses(self.connection, self.faculty_id))
            for record in records:
                take_view.insert("", "end", values=record)

        # 显示页面
        self.root.title(f"{self.action}职员")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()

    def submit(self):
        information = [content.get() for content in self.content]
        flag = commands.modify_user(self.connection, self.id, self.faculty_id, information) if self.is_modify else \
            commands.add_user(self.connection, self.id, information)

        if flag:
            self.connection.commit()
            showinfo(title=self.action, message=f"{self.action}成功")
        else:
            showerror(title=self.action, message=f"{self.action}失败")


class CourseAdmin:
    def __init__(self, connection, id, course_id=None):
        self.connection = connection
        self.id = id
        self.course_id = course_id
        self.is_modify = self.course_id is not None
        self.action = "修改" if self.is_modify else "新建"

        self.root = Toplevel()

        self.course_name = StringVar()
        self.course_type = StringVar()
        self.instructor = None
        self.text = None

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

        Label(information_frame, text="%-9s" % "课程教师").grid(row=2, column=0)
        self.instructor = Combobox(information_frame,
                                   values=[name for _, name in commands.get_instructors(self.connection)])
        self.instructor.grid(row=2, column=1)

        Label(information_frame, text="%-9s" % "课程简介").grid(row=3, column=0)
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

        if self.is_modify:
            values = commands.get_course_information(self.connection, self.course_id)
            self.course_name.set(values[0])
            self.course_type.set(values[1])
            self.text.delete("0.0", "end")
            self.text.insert("0.0", values[2])
            dict = {id: name for id, name in commands.get_instructors(self.connection)}
            instructor = dict[values[3]]
            self.instructor.set(instructor)

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
        dict = {name: id for id, name in commands.get_instructors(self.connection)}
        instructor_id = dict[self.instructor.get()]
        content = self.text.get("0.0", "end")

        if self.is_modify:
            flag = commands.modify_course(self.connection, self.course_id, name, instructor_id, type, content)
        else:
            self.course_id = commands.get_new_course_id(self.connection)[0]
            flag = commands.create_course(self.connection, self.id, self.course_id, name, instructor_id,  type, content)

        for dept_id, var in self.offers.items():
            if not flag:
                break
            flag = commands.modify_offers(self.connection, dept_id, self.course_id, var.get())

        if flag:
            self.connection.commit()
            showinfo(title=self.action, message=f"{self.action}成功")
        else:
            showerror(title=self.action, message=f"{self.action}失败")
