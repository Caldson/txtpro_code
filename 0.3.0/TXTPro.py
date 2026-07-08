import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
root = tk.Tk()
root.title("TXTPro")
root.resizable(False, False)
root.geometry("600x250")
# 标签页数据：{tab_id: {'file_path': str, 'original_content': str, 'text_widget': widget, 'line_number_widget': widget, 'v_scrollbar': widget, 'h_scrollbar': widget}}
tabs_data = {}
tab_counter = 0
status_label = None  # 状态栏标签，用于显示光标位置
filetypes = [("文本", "*.txt"), ("Python", "*.py"), ("JSON", "*.json"), ("BAT", "*.bat"), ("Ruby", "*.rb"), ("JavaScript", "*.js"), ("HTML", "*.html"), ("任何（实验）", "*.*")]
cfiletypes = filetypes[0:-2]
applog = """当前版本：0.3.0
0.1.0：发布TXTPro软件
0.1.1：修复bug
0.2.0：修复bug并节约空间，添加大量功能，更改软件图标
0.3.0：（重量级更新）新增显示行号、统计字符/行数、标签页功能、显示光标位置，修复问题，删除转换为Mathematical Font功能"""
def on_notebook_click(event):
    """处理标签页点击事件，检测是否点击了关闭按钮（×）"""
    # 获取点击位置的标签页索引
    try:
        clicked_tab = notebook.index(f"@{event.x},{event.y}")
        if clicked_tab == -1:
            return
    except:
        return
    
    # 获取当前选中的标签页索引
    try:
        current_selected = notebook.index(notebook.select())
    except:
        current_selected = -1
    
    # 获取该标签页的框架
    try:
        tab_frame = notebook.nametowidget(notebook.tabs()[clicked_tab])
    except:
        return
    
    if tab_frame not in tabs_data:
        return
    
    # 获取标签页文本
    try:
        tab_id = notebook.tabs()[clicked_tab]
        tab_text = notebook.tab(tab_id, "text")
    except:
        # 如果无法获取文本，直接选择标签页，不关闭
        return
    
    # 计算标签页的累积宽度来判断点击位置
    # 遍历所有标签页，计算到点击标签页的累积宽度
    total_width = 0
    for i in range(clicked_tab):
        try:
            prev_tab_id = notebook.tabs()[i]
            prev_tab_text = notebook.tab(prev_tab_id, "text")
            # 估算标签页宽度（文本长度 * 字符宽度 + 边距）
            char_width = 7  # 近似每个字符7像素
            padding = 25  # 标签页的内边距
            prev_tab_width = len(prev_tab_text) * char_width + padding
            total_width += prev_tab_width
        except:
            continue
    
    # 计算当前标签页的宽度
    char_width = 7
    padding = 25
    current_tab_width = len(tab_text) * char_width + padding
    
    # 计算相对于当前标签页的x坐标
    relative_x = event.x - total_width
    
    # 检查是否点击了标签页左侧区域（关闭按钮区域，× 在左边）
    # 只有当点击的是当前已选中的标签页时，才检查关闭按钮
    # 这样可以避免切换标签页时误关闭
    close_width = 10  # 关闭区域宽度，只在最左边的小区域
    if clicked_tab == current_selected and relative_x >= 0 and relative_x <= close_width:
        # 确认点击了关闭按钮区域，阻止默认行为并关闭标签页
        close_tab(tab_frame)
        return "break"  # 阻止事件继续传播
    
    # 如果不是点击关闭按钮，让默认行为处理标签页切换
    # 不返回任何值，让事件正常传播

def get_current_tab_data():
    """获取当前活动标签页的数据"""
    current_tab = notebook.select()
    if not current_tab:
        return None
    
    # notebook.select() 可能返回字符串ID，需要转换为Frame对象
    try:
        # 尝试直接获取
        if current_tab in tabs_data:
            return tabs_data[current_tab]
        # 如果不是，尝试通过nametowidget转换
        tab_frame = notebook.nametowidget(current_tab)
        if tab_frame in tabs_data:
            return tabs_data[tab_frame]
    except:
        pass
    
    return None

def is_content_modified(tab_id=None):
    """检查指定标签页的内容是否被修改"""
    if tab_id is None:
        tab_id = notebook.select()
    if not tab_id:
        return False
    
    # 确保tab_id是Frame对象
    try:
        if tab_id not in tabs_data:
            tab_id = notebook.nametowidget(tab_id)
        if tab_id not in tabs_data:
            return False
    except:
        return False
    
    tab = tabs_data[tab_id]
    text_widget = tab['text_widget']
    current_content = text_widget.get("1.0", tk.END + "-1c")
    return current_content != tab['original_content']
