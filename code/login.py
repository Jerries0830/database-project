from tkinter import *
from tkinter.messagebox import showerror
from pymysql import connect
from administrator import Administrator
from faculty import Faculty
from manager import Manager
from instructor import Instructor

import commands

HOST = "localhost"
PORT = 3306
USER = "root"
PASS = "Zalone1314520"
DATABASE = "databaseDesign"


class Login:
    def __init__(self):
        self.root = Tk()

        self.role = IntVar()
        self.id = StringVar()

    def start(self):
        # 选择身份
        role_frame = LabelFrame(self.root, text="选择身份", padx=5, pady=5)
        role_frame.pack(padx=10, pady=10, fill='x')

        Radiobutton(role_frame, text="管理员", variable=self.role, value=0).grid(row=0, column=0)
        Radiobutton(role_frame, text="职员", variable=self.role, value=1).grid(row=0, column=1)
        Radiobutton(role_frame, text="经理", variable=self.role, value=2).grid(row=0, column=2)
        Radiobutton(role_frame, text="教员", variable=self.role, value=3).grid(row=0, column=3)

        # 输入信息
        login_frame = LabelFrame(self.root, text="登陆", padx=5, pady=5)
        login_frame.pack(padx=10, pady=10, fill='x')

        Label(login_frame, text="员工号：").grid(row=0, column=0, sticky='w')
        Entry(login_frame, textvariable=self.id).grid(row=0, column=1, columnspan=4)

        Button(login_frame, text="登陆", command=self.check).grid(row=2, column=0, columnspan=5)

        self.root.title("员工管理系统")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()

    def check(self):
        id = self.id.get()
        role = self.role.get()

        try:
            connection = connect(host=HOST, port=PORT, user=USER, password=PASS, database=DATABASE)

            if id == "":
                showerror(title="登陆失败", message="请输入员工号")
            elif not commands.login(connection, id, role):
                showerror(title="登陆失败", message="用户没有该身份")
            else:
                if role == 0:
                    Administrator(id, connection).start()
                elif role == 1:
                    Faculty(id, connection).start()
                elif role == 2:
                    Manager(id, connection).start()
                elif role == 3:
                    Instructor(id, connection).start()
        except TimeoutError:
            showerror(title="登陆失败", message="无法建立连接")
