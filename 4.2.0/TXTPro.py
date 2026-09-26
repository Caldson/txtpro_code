import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tkinter.font as tkfont
import os, subprocess
import ctypes
root = tk.Tk()
root.title("TXTPro")
root.geometry("940x500")
tabs_data, tab_counter = {}, 0
cfiletypes = [("任何", "*.*"), ("文本", "*.txt"), ("Python", "*.py"), ("JSON", "*.json"), ("BAT", "*.bat"), ("Ruby", "*.rb"), ("JavaScript", "*.js"), ("HTML", "*.html")]
# 文本区默认字体、字号
DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE = "Consolas", 10
ctypes.windll.shcore.SetProcessDpiAwareness(1)
applog = """当前版本：4.2.0
0.1.0：发布TXTPro软件
0.1.1：修复bug
0.2.0：修复bug并节约空间，添加大量功能，更改软件图标
0.3.0：（重量级更新）新增显示行号、统计字符/行数、标签页功能、显示光标位置，修复问题，删除转换为Mathematical Font功能
0.4.0：删除×按钮的残留部分节约空间，绑定更多按键，添加查找文本功能
0.4.1：修复问题、新增打开文件夹功能、将原本创建新文件和标签页合二为一
0.4.2：增加标签页数量上限至25个、hex功能
1.1.0：（重量级更新）将DeepSeek引入到TXTPro中，分类按钮
重新发布1.1.0：1.1.0补丁，修复deepseek_api.txt路径无法使用的问题
1.1.1：支持运行Python文件，修复Ctrl-S无法保存文件的问题
2.1.0：（重量级更新）将DeepSeek单独设置成一个窗口，添加修改文件功能，绑定更多按键，标签页因为DeepSeek调整成窗口导致标签页上限数量太多导致出现挤压bug所以将标签页上限调整为15个
3.1.0：（重量级更新）写着写着无聊了？看看Tips！又分类了一波...压缩多于出来的行
4.1.0：（重量级更新）更改风格并且移除tips的干扰
4.2.0：感谢DeepSeek对我们TXTPro这个软件的支持。因为DeepSeek近期涨价，我们不得不关闭AI功能，所以抱歉了各位。辅助功能调整。Thanks: DeepSeek"""
# 文件夹相关全局变量
current_folder,folder_listbox,folder_files= None, None, []

