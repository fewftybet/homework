import pymysql
import pyodbc
import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import mysql.connector
from mysql.connector import Error


# 数据库连接配置
def connect_to_database():
    # 定义连接参数
    conn_str = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'passwd': '123456',
        'db': '图书管理系统',
        'charset': 'utf8'
    }

    # 使用 connect 方法连接数据库
    try:
        conn= pymysql.connect(**conn_str)
        return conn
    except Exception as e:
        messagebox.showerror("数据库连接失败", str(e))
        return None

# 执行 SQL 查询
def execute_query(conn, query):
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("查询失败", str(e))
        return False

# 登录验证
def verify_credentials(conn, username, password):
    query = "SELECT role FROM usr WHERE username = %s AND password = %s"
    cursor = conn.cursor()
    cursor.execute(query, (username, password))  # 修正参数传递
    row = cursor.fetchone()
    if row:
        role = row[0]
        if role == 'superadmin':
            messagebox.showinfo("登录成功", "超级管理员登录成功！")
            return 'superadmin'
            # 执行超级管理员的操作
        elif role == 'bookmanager':
            messagebox.showinfo("登录成功", "图书管理员登录成功！")
            return 'bookmanager'
            # 执行图书管理员的操作
        elif role == 'user':
            messagebox.showinfo("登录成功", "普通用户登录成功！")
            return 'user'
            # 执行普通用户的操作

# 登录界面
# 登录窗口
def login_window(root, username_var, password_var):
    root.title("图书馆在线系统")

    tk.Label(root, text="用户名:").grid(row=0, column=0)
    username_entry = tk.Entry(root, textvariable=username_var)
    username_entry.grid(row=0, column=1)

    tk.Label(root, text="密码:").grid(row=1, column=0)
    password_entry = tk.Entry(root, textvariable=password_var, show="*")
    password_entry.grid(row=1, column=1)

    def login():
        conn = connect_to_database()
        if conn:
            username = username_var.get()
            password = password_var.get()
            role = verify_credentials(conn, username, password)
            if role:
                for widget in root.winfo_children():  # 隐藏登录界面元素
                    widget.destroy()
                show_management_interface(root, role,conn)  # 用户成功登录，显示管理界面
            else:
                messagebox.showerror("登录失败", "用户名或密码错误。")

    login_button = tk.Button(root, text="登录", command=login)
    login_button.grid(row=2, column=1)

    def on_register():
        register_window()

    register_button = tk.Button(root, text="注册", command=on_register)
    register_button.grid(row=2, column=0)
# 用户注册窗口

def get_next_read_id(connection):
    cursor = connection.cursor()
    # 查询最大的 ReadId 值，并在此基础上加一
    cursor.execute("SELECT COALESCE(MAX(ReadId), 0) + 1 FROM usr")
    next_id = cursor.fetchone()[0]
    cursor.close()
    return next_id

def register_user(connection, username, password, role):
    cursor = connection.cursor()

    # 获取下一个 ReadId
    read_id = get_next_read_id(connection)

    # 插入新用户时包括 ReadId
    insert_user = "INSERT INTO usr (ReadId, username, password, role) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(insert_user, (read_id, username, password, role))
        connection.commit()
    except pymysql.err.IntegrityError as e:
        # 如果插入失败（比如由于并发问题导致的重复键错误），回滚事务并处理异常
        connection.rollback()
        raise ValueError(f"Failed to insert user: {e}")
    finally:
        cursor.close()

    return read_id

def basic_info_window(username, read_id):
    def submit_info():
        realname = realname_entry.get()
        age = age_entry.get()
        address = address_entry.get()
        gender = gender_entry.get()

        if not realname or not age or not address or not gender:
            messagebox.showerror("错误", "所有字段不能为空")
            return

        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            insert_borrow = "INSERT INTO Reader (ReadId, name, Age, Sex, Adress) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_borrow, (read_id, realname, age, gender, address))
            connection.commit()
            messagebox.showinfo("成功", "信息提交成功")
            cursor.close()
            connection.close()
            root.destroy()

    root = tk.Toplevel()
    root.title("读者基本信息")

    tk.Label(root, text="真实姓名:").grid(row=0)
    realname_entry = tk.Entry(root)
    realname_entry.grid(row=0, column=1)

    tk.Label(root, text="年龄:").grid(row=1)
    age_entry = tk.Entry(root)
    age_entry.grid(row=1, column=1)

    tk.Label(root, text="住址:").grid(row=2)
    address_entry = tk.Entry(root)
    address_entry.grid(row=2, column=1)

    tk.Label(root, text="性别:").grid(row=3)
    gender_entry = tk.Entry(root)
    gender_entry.grid(row=3, column=1)

    tk.Button(root, text="提交", command=submit_info).grid(row=4, column=1)

