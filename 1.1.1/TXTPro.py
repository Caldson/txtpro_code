import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import os
import subprocess
import threading
from openai import OpenAI
root = tk.Tk()
root.title("TXTPro")
root.geometry("800x400")
tabs_data = {}
tab_counter = 0
filetypes = [("文本", "*.txt"), ("Python", "*.py"), ("JSON", "*.json"), ("BAT", "*.bat"), ("Ruby", "*.rb"), ("JavaScript", "*.js"), ("HTML", "*.html"), ("任何（实验）", "*.*")]
cfiletypes = filetypes[0:-2]
applog = """当前版本：1.1.1
0.1.0：发布TXTPro软件
0.1.1：修复bug
0.2.0：修复bug并节约空间，添加大量功能，更改软件图标
0.3.0：（重量级更新）新增显示行号、统计字符/行数、标签页功能、显示光标位置，修复问题，删除转换为Mathematical Font功能
0.4.0：删除×按钮的残留部分节约空间，绑定更多按键，添加查找文本功能
0.4.1：修复问题、新增打开文件夹功能、将原本创建新文件和标签页合二为一
0.4.2：增加标签页数量上限至25个、hex功能
1.1.0：（重量级更新）将DeepSeek引入到TXTPro中，分类按钮
重新发布1.1.0：1.1.0补丁，修复deepseek_api.txt路径无法使用的问题
1.1.1：支持运行Python文件，修复Ctrl-S无法保存文件的问题"""

DEEPSEEK_API_PATH = r"C:\Users\Public\Documents\deepseek_api.txt"

# 文件夹相关全局变量
current_folder = None
folder_files = []
folder_listbox = None
# 打开文件夹函数
def open_folder():
    global current_folder, folder_files
    folder_path = filedialog.askdirectory(title="选择文件夹")
    if not folder_path:
        return
    current_folder = folder_path
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        folder_files = files
        update_folder_listbox()
    except Exception as e:
        messagebox.showerror("错误", f"读取文件夹失败: {str(e)}")

# 刷新文件列表函数
def update_folder_listbox():
    if folder_listbox is not None:
        folder_listbox.delete(0, tk.END)
        for f in folder_files:
            folder_listbox.insert(tk.END, f)

# 定时刷新文件夹列表
def auto_refresh_folder():
    if current_folder:
        try:
            files = [f for f in os.listdir(current_folder) if os.path.isfile(os.path.join(current_folder, f))]
            global folder_files
            folder_files = files
            update_folder_listbox()
        except Exception:
            pass
    root.after(1*1000, auto_refresh_folder)

