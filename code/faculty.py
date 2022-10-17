from tkinter import *
from tkinter.messagebox import showerror, showinfo
from common import get_treeview

import commands

status = {None: "进行中", 0: "未通过", 1: "已通过"}


class Faculty:
    def __init__(self, id, connection):
        self.id = id
        self.connection = connection

        self.address = StringVar()
        self.phoneNumber = StringVar()
        self.email = StringVar()

        self.root = Toplevel()

    def start(self):
        # 左侧为个人信息，右侧为已修课程
        information_frame = LabelFrame(self.root, text="个人信息", padx=5, pady=5)
        course_frame = LabelFrame(self.root, text="已修课程", padx=5, pady=5)

        # 左侧个人信息
        information = commands.get_personal_information(self.connection, self.id)
        self.address.set(information[6])
        self.phoneNumber.set(information[7])
        self.email.set(information[8])

        raw_labels = ["员工号", "部门", "姓名", "性别", "年龄", "入职日", "地址", "电话", "邮箱"]
        labels = ["%-9s" % raw_label for raw_label in raw_labels]

        # 不可变信息
        for i in range(6):
            Label(information_frame, text=labels[i]).grid(row=i, column=0, sticky='w')
            Label(information_frame, text=information[i]).grid(row=i, column=1, sticky='w')

        # 可变信息
        Label(information_frame, text=labels[6]).grid(row=6, column=0, sticky='w')
        Entry(information_frame, textvariable=self.address).grid(row=6, column=1, sticky='w')
        Label(information_frame, text=labels[7]).grid(row=7, column=0, sticky='w')
        Entry(information_frame, textvariable=self.phoneNumber).grid(row=7, column=1, sticky='w')
        Label(information_frame, text=labels[8]).grid(row=8, column=0, sticky='w')
        Entry(information_frame, textvariable=self.email).grid(row=8, column=1, sticky='w')

        # 修改按钮
        modify_button = Button(information_frame, text="修改", command=self.modify, width=27)
        modify_button.grid(row=9, column=0, columnspan=2, sticky='w')

        # 右侧已修课程
        # 课程列表
        take_view = get_treeview(course_frame,
                                 columns=["课程名称", "序号", "状态", "成绩"],
                                 widths=[100, 50, 70, 50],
                                 anchors=["w", "center", "center", "center"])

        records = ((course, sectionId, status[passed], score if score is not None else "-") for
                   course, sectionId, passed, score in
                   commands.get_taken_courses(self.connection, self.id))
        for record in records:
            take_view.insert("", "end", values=record)

        # 显示页面
        information_frame.pack(padx=10, pady=10, side="left")
        course_frame.pack(padx=10, pady=10, side="left", fill="y", expand=True)

        self.root.title("职员")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()

    def modify(self):
        address = self.address.get()
        phoneNumber = self.phoneNumber.get()
        email = self.email.get()

        if commands.modify_personal_information(self.connection, self.id, address, phoneNumber, email):
            self.connection.commit()
            showinfo(title="修改", message="修改成功")
        else:
            showerror(title="修改", message="修改失败")