def register_window():
    def register():
        username = username_entry.get()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()

        if not username or not password or not confirm_password:
            messagebox.showerror("错误", "所有字段不能为空")
            return

        if password != confirm_password:
            messagebox.showerror("错误", "密码和确认密码不一致")
            return

        connection = connect_to_database()
        if connection:
            # 调用 register_user 时传入 'user' 作为角色
            read_id = register_user(connection, username, password, 'user')
            if read_id:
                basic_info_window(username, read_id)
            connection.close()

    root = tk.Tk()
    root.title("注册新用户")

    tk.Label(root, text="用户名:").grid(row=0)
    username_entry = tk.Entry(root)
    username_entry.grid(row=0, column=1)

    tk.Label(root, text="密码:").grid(row=1)
    password_entry = tk.Entry(root, show="*")
    password_entry.grid(row=1, column=1)

    tk.Label(root, text="确认密码:").grid(row=2)
    confirm_password_entry = tk.Entry(root, show="*")
    confirm_password_entry.grid(row=2, column=1)

    tk.Button(root, text="注册", command=register).grid(row=3, column=1)

    root.mainloop()



# 全局变量，用于存储上一级界面的函数
current_interface = None

def show_management_interface(root, role, conn):
    global current_interface
    # 保存当前界面的引用
    current_interface = root
    root.title("图书管理系统")

    # 清除所有现有的界面元素
    for widget in root.winfo_children():
        widget.destroy()

    if role == 'superadmin':
        # 添加图书管理按钮
        book_management_button = tk.Button(root, text="图书管理：增删改查", command=lambda: manage_books1(root, conn))
        book_management_button.pack(pady=10)

        # 添加借阅管理按钮
        borrow_management_button = tk.Button(root, text="借阅管理：借阅、归还", command=lambda: manage_borrow1(root,conn))
        borrow_management_button.pack(pady=10)

        # 添加用户管理按钮
        user_management_button = tk.Button(root, text="用户管理：更新管理员和普通用户", command=lambda: manage_usr1(root))
        user_management_button.pack(pady=10)

    elif role == 'bookmanager':
        # 图书管理员界面
        # 添加图书管理按钮
        book_management_button = tk.Button(root, text="图书查询", command=lambda: manage_books2(root, conn))
        book_management_button.pack(pady=10)

        borrow_management_button = tk.Button(root, text="借阅管理：借阅、归还",
                                             command=lambda: manage_borrow2(root, conn))
        borrow_management_button.pack(pady=10)

    elif role == 'user':
        # 清除所有现有的界面元素
        for widget in root.winfo_children():
            widget.destroy()

        # 普通用户界面
        browse_books_button = tk.Button(root, text="查阅书籍", command=lambda: read_books(conn, text_widget))
        browse_books_button.pack(pady=10)

        current_borrows_button = tk.Button(root, text="查看当前借阅的书籍",
                                           command=lambda: query_borrow_record1_dialog(conn))
        current_borrows_button.pack(pady=10)

        user_info_button = tk.Button(root, text="查看当前的用户基本信息",
                                     command=lambda: user_info(conn, username, text_widget))
        user_info_button.pack(pady=10)

        # 返回上一级按钮
        back_button = tk.Button(root, text="返回上一级",
                                command=lambda: show_management_interface(current_interface, 'user', conn))
        back_button.pack(pady=20)

        # 文本框用于显示信息
        text_widget = tk.Text(root, height=15, width=80)
        text_widget.pack(padx=20, pady=20)


