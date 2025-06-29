# 图书管理系统项目介绍

## 一、项目概述
本图书管理系统是一个基于 Python 语言开发的桌面应用程序，利用 Tkinter 库构建了图形用户界面（GUI），并通过 PyMySQL 实现与 MySQL 数据库的连接，实现了图书信息管理、借阅管理、用户管理等核心功能。系统支持三种用户角色：超级管理员、图书管理员和普通用户，不同角色拥有不同的操作权限，以满足多样化的图书管理需求。

## 二、功能特性
### 1. 用户认证
- **登录功能**：用户输入用户名和密码，系统验证其身份信息，根据验证结果判断用户角色（超级管理员、图书管理员、普通用户），并显示相应的管理界面。
- **注册功能**：新用户可以进行注册，注册成功后需完善个人基本信息，系统会自动分配唯一的读者 ID。

### 2. 超级管理员功能
- **图书管理**：可以对图书信息进行增删改查操作，包括添加新书籍、更新书籍信息、删除书籍以及查询书籍详细信息。
- **借阅管理**：处理图书的借阅和归还业务，查询个人和所有借阅记录。
- **用户管理**：可对管理员和普通用户信息进行更新。

### 3. 图书管理员功能
- **图书查询**：读取所有书籍信息，更新书籍信息，获取指定书籍的详细信息。
- **借阅管理**：处理图书的借阅和归还业务，查询个人和所有借阅记录。

### 4. 普通用户功能
- **查阅书籍**：查看所有书籍的基本信息。
- **查看借阅记录**：查询当前个人的借阅记录。
- **查看用户信息**：查看个人的基本信息。

## 三、代码结构与模块
### 1. 数据库连接模块
```python
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
        conn = pymysql.connect(**conn_str)
        return conn
    except Exception as e:
        messagebox.showerror("数据库连接失败", str(e))
        return None
```
该函数负责建立与 MySQL 数据库的连接，若连接失败会弹出错误提示框。

### 2. SQL 查询执行模块
```python
def execute_query(conn, query):
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("查询失败", str(e))
        return False
```
用于执行 SQL 查询并提交事务，若执行失败会弹出错误提示框。

### 3. 用户认证模块
```python
def verify_credentials(conn, username, password):
    query = "SELECT role FROM usr WHERE username = %s AND password = %s"
    cursor = conn.cursor()
    cursor.execute(query, (username, password))
    row = cursor.fetchone()
    if row:
        role = row[0]
        if role == 'superadmin':
            messagebox.showinfo("登录成功", "超级管理员登录成功！")
            return 'superadmin'
        elif role == 'bookmanager':
            messagebox.showinfo("登录成功", "图书管理员登录成功！")
            return 'bookmanager'
        elif role == 'user':
            messagebox.showinfo("登录成功", "普通用户登录成功！")
            return 'user'
```
根据输入的用户名和密码验证用户身份，并返回用户角色。

### 4. GUI 界面模块
- **登录界面**：提供用户名和密码输入框，以及登录和注册按钮。
```python
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
                for widget in root.winfo_children():
                    widget.destroy()
                show_management_interface(root, role, conn)
            else:
                messagebox.showerror("登录失败", "用户名或密码错误。")

    login_button = tk.Button(root, text="登录", command=login)
    login_button.grid(row=2, column=1)

    def on_register():
        register_window()

    register_button = tk.Button(root, text="注册", command=on_register)
    register_button.grid(row=2, column=0)
```
- **管理界面**：根据用户角色显示不同的操作按钮，如图书管理、借阅管理、用户管理等。

### 5. 业务逻辑模块
包含图书管理、借阅管理、用户管理等具体业务逻辑的实现函数，如创建书籍、更新书籍信息、借阅图书、归还图书等。

## 四、使用方法
### 1. 环境准备
- 安装 Python 环境（建议 Python 3.6 及以上版本）。
- 安装所需的第三方库：`pymysql`、`tkinter`。可以使用以下命令进行安装：
```bash
pip install pymysql
```

### 2. 数据库配置
- 创建名为 `图书管理系统` 的 MySQL 数据库，并根据代码中的表结构创建相应的表（`usr`、`Books`、`Borrow`、`Reader` 等）。
- 修改 `connect_to_database` 函数中的数据库连接参数，确保能够正确连接到数据库。

### 3. 运行程序
将代码保存为 `bookmanage.py` 文件，在终端中运行以下命令：
```bash
python bookmanage.py
```
程序启动后，会显示登录界面，用户可以输入用户名和密码进行登录，或点击注册按钮进行新用户注册。

## 五、注意事项
- 请确保 MySQL 数据库服务正常运行，并且数据库连接参数正确。
- 在进行数据库操作时，如插入、更新、删除数据，要注意数据的完整性和一致性，避免出现错误。
- 本系统仅为示例项目，在实际应用中可根据需求进行功能扩展和优化。