class Window(tk.Frame):
    def __init__(self, master, window_title="tk", width=200, height=200, placex=100, placey=100, bg="white", **kwargs):
        super().__init__(master, bd=2, relief="raised", bg=bg, **kwargs)
        self.place(x=placex, y=placey, width=width, height=height)
        self.width = width
        self.height = height

        # 顶部标题栏
        self.title_bar = tk.Frame(self, bg="#333", height=28)
        self.title_bar.pack(side=tk.TOP, anchor=tk.W, fill=tk.X)

        self.title_label = tk.Label(self.title_bar, text=window_title, fg="white", bg="#333")
        self.title_label.pack(side=tk.LEFT, padx=6)
        self.close_button = tk.Button(self.title_bar, text="X", command=self.destroy, bg="#333", fg="white", bd=0, relief="raised", activebackground="#333", activeforeground="white")
        self.close_button.pack(side=tk.RIGHT, padx=6)
        self.content = tk.Frame(self, bg=bg)
        self.content.pack(fill=tk.BOTH, expand=True)
        self._drag_x = 0
        self._drag_y = 0
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)
        self.title_label.bind("<Button-1>", self.start_drag)
        self.title_label.bind("<B1-Motion>", self.do_drag)
        self.update_size()
        self.content.bind("<Button-1>", lambda event: self.lift())

    def start_drag(self, event):
        self.lift()
        self._drag_x = event.x
        self._drag_y = event.y

    def do_drag(self, event):
        new_x = self.winfo_x() + event.x - self._drag_x
        new_y = self.winfo_y() + event.y - self._drag_y

        parent = self.master
        max_x = parent.winfo_width() - self.winfo_width()
        max_y = parent.winfo_height() - self.winfo_height()
        new_x = max(0, min(new_x, max_x))
        new_y = max(0, min(new_y, max_y))

        self.place(x=new_x, y=new_y)

    def geometry(self, width=None, height=None, placex=None, placey=None):
        if width != None:
            self.config(width=width)
        if height != None:
            self.config(height=height)
        if placex != None and placey != None:
            self.place(x=placex, y=placey)

    def bind_when_closed(self, callback):
        self.close_button.config(command=callback)

    def update_size(self):
        if self.width == 200 and self.height == 200:
            self.update_idletasks()
            if self.content.winfo_children():
                self.place_configure(width=self.winfo_reqwidth(), height=self.winfo_reqheight())
            else:
                self.place_configure(width=200, height=200)
        self.after(50, self.update_size)
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
    find_win = Window(root, "查找文本")
    tk.Label(find_win.content, text="查找内容:").grid(row=0, column=0, padx=6, pady=6)
    find_entry = tk.Entry(find_win.content, width=24)
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
    def clear_highlight():
        text_widget.tag_remove('find_highlight', '1.0', tk.END)
    ttk.Button(find_win.content, text="查找", command=highlight_all).grid(row=1, column=0, padx=6, pady=6)
    ttk.Button(find_win.content, text="清空", command=clear_highlight).grid(row=1, column=1, padx=6, pady=6)
    find_entry.focus_set()
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
    # 检查标签页数量限制（最多15个）
    if len(tabs_data) >= 15:
        messagebox.showwarning("提示", "标签页数量已达到上限（最多15个），请先关闭一些标签页")
        return None
    global tab_counter
    tab_counter += 1
    # 新标签页沿用当前标签页的字体设置（没有标签页时用默认设置）
    font_family, font_size = current_font_family, current_font_size
    active_tab = resolve_tab()
    if active_tab is not None:
        font_family, font_size = get_tab_font(active_tab)
    # 创建标签页框架
    tab_frame = tk.Frame(notebook)
    tab_text = "新文件" if not file_path else os.path.basename(file_path)
    # 添加标签页
    notebook.add(tab_frame, text=tab_text)
    notebook.select(tab_frame)
    # 创建上半部分（行号和文本区域）
    top_text_frame = tk.Frame(tab_frame)
    top_text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    # 行号显示区域（字体、字号跟随文本区，保证行号与文本对齐）
    line_number_widget = tk.Text(top_text_frame, width=4, padx=5, pady=5, 
                                  state=tk.DISABLED, wrap=tk.NONE, 
                                  bg="#f0f0f0", fg="#666666", 
                                  font=(font_family, font_size), relief=tk.FLAT)
    line_number_widget.pack(side=tk.LEFT, fill=tk.Y)
    # 创建文本和垂直滚动条的容器
    text_container = tk.Frame(top_text_frame)
    text_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    # 文本框（编辑框）
    text_widget = tk.Text(text_container, wrap=tk.NONE, padx=5, pady=5,
                          font=(font_family, font_size))
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
        'h_scrollbar': h_scrollbar,
        'font_family': font_family,
        'font_size': font_size
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
    # Ctrl+滚轮调整字号
    text_widget.bind('<Control-MouseWheel>', on_font_wheel)
    line_number_widget.bind('<Control-MouseWheel>', on_font_wheel)
    # 插入内容
    if content:
        text_widget.insert("1.0", content)
    update_line_numbers(tab_frame)
    update_tab_title(tab_frame)
    update_window_title()
    sync_font_controls()
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
        filetypes=[("任何", "*.*")]
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
    except PermissionError:
        messagebox.showerror("错误", "请以管理员身份重新运行此程序")
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
            root.title(f"TXTPro - *{base_name}")
        else:
            root.title(f"TXTPro - {base_name}")
    else:
        if is_content_modified():
            root.title("TXTPro - *新文件")
        else:
            root.title("TXTPro - 新文件")
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
    if is_content_modified(tab_id):
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
    # 更新窗口标题
    update_window_title()
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
    """标签页切换时更新行号、标题和字体工具条"""
    current_tab = notebook.select()
    if current_tab:
        update_line_numbers(current_tab)
        update_tab_title(current_tab)
        update_window_title()
        update_cursor_position()
        sync_font_controls()
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
    # 检查是否有未保存的标签页
    has_unsaved_changes = False
    for tab_id in tabs_data:
        if is_content_modified(tab_id):
            has_unsaved_changes = True
            break
    if has_unsaved_changes:
        messagebox.showerror("未保存", "请先保存未保存的标签页")
        return
    # 关闭所有标签页
    tabs_to_close = list(tabs_data.keys())
    for tab_id in tabs_to_close:
        close_tab(tab_id)
    root.destroy()
def show_hex_converter():
    import pyperclip
    win = Window(root, "文本转hex")
    tk.Label(win.content, text="输入文本:").grid(row=0, column=0, padx=6, pady=6)
    entry = tk.Entry(win.content, width=32)
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
    btn_convert = ttk.Button(win.content, text="转换为hex", command=convert)
    btn_convert.grid(row=1, column=0, padx=6, pady=6)
    btn_copy = ttk.Button(win.content, text="复制", command=copy_hex)
    btn_copy.grid(row=1, column=1, padx=6, pady=6)
    entry.focus_set()