# 超管的图书管理功能
def manage_books1(root, conn):
    global current_interface
    # 清除所有现有的界面元素
    for widget in root.winfo_children():
        widget.destroy()

    # 创建一个框架来放置按钮
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)

    # 添加按钮来执行不同的数据库操作
    read_button = tk.Button(btn_frame, text="读取所有书籍", command=lambda: read_books(conn, text_widget))
    read_button.pack(pady=5)

    create_button = tk.Button(btn_frame, text="创建书籍", command=lambda: create_book_dialog(conn))
    create_button.pack(pady=5)

    update_button = tk.Button(btn_frame, text="更新书籍信息", command=lambda: update_book_dialog(conn))
    update_button.pack(pady=5)

    delete_button = tk.Button(btn_frame, text="删除书籍", command=lambda: delete_book_dialog(conn))
    delete_button.pack(pady=5)

    get_info_button = tk.Button(btn_frame, text="获取书籍信息", command=lambda: get_book_id_dialog(conn))
    get_info_button.pack(pady=5)

    # 返回上一级按钮
    back_button = tk.Button(root, text="返回上一级",
                            command=lambda: show_management_interface(current_interface, 'superadmin', conn))
    back_button.pack(pady=20)

    # 文本框用于显示书籍信息
    global text_widget
    text_widget = tk.Text(root, height=15, width=130)
    text_widget.pack(padx=20, pady=20)

# 超管的借阅图书和还书功能
def manage_borrow1(root, conn):
    global current_interface
    # 清除所有现有的界面元素
    for widget in root.winfo_children():
        widget.destroy()

    # 创建一个框架来放置按钮
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)

    # 添加按钮来执行借阅图书操作
    borrow_button = tk.Button(btn_frame, text="1. 借阅图书", command=lambda: borrow_book_dialog(conn))
    borrow_button.pack(pady=5)

    # 添加按钮来执行还书操作
    return_button = tk.Button(btn_frame, text="2. 还书", command=lambda: return_book_dialog(conn))
    return_button.pack(pady=5)

    # 添加按钮来查询个人借阅记录
    personal_record_button = tk.Button(btn_frame, text="3. 查询个人借阅记录", command=lambda: query_borrow_record1_dialog(conn))
    personal_record_button.pack(pady=5)

    # 添加按钮来查询所有借阅记录
    all_records_button = tk.Button(btn_frame, text="4. 查询所有借阅记录", command=lambda: query_borrow_record2_dialog(conn))
    all_records_button.pack(pady=5)

    # 返回上一级按钮
    back_button = tk.Button(root, text="返回上一级", command=lambda: show_management_interface(current_interface, 'superadmin', conn))
    back_button.pack(pady=20)

    # 文本框用于显示借阅信息
    global text_widget
    text_widget = tk.Text(root, height=15, width=130)
    text_widget.pack(padx=20, pady=20)

# 超管的用户管理功能
def manage_usr1(root,conn):
    # 这里添加用户管理的代码
    pass

# 退出系统
def exit_system(conn, root):
    if conn:
        conn.close()
    root.destroy()

def manage_books2(root, conn):
    global current_interface
    # 清除所有现有的界面元素
    for widget in root.winfo_children():
        widget.destroy()

    # 创建一个框架来放置按钮
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)

    # 添加按钮来执行不同的数据库操作
    read_button = tk.Button(btn_frame, text="读取所有书籍", command=lambda: read_books(conn, text_widget))
    read_button.pack(pady=5)

    update_button = tk.Button(btn_frame, text="更新书籍信息", command=lambda: update_book_dialog(conn))
    update_button.pack(pady=5)

    get_info_button = tk.Button(btn_frame, text="获取书籍信息", command=lambda: get_book_id_dialog(conn))
    get_info_button.pack(pady=5)

    # 返回上一级按钮
    back_button = tk.Button(root, text="返回上一级", command=lambda: show_management_interface(current_interface, 'bookmanager', conn))
    back_button.pack(pady=20)

    # 文本框用于显示书籍信息
    global text_widget
    text_widget = tk.Text(root, height=15, width=130)
    text_widget.pack(padx=20, pady=20)