def create_new_tab(file_path=None, content=""):
    """创建新标签页"""
    # 检查标签页数量限制（最多10个）
    if len(tabs_data) >= 10:
        messagebox.showwarning("提示", "标签页数量已达到上限（最多10个），请先关闭一些标签页")
        return None
    
    global tab_counter
    tab_counter += 1
    
    # 创建标签页框架
    tab_frame = tk.Frame(notebook)
    tab_text = "新文件" if not file_path else os.path.basename(file_path)
    
    # 添加标签页
    notebook.add(tab_frame, text=tab_text)
    notebook.select(tab_frame)
    
    # 创建上半部分（行号和文本区域）
    top_text_frame = tk.Frame(tab_frame)
    top_text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # 行号显示区域
    line_number_widget = tk.Text(top_text_frame, width=4, padx=5, pady=5, 
                                  state=tk.DISABLED, wrap=tk.NONE, 
                                  bg="#f0f0f0", fg="#666666", 
                                  font=("Consolas", 10), relief=tk.FLAT)
    line_number_widget.pack(side=tk.LEFT, fill=tk.Y)
    
    # 创建文本和垂直滚动条的容器
    text_container = tk.Frame(top_text_frame)
    text_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # 文本框（编辑框）
    text_widget = tk.Text(text_container, wrap=tk.NONE, padx=5, pady=5,
                          font=("Consolas", 10))
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # 垂直滚动条
    v_scrollbar = tk.Scrollbar(text_container, orient=tk.VERTICAL, command=text_widget.yview)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # 水平滚动条
    h_scrollbar = tk.Scrollbar(tab_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # 保存标签页数据（必须在绑定事件之前）
    tabs_data[tab_frame] = {
        'file_path': file_path,
        'original_content': content,
        'text_widget': text_widget,
        'line_number_widget': line_number_widget,
        'v_scrollbar': v_scrollbar,
        'h_scrollbar': h_scrollbar
    }
    
    # 配置文本框的滚动命令（使用tab_frame作为标识符）
    text_widget.config(yscrollcommand=lambda *args, tf=tab_frame: (v_scrollbar.set(*args), sync_scroll(tf, *args)))
    text_widget.config(xscrollcommand=h_scrollbar.set)
    
    # 绑定事件（使用tab_frame作为标识符）
    text_widget.bind('<KeyRelease>', lambda e, tf=tab_frame: on_text_change(tf))
    text_widget.bind('<Button-1>', lambda e, tf=tab_frame: on_text_change(tf))
    text_widget.bind('<ButtonRelease-1>', lambda e: root.after_idle(update_cursor_position))
    text_widget.bind('<Left>', lambda e: root.after_idle(update_cursor_position))
    text_widget.bind('<Right>', lambda e: root.after_idle(update_cursor_position))
    text_widget.bind('<Up>', lambda e: root.after_idle(update_cursor_position))
    text_widget.bind('<Down>', lambda e: root.after_idle(update_cursor_position))
    text_widget.bind('<Home>', lambda e: root.after_idle(update_cursor_position))
    text_widget.bind('<End>', lambda e: root.after_idle(update_cursor_position))
    
    # 插入内容
    if content:
        text_widget.insert("1.0", content)
    
    # 更新行号
    update_line_numbers(tab_frame)
    
    # 初始化光标位置显示
    root.after_idle(update_cursor_position)
    
    return tab_frame

def create_file():
    """创建新文件"""
    file_path = filedialog.asksaveasfilename(
        title="创建文件",
        defaultextension=".txt",
        filetypes=cfiletypes
    )
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("")
            create_new_tab(file_path, "")
            messagebox.showinfo("成功", f"文件已创建: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"创建文件失败: {str(e)}")
def select_file():
    """选择并打开文件"""
    file_path = filedialog.askopenfilename(
        title="选择文件",
        filetypes=filetypes
    )
    if file_path:
        # 检查文件是否已经在标签页中打开
        for tab_id, tab_data in tabs_data.items():
            if tab_data['file_path'] == file_path:
                notebook.select(tab_id)
                return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            create_new_tab(file_path, content)
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败: {str(e)}")
def save_file():
    """保存当前标签页的文件"""
    tab_data = get_current_tab_data()
    if not tab_data:
        messagebox.showwarning("提示", "没有活动的标签页")
        return
    
    text_widget = tab_data['text_widget']
    content = text_widget.get("1.0", tk.END + "-1c")
    
    # 如果没有文件路径，弹出保存对话框
    if not tab_data['file_path']:
        file_path = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".txt",
            filetypes=cfiletypes
        )
        if not file_path:
            return  # 用户取消了保存
        
        # 更新标签页的文件路径
        tab_data['file_path'] = file_path
    else:
        file_path = tab_data['file_path']
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        tab_data['original_content'] = content
        # 更新标签页标题
        update_tab_title(notebook.select())
        messagebox.showinfo("成功", "文件已保存")
    except Exception as e:
        messagebox.showerror("错误", f"保存文件失败: {str(e)}")
def update_line_numbers(tab_id=None):
    """更新指定标签页的行号显示"""
    if tab_id is None:
        tab_id = notebook.select()
    if not tab_id:
        return
    
    # 确保tab_id是Frame对象
    try:
        if tab_id not in tabs_data:
            tab_id = notebook.nametowidget(tab_id)
        if tab_id not in tabs_data:
            return
    except:
        return
    
    tab_data = tabs_data[tab_id]
    text_widget = tab_data['text_widget']
    line_number_widget = tab_data['line_number_widget']
    
    # 获取文本内容（不包括末尾的换行符）
    content = text_widget.get("1.0", tk.END + "-1c")
    
    # 计算行数
    if not content:
        line_count = 1  # 空文件至少显示一行
    else:
        line_count = content.count('\n') + 1  # 行数 = 换行符数 + 1
    
    # 生成行号字符串
    line_numbers = ""
    for i in range(1, line_count + 1):
        line_numbers += str(i) + "\n"
    
    line_number_widget.config(state=tk.NORMAL)
    line_number_widget.delete("1.0", tk.END)
    line_number_widget.insert("1.0", line_numbers)
    line_number_widget.config(state=tk.DISABLED)
    
    # 同步滚动
    line_number_widget.yview_moveto(text_widget.yview()[0])

def sync_scroll(tab_id, *args):
    """同步指定标签页的两个文本区域的滚动"""
    if tab_id not in tabs_data:
        return
    tab_data = tabs_data[tab_id]
    tab_data['line_number_widget'].yview_moveto(tab_data['text_widget'].yview()[0])

def update_tab_title(tab_id=None):
    """更新标签页标题，显示未保存标记"""
    if tab_id is None:
        tab_id = notebook.select()
    if not tab_id:
        return
    
    # 保存原始tab_id用于更新notebook标签
    original_tab_id = tab_id
    
    # 确保tab_id是Frame对象
    try:
        if tab_id not in tabs_data:
            tab_id = notebook.nametowidget(tab_id)
        if tab_id not in tabs_data:
            return
    except:
        return
    
    tab_data = tabs_data[tab_id]
    if tab_data['file_path']:
        base_name = os.path.basename(tab_data['file_path'])
        if is_content_modified(tab_id):
            title = f"*{base_name}"
        else:
            title = base_name
    else:
        if is_content_modified(tab_id):
            title = "*新文件"
        else:
            title = "新文件"
    
    # 更新标签页文本，包含 × 符号（关闭按钮，在左边）
    # 使用原始tab_id来更新notebook标签（notebook.tab需要原始ID）
    try:
        notebook.tab(original_tab_id, text=title)
    except:
        # 如果失败，尝试使用tab_id
        try:
            notebook.tab(tab_id, text=title)
        except:
            pass

def update_cursor_position():
    """更新光标位置显示"""
    tab_data = get_current_tab_data()
    if not tab_data or status_label is None:
        return
    
    text_widget = tab_data['text_widget']
    try:
        # 获取光标位置（例如 "1.5" 表示第1行第5列）
        cursor_pos = text_widget.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        status_label.config(text=f"行 {line}, 列 {int(col)}")
    except:
        status_label.config(text="")

def on_text_change(tab_id=None):
    """文本内容变化时更新行号"""
    if tab_id is None:
        tab_id = notebook.select()
    root.after_idle(lambda: (update_line_numbers(tab_id), update_tab_title(tab_id), update_cursor_position()))

def show_statistics():
    """显示当前标签页的统计信息"""
    tab_data = get_current_tab_data()
    if not tab_data:
        return
    
    text_widget = tab_data['text_widget']
    content = text_widget.get("1.0", tk.END + "-1c")
    char_count = len(content)
    line_count = content.count('\n')
    if content and not content.endswith('\n'):
        line_count += 1
    elif not content:
        line_count = 0
    messagebox.showinfo("统计", f"字符：{char_count}\n行数：{line_count}")

def show_log():
    messagebox.showinfo("更新历史", applog)
def close_tab(tab_id):
    """关闭指定标签页"""
    if tab_id not in tabs_data:
        return False
    
    tab_data = tabs_data[tab_id]
    if tab_data['file_path'] and is_content_modified(tab_id):
        result = messagebox.askyesnocancel("提示", "文件有未保存的修改，是否保存？")
        if result is True:
            # 临时切换到该标签页并保存
            notebook.select(tab_id)
            save_file()
        elif result is None:
            return False  # 取消关闭
    
    # 删除标签页
    notebook.forget(tab_id)
    del tabs_data[tab_id]
    return True

def show_tab_context_menu(event):
    """显示标签页右键菜单"""
    # 获取点击位置的标签页索引
    try:
        clicked_tab = notebook.index(f"@{event.x},{event.y}")
        if clicked_tab == -1:
            return
    except:
        return
    
    # 获取该标签页的框架
    try:
        tab_id = notebook.tabs()[clicked_tab]
        tab_frame = notebook.nametowidget(tab_id)
    except:
        return
    
    if tab_frame not in tabs_data:
        return
    
    # 切换到被点击的标签页
    notebook.select(tab_frame)
    
    # 创建右键菜单
    context_menu = tk.Menu(root, tearoff=0)
    
    # 添加"保存"选项
    tab_data = tabs_data[tab_frame]
    if tab_data['file_path']:  # 只有当标签页有文件路径时才显示保存选项
        context_menu.add_command(label="保存", command=save_file)
    else:
        context_menu.add_command(label="保存", state=tk.DISABLED)
    
    # 添加"关闭"选项
    context_menu.add_command(label="关闭", command=lambda tf=tab_frame: close_tab(tf))
    
    # 在鼠标位置显示菜单
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()

def on_tab_closed(event):
    """处理标签页关闭事件（通过鼠标中键）"""
    if event.num == 2:  # 鼠标中键
        current_tab = notebook.select()
        if current_tab:
            close_tab(current_tab)

def on_tab_changed(event):
    """标签页切换时更新行号和标题"""
    current_tab = notebook.select()
    if current_tab:
        update_line_numbers(current_tab)
        update_tab_title(current_tab)
        update_cursor_position()

def on_closing():
    """窗口关闭时检查所有标签页"""
    tabs_to_close = list(tabs_data.keys())
    for tab_id in tabs_to_close:
        if not close_tab(tab_id):
            return  # 如果用户取消关闭某个标签页，则不关闭窗口
    root.destroy()
# 初始化
top_frame = tk.Frame(root)
top_frame.pack(pady=10, padx=10, fill="x")
button_frame = tk.Frame(top_frame)
button_frame.pack(side="left", anchor="w")
# 按钮
create_file_button = tk.Button(button_frame, text="创建", command=create_file)
create_file_button.pack(side="left", padx=(0, 10))
select_file_button = tk.Button(button_frame, text="选择文件", command=select_file)
select_file_button.pack(side="left", padx=(0, 10))
save_button = tk.Button(button_frame, text="保存", command=save_file)
save_button.pack(side="left", padx=(0, 10))
statistics_button = tk.Button(button_frame, text="统计", command=show_statistics)
statistics_button.pack(side="left", padx=(0, 10))
new_tab_button = tk.Button(button_frame, text="新建标签页", command=lambda: create_new_tab())
new_tab_button.pack(side="left")
# 右上角：光标位置显示和更新历史按钮
status_label = tk.Label(top_frame, text="", font=("Consolas", 8), fg="#666666")
status_label.pack(side="right", padx=(0, 10))
log_button = tk.Button(top_frame, text="更新历史", command=show_log)
log_button.pack(side="right")
# 创建Notebook（标签页容器）
notebook = ttk.Notebook(root)
notebook.pack(pady=10, padx=10, fill="both", expand=True)
# 绑定标签页事件
notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
notebook.bind("<Button-2>", on_tab_closed)  # 鼠标中键关闭标签页
notebook.bind("<Button-3>", show_tab_context_menu)   # 鼠标右键显示菜单（Windows）
# 关闭窗口
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()