def show_hex_to_text():
    import pyperclip
    win = Window(root, "hex转文本")
    tk.Label(win.content, text="输入hex:").grid(row=0, column=0, padx=6, pady=6)
    entry = tk.Entry(win.content, width=32)
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
    btn_convert = ttk.Button(win.content, text="转换为文本", command=convert)
    btn_convert.grid(row=1, column=0, padx=6, pady=6)
    btn_copy = ttk.Button(win.content, text="复制", command=copy_text)
    btn_copy.grid(row=1, column=1, padx=6, pady=6)
    entry.focus_set()
# ===== 辅助功能：编辑区（文本区）字体、字号调整 =====
FONT_SIZE_MIN, FONT_SIZE_MAX = 6, 72
FONT_SIZE_STEP = 1
# 当前默认字体（新标签页会沿用最近一次使用的设置）
current_font_family, current_font_size = DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE
def resolve_tab(tab_id=None):
    """把标签页ID（可能是字符串名）统一转换成tabs_data中的Frame对象"""
    if tab_id is None:
        tab_id = notebook.select()
    if not tab_id:
        return None
    try:
        if tab_id not in tabs_data:
            tab_id = notebook.nametowidget(tab_id)
    except Exception:
        return None
    return tab_id if tab_id in tabs_data else None
def get_tab_font(tab_id=None):
    """获取指定标签页当前的字体、字号"""
    tab_id = resolve_tab(tab_id)
    if tab_id is None:
        return current_font_family, current_font_size
    tab_data = tabs_data[tab_id]
    return (tab_data.get('font_family', current_font_family),
            tab_data.get('font_size', current_font_size))
def apply_font(family=None, size=None, tab_id=None):
    """把字体/字号应用到当前标签页的文本区（行号区同步，保证行号与文本对齐）"""
    global current_font_family, current_font_size
    if family:
        current_font_family = family
    if size:
        current_font_size = max(FONT_SIZE_MIN, min(FONT_SIZE_MAX, int(size)))
    tab_id = resolve_tab(tab_id)
    if tab_id is not None:
        tab_data = tabs_data[tab_id]
        tab_data['font_family'] = current_font_family
        tab_data['font_size'] = current_font_size
        tab_data['text_widget'].config(font=(current_font_family, current_font_size))
        tab_data['line_number_widget'].config(font=(current_font_family, current_font_size))
        update_line_numbers(tab_id)
    sync_font_controls()
def set_font_family(family=None):
    """按下拉框/输入框里填写的字体名应用"""
    family = (font_family_var.get() if family is None else family).strip()
    if not family:
        sync_font_controls()
        return
    apply_font(family=family)
def set_font_size(size=None):
    """按下拉框/输入框里填写的字号应用"""
    if size is None:
        raw = font_size_var.get().strip()
        try:
            size = int(float(raw))
        except ValueError:
            messagebox.showwarning("提示", "字号必须是数字")
            sync_font_controls()
            return
    apply_font(size=size)
def step_font_size(delta):
    """增减字号（A+/A-按钮、Ctrl+加号/减号、Ctrl+滚轮）"""
    _, size = get_tab_font()
    apply_font(size=size + delta)
def reset_font():
    """恢复默认字体、字号"""
    apply_font(family=DEFAULT_FONT_FAMILY, size=DEFAULT_FONT_SIZE)
def sync_font_controls(*args):
    """让工具条显示当前标签页的字体、字号"""
    family, size = get_tab_font()
    try:
        font_family_var.set(family)
        font_size_var.set(str(size))
    except Exception:
        pass
def on_font_wheel(event):
    """Ctrl+滚轮调整字号"""
    step_font_size(FONT_SIZE_STEP if event.delta > 0 else -FONT_SIZE_STEP)
    return "break"
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
file_menu.add_command(label="新建（Ctrl-N）", command=create_new_tab)
file_menu.add_command(label="选择文件", command=select_file)
file_menu.add_command(label="打开文件夹", command=open_folder)
file_menu.add_command(label="保存（Ctrl-S）", command=save_file)
file_menu.add_command(label="运行（F5）", command=run_python_file)
file_menu.add_separator()
findandtotal = tk.Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="查找和统计", menu=findandtotal)
findandtotal.add_command(label="查找", command=show_find_dialog)
findandtotal.add_command(label="统计", command=show_statistics)
file_menu.add_separator()
encodeanddecode = tk.Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="转码", menu=encodeanddecode)
encodeanddecode.add_command(label="文本转hex", command=show_hex_converter)
encodeanddecode.add_command(label="hex转文本", command=show_hex_to_text)
file_menu_button.config(menu=file_menu)
# 右上角：光标位置显示
status_label = tk.Label(top_frame, text="", font=("Consolas", 8), fg="#666666")
status_label.pack(side="right", padx=(0, 10))
# 辅助功能工具条：调整文本区的字体、字号
font_bar = tk.Frame(root)
font_bar.pack(fill="x", padx=10, pady=(0, 6))
tk.Label(font_bar, text="文本区字体:").pack(side="left")
font_family_var = tk.StringVar(value=current_font_family)
try:
    font_families = sorted(set(tkfont.families(root)))