def manage_borrow2(root, conn):
    global current_interface
    # 清除所有现有的界面元素
    for widget in root.winfo_children():
        widget.destroy()

    # 创建一个框架来放置按钮
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)

    # 添加按钮来执行借阅图书操作
    borrow_button = tk.Button(btn_frame, text="1. 借阅图书", command=lambda: borrow_book_dialog(conn))
    borrow_button.pack(pady=5)

    # 添加按钮来执行还书操作
    return_button = tk.Button(btn_frame, text="2. 还书", command=lambda: return_book_dialog(conn))
    return_button.pack(pady=5)

    # 添加按钮来查询个人借阅记录
    personal_record_button = tk.Button(btn_frame, text="3. 查询个人借阅记录", command=lambda: query_borrow_record1_dialog(conn))
    personal_record_button.pack(pady=5)

    # 添加按钮来查询所有借阅记录
    all_records_button = tk.Button(btn_frame, text="4. 查询所有借阅记录", command=lambda: query_borrow_record2_dialog(conn))
    all_records_button.pack(pady=5)

    # 返回上一级按钮
    back_button = tk.Button(root, text="返回上一级", command=lambda: show_management_interface(current_interface, 'bookmanager', conn))
    back_button.pack(pady=20)

    # 文本框用于显示借阅信息
    global text_widget
    text_widget = tk.Text(root, height=15, width=130)
    text_widget.pack(padx=20, pady=20)

def manage_books3(root, conn):
    global current_interface
    # 清除所有现有的界面元素
    for widget in root.winfo_children():
        widget.destroy()

    # 创建一个框架来放置按钮
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)

    # 添加按钮来执行不同的数据库操作
    read_button = tk.Button(btn_frame, text="读取所有书籍", command=lambda: read_books(conn, text_widget))
    read_button.pack(pady=5)

    get_info_button = tk.Button(btn_frame, text="获取书籍信息", command=lambda: get_book_id_dialog(conn))
    get_info_button.pack(pady=5)

    # 返回上一级按钮
    back_button = tk.Button(root, text="返回上一级", command=lambda: show_management_interface(current_interface, 'user', conn))
    back_button.pack(pady=20)

    # 文本框用于显示书籍信息
    global text_widget
    text_widget = tk.Text(root, height=15, width=130)
    text_widget.pack(padx=20, pady=20)
#创建书籍
def create_book_dialog(conn):
    try:
        # 使用try-except结构来捕获可能的异常
        book_id = simpledialog.askinteger("输入", "书籍ID:", parent=root, minvalue=1)
        if book_id is None:
            raise ValueError("书籍ID不能为空")
        book_name = simpledialog.askstring("输入", "书名:", parent=root)
        if not book_name:
            raise ValueError("书名不能为空")
        publisher_action_data = simpledialog.askstring("输入", "发行日期:", parent=root)
        if not publisher_action_data:
            raise ValueError("发行日期不能为空")
        publisher = simpledialog.askstring("输入", "出版商:", parent=root)
        if not publisher:
            raise ValueError("出版商不能为空")
        book_rack_id = simpledialog.askinteger("输入", "书架ID:", parent=root, minvalue=1)
        if book_rack_id is None:
            raise ValueError("书架ID不能为空")
        room_id = simpledialog.askinteger("输入", "书架房间号:", parent=root, minvalue=1)
        if room_id is None:
            raise ValueError("书架房间号不能为空")

        create_book(conn, book_id, book_name, publisher_action_data, publisher, book_rack_id, room_id)
    except ValueError as e:
        tk.messagebox.showerror("错误", str(e))

#更新书籍
def update_book_dialog(conn):
    try:
        book_id = simpledialog.askinteger("输入", "书籍ID:", parent=root, minvalue=1)
        new_book_name = simpledialog.askstring("输入", "新书名（留空则不修改）:", parent=root)
        new_publisher_action_data = simpledialog.askstring("输入", "新发行日期（留空则不修改）:", parent=root)
        new_publisher = simpledialog.askstring("输入", "新出版商（留空则不修改）:", parent=root)
        new_book_rack_id = simpledialog.askinteger("输入", "新书架ID（留空则不修改）:", parent=root, minvalue=0)
        new_room_id = simpledialog.askinteger("输入", "新书架房间号（留空则不修改）:", parent=root, minvalue=0)

        update_book(conn, book_id, new_book_name, new_publisher_action_data, new_publisher, new_book_rack_id,
                    new_room_id)
    except ValueError as e:
        tk.messagebox.showerror("错误", str(e))