root.after(1*1000, auto_refresh_folder)
# 查找文本功能
def show_find_dialog():
    tab_data = get_current_tab_data()
    if not tab_data:
        messagebox.showwarning("提示", "没有活动的标签页")
        return
    text_widget = tab_data['text_widget']
    # 弹窗
    find_win = tk.Toplevel(root)
    find_win.title("查找文本")
    find_win.resizable(False, False)
    find_win.transient(root)
    tk.Label(find_win, text="查找内容:").grid(row=0, column=0, padx=6, pady=6)
    find_entry = tk.Entry(find_win, width=24)
    find_entry.grid(row=0, column=1, padx=6, pady=6)

    def highlight_all():
        text_widget.tag_remove('find_highlight', '1.0', tk.END)
        keyword = find_entry.get()
        if not keyword:
            return
        start = '1.0'
        count = 0
        while True:
            idx = text_widget.search(keyword, start, stopindex=tk.END, nocase=1)
            if not idx:
                break
            end = f"{idx}+{len(keyword)}c"
            text_widget.tag_add('find_highlight', idx, end)
            start = end
            count += 1
        text_widget.tag_config('find_highlight', background='#ffe066', foreground='#d2691e')
        if count == 0:
            messagebox.showinfo("查找结果", "未找到内容")
        else:
            # 跳转到第一个匹配
            text_widget.mark_set(tk.INSERT, text_widget.tag_nextrange('find_highlight', '1.0')[0])
            text_widget.see(text_widget.tag_nextrange('find_highlight', '1.0')[0])
            folder_path = filedialog.askdirectory(title="选择文件夹")
            if not folder_path:
                return
            current_folder = folder_path
            # 获取文件夹下所有文件（不递归）
            try:
                files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                folder_files = files
                update_folder_listbox()
            except Exception as e:
                messagebox.showerror("错误", f"读取文件夹失败: {str(e)}")

        def update_folder_listbox():
            if folder_listbox is not None:
                folder_listbox.delete(0, tk.END)
                for f in folder_files:
                    folder_listbox.insert(tk.END, f)

        def on_folder_file_select(event):
            if folder_listbox is None or current_folder is None:
                return
            selection = folder_listbox.curselection()
            if not selection:
                return
            filename = folder_listbox.get(selection[0])
            file_path = os.path.join(current_folder, filename)
            # 检查是否已打开
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

            count += 1
        text_widget.tag_config('find_highlight', background='#ffe066', foreground='#d2691e')
        if count == 0:
            messagebox.showinfo("查找结果", "未找到内容")
        else:
            # 跳转到第一个匹配
            text_widget.mark_set(tk.INSERT, text_widget.tag_nextrange('find_highlight', '1.0')[0])
            text_widget.see(text_widget.tag_nextrange('find_highlight', '1.0')[0])

    def clear_highlight():
        text_widget.tag_remove('find_highlight', '1.0', tk.END)

    tk.Button(find_win, text="查找", command=highlight_all).grid(row=1, column=0, padx=6, pady=6)
    tk.Button(find_win, text="清空", command=clear_highlight).grid(row=1, column=1, padx=6, pady=6)
    find_entry.focus_set()
    find_win.grab_set()
    find_win.bind('<Return>', lambda e: highlight_all())
    find_win.bind('<Escape>', lambda e: find_win.destroy())
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
    # 检查标签页数量限制（最多25个）
    if len(tabs_data) >= 25:
        messagebox.showwarning("提示", "标签页数量已达到上限（最多25个），请先关闭一些标签页")
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
    
    # 更新标签页标题和窗口标题
    update_tab_title(tab_frame)
    update_window_title()
    
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
# 在保存文件之前检查标签页是否存在于tabs_data中
def save_file(tab_id=None):
    """保存当前标签页的文件"""
    if tab_id is not None and tab_id not in tabs_data:
        messagebox.showerror("错误", "目标标签页不存在或已关闭！")
        return

    tab_data = get_current_tab_data() if tab_id is None else tabs_data.get(tab_id)
    if not tab_data:
        messagebox.showerror("错误", "没有活动的标签页！")
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
            return
        tab_data['file_path'] = file_path
    else:
        file_path = tab_data['file_path']

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        tab_data['original_content'] = content
        update_tab_title(tab_id)
        update_window_title()
        messagebox.showinfo("保存成功", f"文件已保存到：{file_path}")
    except Exception as e:
        messagebox.showerror("错误", f"保存文件失败：{e}")
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
    
    # 更新标签页文本（显示未保存标记）
    # 使用原始tab_id来更新notebook标签（notebook.tab需要原始ID）
    try:
        notebook.tab(original_tab_id, text=title)
    except:
        # 如果失败，尝试使用tab_id
        try:
            notebook.tab(tab_id, text=title)
        except:
            pass

def update_window_title():
    """更新窗口标题，显示当前文件名"""
    tab_data = get_current_tab_data()
    if not tab_data:
        root.title("TXTPro")
        return
    
    if tab_data['file_path']:
        base_name = os.path.basename(tab_data['file_path'])
        if is_content_modified():
            root.title(f"*{base_name}")
        else:
            root.title(base_name)
    else:
        if is_content_modified():
            root.title("*新文件")
        else:
            root.title("新文件")

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
    root.after_idle(lambda: (update_line_numbers(tab_id), update_tab_title(tab_id), update_window_title(), update_cursor_position()))

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
        update_window_title()
        update_cursor_position()
def run_python_file():
    """运行当前打开的Python文件"""
    tab_data = get_current_tab_data()
    if not tab_data or not tab_data['file_path']:
        messagebox.showwarning("提示", "没有打开的Python文件")
        return
    
    # 检查是否为Python文件
    _, ext = os.path.splitext(tab_data['file_path'])
    if ext.lower() != '.py':
        messagebox.showwarning("提示", "当前文件不是Python文件")
        return
    
    # 只有当文件内容被修改时才询问是否保存
    if is_content_modified():
        result = messagebox.askyesnocancel("保存文件", "文件有未保存的修改，是否保存？")
        if result is True:
            # 保存文件
            save_file()
        elif result is None:
            # 取消运行
            return
    
    try:
        # 获取文件路径和目录
        file_path = tab_data['file_path']
        file_dir = os.path.dirname(file_path)
        
        # 构建PowerShell命令，设置工作目录并运行Python文件
        # 使用NoExit参数保持PowerShell窗口打开，方便查看输出
        powershell_command = f"cd '{file_dir}' ; python '{file_path}' ; pause"
        
        # 打开新的PowerShell窗口运行命令
        subprocess.Popen([
            'cmd.exe', '/c', 'start', 'powershell', '-NoExit', '-Command', powershell_command
        ])
        
    except Exception as e:
        messagebox.showerror("错误", f"运行Python文件失败: {str(e)}")
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
# 创建一个"文件"按钮，并将新建、选择文件、打开文件夹、保存、查找、统计功能集合到一个菜单中
file_menu_button = tk.Menubutton(button_frame, text="文件", relief=tk.RAISED)
file_menu_button.pack(side="left", padx=(0, 10))