except Exception:
    font_families = ["Consolas", "Courier New", "Microsoft YaHei", "SimSun", "Arial"]
font_family_combo = ttk.Combobox(font_bar, textvariable=font_family_var, values=font_families,
                                 width=22, state="normal")
font_family_combo.pack(side="left", padx=(4, 12))
font_family_combo.bind("<<ComboboxSelected>>", lambda e: set_font_family())
font_family_combo.bind("<Return>", lambda e: set_font_family())
tk.Label(font_bar, text="字号:").pack(side="left")
font_size_var = tk.StringVar(value=str(current_font_size))
font_size_combo = ttk.Combobox(font_bar, textvariable=font_size_var, width=4, state="normal",
                               values=[str(s) for s in range(FONT_SIZE_MIN, FONT_SIZE_MAX + 1)])
font_size_combo.pack(side="left", padx=(4, 6))
font_size_combo.bind("<<ComboboxSelected>>", lambda e: set_font_size())
font_size_combo.bind("<Return>", lambda e: set_font_size())
ttk.Button(font_bar, text="A-", width=3, command=lambda: step_font_size(-FONT_SIZE_STEP)).pack(side="left", padx=2)
ttk.Button(font_bar, text="A+", width=3, command=lambda: step_font_size(FONT_SIZE_STEP)).pack(side="left", padx=2)
ttk.Button(font_bar, text="恢复默认", command=reset_font).pack(side="left", padx=(6, 0))
tk.Label(font_bar, text="（可用 Ctrl+加号/减号、Ctrl+滚轮、Ctrl+0 快捷调整）",
         fg="#666666").pack(side="left", padx=10)
# 创建Notebook（标签页容器）
# 左侧文件列表 Listbox
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)
# 文件夹列表框
folder_listbox = tk.Listbox(main_frame, font=("Consolas", 10))
# 右侧编辑区（Notebook）——DeepSeek功能区已删除，编辑区占满右侧全部空间
notebook = ttk.Notebook(main_frame)
# 定义布局更新函数
def update_layout(event=None):
    """更新布局：左侧文件列表占约1/5，右侧编辑区占满剩余空间"""
    width = main_frame.winfo_width()
    height = main_frame.winfo_height()
    # 当窗口太小时，不更新布局，避免组件大小变为负数或零
    if width < 200 or height < 150:
        return
    # 计算各区域宽度
    folder_width = width // 5
    editor_width = width - folder_width
    # 确保各组件有最小宽度
    min_folder_width = 100
    min_editor_width = 300
    if folder_width < min_folder_width:
        folder_width = min_folder_width
        editor_width = width - folder_width
    if editor_width < min_editor_width:
        editor_width = min_editor_width
        folder_width = max(0, width - editor_width)
    # 设置各组件位置
    folder_listbox.place(x=0, y=0, width=folder_width, height=height)
    notebook.place(x=folder_width + 10, y=0, width=max(1, editor_width - 20), height=max(1, height - 10))  # 减去边距
# 绑定窗口大小变化事件
main_frame.bind("<Configure>", update_layout)
# 初始布局
update_layout()
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
def _save_file(event=None):
    save_file()
    return "break"
def _run_python_file(event=None):
    run_python_file()
    return "break"
def _new_tab(event=None):
    create_new_tab()
    return "break"
def _font_bigger(event=None):
    step_font_size(FONT_SIZE_STEP)
    return "break"
def _font_smaller(event=None):
    step_font_size(-FONT_SIZE_STEP)
    return "break"
def _font_reset(event=None):
    reset_font()
    return "break"
# 绑定 notebook 事件与关闭回调（确保只绑定一次）
notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
notebook.bind("<Button-3>", show_tab_context_menu)   # 鼠标右键显示菜单（Windows）
root.bind("<Control-s>", _save_file)
root.bind("<F5>", _run_python_file)
root.bind("<Control-n>", _new_tab)
root.bind("<Control-plus>", _font_bigger)
root.bind("<Control-equal>", _font_bigger)
root.bind("<Control-minus>", _font_smaller)
root.bind("<Control-0>", _font_reset)
root.protocol("WM_DELETE_WINDOW", on_closing)
update_history = ttk.Button(button_frame, text="更新历史", command=show_log)
update_history.pack(side=tk.RIGHT, padx=(0, 10), anchor="e")
root.mainloop()