#删除书籍
def delete_book_dialog(conn):
    try:
        book_id = simpledialog.askinteger("输入", "书籍ID:", parent=root, minvalue=1)
        delete_book(conn, book_id)
    except ValueError as e:
        tk.messagebox.showerror("错误", str(e))

#书ID查找
def get_book_id_dialog(conn):
    try:
        book_id = simpledialog.askinteger("输入", "书籍ID:", parent=root, minvalue=1)
        get_book_id(conn, book_id)
    except ValueError as e:
        tk.messagebox.showerror("错误", str(e))
#查询所有书籍
def read_books(conn, text_widget):
    # 遍历当前所有书籍
    query = "SELECT * FROM Books"
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    text_widget.delete(1.0, tk.END)  # 清空文本框内容
    for row in rows:
        # 假设字段顺序是：BookId, BookName, PublisherActionData, Publisher, BookRackId, RoomID
        text = f"书籍ID: {row[0]}, 书名: {row[1]}, 发行日期: {row[2]}, 出版商: {row[3]}, 书架ID: {row[4]}, 书架房间号: {row[5]}\n"
        text_widget.insert(tk.END, text)  # 将文本插入到文本框中
    text_widget.insert(tk.END, "查询完毕。\n")

#创建书籍
def create_book(conn, book_id, book_name, publisher_action_data, publisher, book_rack_id, room_id):
    query = "INSERT INTO Books (BookId, BookName, PublisherActionData, Publisher, BookRackId, RoomID) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    # 确保所有参数都是字符串类型
    params = (str(book_id), str(book_name), str(publisher_action_data), str(publisher), str(book_rack_id), str(room_id))
    cursor.execute(query, params)
    conn.commit()
    text_widget.insert(tk.END, "添加书籍成功。\n")
#更新书籍的信息
def update_book(conn, book_id, new_book_name=None, new_publisher_action_data=None, new_publisher=None, new_book_rack_id=0, new_room_id=0):
    query = "UPDATE Books SET "
    params = []
    if new_book_name:
        query += "BookName = %s, "
        params.append(new_book_name)
    if new_publisher_action_data:
        query += "PublisherActionData = %s, "
        params.append(new_publisher_action_data)
    if new_publisher:
        query += "Publisher = %s, "
        params.append(new_publisher)
    if new_book_rack_id != 0:
        query += "BookRackId = %s, "
        params.append(new_book_rack_id)
    if new_room_id != 0:
        query += "RoomID = %s, "
        params.append(new_room_id)
    query = query.rstrip(', ') + " WHERE BookId = %s"
    params.append(book_id)
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    conn.commit()
    text_widget.insert(tk.END, "更新书籍成功。\n")

#删除书籍
def delete_book(conn, book_id):
    query = "DELETE FROM Books WHERE BookId = %s"
    cursor = conn.cursor()
    # 将 book_id 放入元组中
    cursor.execute(query, (book_id,))
    conn.commit()
    text_widget.insert(tk.END, "书籍书籍成功。\n")

#通过ID来获取书籍信息
def get_book_id(conn, book_id):
    query = "SELECT * FROM Books WHERE BookId = %s"
    cursor = conn.cursor()
    cursor.execute(query, (book_id,))
    row = cursor.fetchone()
    if row:
        text_widget.insert(tk.END, f"Book ID: {row[0]}, Name: {row[1]}, Action: {row[2]}, Publisher: {row[3]}, BookRackId: {row[4]}, RoomID: {row[5]}\n")
    else:
        text_widget.insert(tk.END, "查询失败，没有找到该书籍。\n")