file_menu = tk.Menu(file_menu_button, tearoff=0)
file_menu.add_command(label="新建", command=create_new_tab)
file_menu.add_command(label="选择文件", command=select_file)
file_menu.add_command(label="打开文件夹", command=open_folder)
file_menu.add_command(label="保存（Ctrl-S）", command=save_file)
file_menu.add_command(label="运行（F5）", command=run_python_file)
file_menu.add_separator()
file_menu.add_command(label="查找", command=show_find_dialog)
file_menu.add_command(label="统计", command=show_statistics)

file_menu_button.config(menu=file_menu)

# 文本与hex按钮
def show_hex_converter():
    import pyperclip
    win = tk.Toplevel(root)
    win.title("文本转hex")
    win.resizable(False, False)
    win.transient(root)
    tk.Label(win, text="输入文本:").grid(row=0, column=0, padx=6, pady=6)
    entry = tk.Entry(win, width=32)
    entry.grid(row=0, column=1, padx=6, pady=6)

    def convert():
        text = entry.get()
        hex_str = text.encode('utf-8').hex()
        messagebox.showinfo("转换结果", hex_str)

    def copy_hex():
        text = entry.get()
        hex_str = text.encode('utf-8').hex()
        pyperclip.copy(hex_str)
        messagebox.showinfo("复制成功", "已复制到剪贴板！")

    btn_convert = tk.Button(win, text="转换为hex", command=convert)
    btn_convert.grid(row=1, column=0, padx=6, pady=6)
    btn_copy = tk.Button(win, text="复制", command=copy_hex)
    btn_copy.grid(row=1, column=1, padx=6, pady=6)
    entry.focus_set()
    win.grab_set()
def show_hex_to_text():
    import pyperclip
    win = tk.Toplevel(root)
    win.title("hex转文本")
    win.resizable(False, False)
    win.transient(root)
    tk.Label(win, text="输入hex:").grid(row=0, column=0, padx=6, pady=6)
    entry = tk.Entry(win, width=32)
    entry.grid(row=0, column=1, padx=6, pady=6)

    def convert():
        hex_str = entry.get().strip().replace(" ", "")
        if not hex_str:
            return
        try:
            raw = bytes.fromhex(hex_str)
            text = raw.decode('utf-8')
        except Exception as e:
            messagebox.showerror("错误", f"无法解析为文本: {e}")
            return
        messagebox.showinfo("转换结果", text)

    def copy_text():
        hex_str = entry.get().strip().replace(" ", "")
        try:
            raw = bytes.fromhex(hex_str)
            text = raw.decode('utf-8')
        except Exception as e:
            messagebox.showerror("错误", f"无法解析为文本: {e}")
            return
        pyperclip.copy(text)
        messagebox.showinfo("复制成功", "已复制到剪贴板！")

    btn_convert = tk.Button(win, text="转换为文本", command=convert)
    btn_convert.grid(row=1, column=0, padx=6, pady=6)
    btn_copy = tk.Button(win, text="复制", command=copy_text)
    btn_copy.grid(row=1, column=1, padx=6, pady=6)
    entry.focus_set()
    win.grab_set()

# 创建一个"hex转码"按钮，并将文本转hex和hex转文本功能集合到一个菜单中
hex_menu_button = tk.Menubutton(button_frame, text="hex转码", relief=tk.RAISED)
hex_menu_button.pack(side="left", padx=(0, 10))

hex_menu = tk.Menu(hex_menu_button, tearoff=0)
hex_menu.add_command(label="文本转hex", command=show_hex_converter)
hex_menu.add_command(label="hex转文本", command=show_hex_to_text)

hex_menu_button.config(menu=hex_menu)
# 右上角：光标位置显示和更新历史按钮
status_label = tk.Label(top_frame, text="", font=("Consolas", 8), fg="#666666")
status_label.pack(side="right", padx=(0, 10))
log_button = tk.Button(top_frame, text="更新历史", command=show_log)
log_button.pack(side="right")
# 创建Notebook（标签页容器）
# 左侧文件列表 Listbox
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=3)
main_frame.rowconfigure(0, weight=1)

folder_listbox = tk.Listbox(main_frame, font=("Consolas", 10))
folder_listbox.grid(row=0, column=0, sticky="nsew")

# 右侧编辑区（Notebook）
notebook = ttk.Notebook(main_frame)
notebook.grid(row=0, column=1, sticky="nsew", padx=(10, 10), pady=(0, 10))