def borrow_book_dialog(conn):
    try:
        reader_name = simpledialog.askstring("输入", "读者姓名:", parent=root)
        book_id = simpledialog.askinteger("输入", "书籍ID:", parent=root, minvalue=1)
        if reader_name and book_id:
            borrow_book(conn, book_id, reader_name)
        else:
            messagebox.showerror("错误", "读者姓名和书籍ID不能为空")
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def return_book_dialog(conn):
    try:
        book_id = simpledialog.askinteger("输入", "书籍ID:", parent=root, minvalue=1)
        return_date = simpledialog.askstring("输入", "归还日期 (格式YYYY-MM-DD HH:MM:SS):", parent=root)
        if book_id and return_date:
            return_book(conn, book_id, return_date)
        else:
            messagebox.showerror("错误", "书籍ID和归还日期不能为空")
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def query_borrow_record1_dialog(conn):
    try:
        username = simpledialog.askstring("输入", "读者姓名:", parent=root)
        if username:
            query_borrow_records1(conn, username)
        else:
            messagebox.showerror("错误", "读者姓名不能为空")
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def query_borrow_record2_dialog(conn):
    query_borrow_records2(conn)  # 直接调用函数，不需要用户输入


def get_current_date_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 查询单个人当前借阅记录
def query_borrow_records1(conn, username):
    query = """
        SELECT B.BookId, B.BorrowDate, B.ReturnDate, A.BookName
        FROM usr U
        JOIN Borrow B ON U.ReadId = B.ReadId
        JOIN Books A ON B.BookId = A.BookId
        WHERE U.username = %s
        """
    cursor = conn.cursor()
    cursor.execute(query, (username,))
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            # 将文本插入到文本框中
            text = f"书籍ID: {row[0]}, 书名: {row[3]}, 借阅日期: {row[1]}, 归还日期: {row[2]}\n"
            text_widget.insert(tk.END, text)
    else:
        text_widget.insert(tk.END, "没有找到借阅记录。\n")
    cursor.close()

# 查询所有借阅记录
def query_borrow_records2(conn):
    query = """
        SELECT B.BookId, B.BorrowDate, B.ReturnDate, A.BookName, U.username
        FROM usr U
        JOIN Borrow B ON U.ReadId = B.ReadId
        JOIN Books A ON B.BookId = A.BookId
        WHERE B.ReturnDate = '9999-12-31 23:59:59'
        ORDER BY B.BookId ASC
        """
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        text = f"书籍ID: {row[0]}, 书名: {row[3]}, 借阅日期: {row[1]}, 归还日期: {row[2]}, 读者: {row[4]}"
        text_widget.insert(tk.END, text)  # 将文本插入到文本框中
        text_widget.insert(tk.END, "查询完毕。\n")

    cursor.close()

# 归还书籍
def return_book(conn, book_id, return_date):
    query = "UPDATE Borrow SET ReturnDate = %s WHERE BookId = %s"
    cursor = conn.cursor()
    cursor.execute(query, (return_date, book_id))
    conn.commit()
    try:
        cursor.execute(query, (return_date, book_id))  # 注意参数的顺序
        conn.commit()
        text_widget.insert(tk.END, "书籍归还成功。\n")
    except Exception as e:
        text =f"执行语句失败: {e}"
        text_widget.insert(tk.END,text)
    cursor.close()

# 借书函数
def borrow_book(conn, book_id, reader_name):
    query_get_read_id = "SELECT ReadId FROM usr WHERE username = %s"
    cursor = conn.cursor()
    cursor.execute(query_get_read_id, (reader_name,))
    read_id = cursor.fetchone()
    if read_id:
        borrow_date = get_current_date_time()
        return_date = "9999-12-31 23:59:59"  # 未来的日期作为还书日期
        max_borrow_book_id_query = "SELECT MAX(BorrowBookId) FROM Borrow"
        cursor.execute(max_borrow_book_id_query)
        max_id = cursor.fetchone()
        new_borrow_book_id = max_id[0] + 1 if max_id[0] else 1

        insert_borrow_query = """
                    INSERT INTO Borrow (BorrowBookId, BookId, ReadId, BorrowDate, ReturnDate)
                    VALUES (%s, %s, %s, %s, %s)
                    """
        cursor.execute(insert_borrow_query, (new_borrow_book_id, book_id, read_id[0], borrow_date, return_date))
        conn.commit()
        text_widget.insert(tk.END, "书籍借阅成功\n")
    else:
        text_widget.insert(tk.END, "未找到读者ID，无法借阅书籍\n")
    cursor.close()




if __name__ == "__main__":
    root = tk.Tk()
    username_var = tk.StringVar()
    password_var = tk.StringVar()
    login_window(root, username_var, password_var)
    root.mainloop()