def on_folder_file_select(event):
    if folder_listbox is None or current_folder is None:
        return
    selection = folder_listbox.curselection()
    if not selection:
        return
    filename = folder_listbox.get(selection[0])
    file_path = os.path.join(current_folder, filename)
    # 检查是否已打开
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
folder_listbox.bind('<<ListboxSelect>>', on_folder_file_select)
def use_deepseek():
    """调用DeepSeek API并显示结果"""
    tab_data = get_current_tab_data()
    if not tab_data:
        messagebox.showerror("错误", "没有活动的标签页！")
        return

    text_widget = tab_data['text_widget']
    content = text_widget.get("1.0", tk.END + "-1c")

    if not content.strip():
        messagebox.showerror("错误", "当前标签页内容为空！")
        return

    # 如果 deepseek_client 未初始化，提示用户设置 API
    if deepseek_client is None:
        if messagebox.askyesno("未配置 DeepSeek API", "未检测到 DeepSeek API Key，是否现在设置？"):
            set_deepseek_api()
        return

    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个有帮助的助手"},
                {"role": "user", "content": content},
            ],
            stream=False
        )
        result = response.choices[0].message.content
        messagebox.showinfo("DeepSeek 回答", result)
    except Exception as e:
        messagebox.showerror("错误", f"调用DeepSeek API失败。错误信息: {str(e)}\n\n请确保在 C:\\Users\\Public\\Documents\\deepseek_api.txt 中写入您的 DeepSeek API Key，或使用“设置 DeepSeek API”配置。")

def read_deepseek_api_from_file():
    try:
        if not os.path.exists(DEEPSEEK_API_PATH):
            # 创建空文件
            os.makedirs(os.path.dirname(DEEPSEEK_API_PATH), exist_ok=True)
            with open(DEEPSEEK_API_PATH, 'w', encoding='utf-8') as f:
                f.write('')
            return ''
        with open(DEEPSEEK_API_PATH, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return ''

def set_deepseek_api():
    """弹出对话框设置并保存 DeepSeek API Key"""
    current = read_deepseek_api_from_file()
    win = tk.Toplevel(root)
    win.title("设置 DeepSeek API")
    win.resizable(False, False)
    win.transient(root)
    tk.Label(win, text="DeepSeek API Key:").grid(row=0, column=0, padx=6, pady=6)
    entry = tk.Entry(win, width=48)
    entry.grid(row=0, column=1, padx=6, pady=6)
    entry.insert(0, current)

    def save_key():
        key = entry.get().strip()
        try:
            with open(DEEPSEEK_API_PATH, 'w', encoding='utf-8') as f:
                f.write(key)
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
            return
        # 重新初始化 deepseek_client（允许环境变量覆盖）
        init_deepseek_client()
        messagebox.showinfo("成功", "DeepSeek API Key 已保存。")
        win.destroy()

    tk.Button(win, text="保存", command=save_key).grid(row=1, column=0, padx=6, pady=6)
    tk.Button(win, text="取消", command=win.destroy).grid(row=1, column=1, padx=6, pady=6)
    entry.focus_set()
    win.grab_set()

def init_deepseek_client():
    """初始化 deepseek_client，若无 key 则设为 None"""
    global deepseek_client
    api_key = os.environ.get('DEEPSEEK_API_KEY', '') or read_deepseek_api_from_file()
    api_key = api_key.strip()
    if api_key:
        try:
            deepseek_client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        except Exception:
            deepseek_client = None
    else:
        deepseek_client = None
def reset_deepseek_api_key():
    with open("C:/Users/Public/Documents/deepseek_api.txt", 'w', encoding='utf-8') as f:
        f.write('')
        messagebox.showinfo("成功", "DeepSeek API Key 已重置。")

# 在界面创建后，添加设置 API 的菜单项（插入到“文件”菜单）
try:
    file_menu.add_separator()
    file_menu.add_command(label="设置 DeepSeek API Key", command=set_deepseek_api)
    file_menu.add_command(label="重置 DeepSeek API Key", command=reset_deepseek_api_key)
except Exception:
    pass

# 初始化 DeepSeek 客户端（首次）
init_deepseek_client()
deepseek_use_button = tk.Button(button_frame, text="DeepSeek", command=use_deepseek)
deepseek_use_button.pack(side="left", padx=(0, 10))


def _save_file(event=None):
    save_file()
    return "break"
def _run_python_file(event=None):
    run_python_file()
    return "break"

# 绑定 notebook 事件与关闭回调（确保只绑定一次）
notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
notebook.bind("<Button-3>", show_tab_context_menu)   # 鼠标右键显示菜单（Windows）
root.bind("<Control-s>", _save_file)
root.bind("<F5>", _run_python_file)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()