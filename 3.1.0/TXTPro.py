import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from random import choice
import os, subprocess
from openai import OpenAI
root = tk.Tk()
root.title("TXTPro"); root.geometry("800x400")
tabs_data, tab_counter = {}, 0
filetypes = [("文本", "*.txt"), ("Python", "*.py"), ("JSON", "*.json"), ("BAT", "*.bat"), ("Ruby", "*.rb"), ("JavaScript", "*.js"), ("HTML", "*.html"), ("任何（实验）", "*.*")]
cfiletypes = filetypes[0:-2]
applog = """当前版本：3.1.0
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
3.1.0：（重量级更新）写着写着无聊了？看看Tips！又分类了一波...压缩多于出来的行"""
DEEPSEEK_API_PATH = r"C:\Users\Public\Documents\deepseek_api.txt"
tips = ["让我猜猜...现在是上午？","哦，我的txtpro真好用！","wow deepseek真的好用吗？","按Ctrl+N新建标签页！","按Ctrl+S保存文件！","难道真的没人用deepseek吗？","txtpro是一个用python做的文本编辑器","让我猜猜...用0.1.0版本的txtpro人真的很少吧...","PCL启动器能启动txtpro吗？","你是花了多少时间去刷到这个tips的？！", "Tips：Tips：Tips："]
# 文件夹相关全局变量
current_folder,folder_listbox,folder_files= None, None, []
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
    def clear_highlight():
        text_widget.tag_remove('find_highlight', '1.0', tk.END)
    ttk.Button(find_win, text="查找", command=highlight_all).grid(row=1, column=0, padx=6, pady=6)
    ttk.Button(find_win, text="清空", command=clear_highlight).grid(row=1, column=1, padx=6, pady=6)
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
    # 检查标签页数量限制（最多15个）
    if len(tabs_data) >= 15:
        messagebox.showwarning("提示", "标签页数量已达到上限（最多15个），请先关闭一些标签页")
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
    update_line_numbers(tab_frame)
    update_tab_title(tab_frame)
    update_window_title()
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
file_menu.add_command(label="查找", command=show_find_dialog)
file_menu.add_command(label="统计", command=show_statistics)
file_menu.add_separator()
file_menu.add_command(label="文本转hex", command=show_hex_converter)
file_menu.add_command(label="hex转文本", command=show_hex_to_text)
file_menu_button.config(menu=file_menu)
# 右上角：光标位置显示
status_label = tk.Label(top_frame, text="", font=("Consolas", 8), fg="#666666")
status_label.pack(side="right", padx=(0, 10))
# 右下角：定时显示Tips
tips_label = tk.Label(root, text="", font=("Consolas", 8), fg="#333333", bg="#ffffcc", relief="solid", borderwidth=1, padx=5, pady=2)
# 更新Tips的函数
def update_tips():
    tip = choice(tips)
    tips_label.config(text=f"Tips：{tip}")
    # 强制更新标签大小
    tips_label.update_idletasks()
    # 调整位置
    adjust_tips_position()
    # 3秒后再次更新
    root.after(3000, update_tips)
# 调整Tips标签位置的函数
def adjust_tips_position():
    # 获取窗口大小
    width = root.winfo_width()
    height = root.winfo_height()
    # 确保窗口已初始化
    if width > 0 and height > 0:
        # 强制更新标签大小
        tips_label.update_idletasks()
        # 获取标签大小
        label_width = tips_label.winfo_reqwidth()
        label_height = tips_label.winfo_reqheight()
        # 设置标签位置在右下角
        tips_label.place(x=width - label_width - 10, y=height - label_height - 10)
# 绑定窗口大小变化事件
root.bind("<Configure>", lambda e: adjust_tips_position())
# 初始化Tips标签
update_tips()
# 确保标签可见
root.after(100, lambda: tips_label.lift())
# 创建Notebook（标签页容器）
# 左侧文件列表 Listbox
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)
# 文件夹列表框
folder_listbox = tk.Listbox(main_frame, font=("Consolas", 10))
# 中间编辑区（Notebook）
notebook = ttk.Notebook(main_frame)
# 右侧DeepSeek功能区
deepseek_frame = tk.Frame(main_frame)
# 定义布局更新函数
def update_layout(event=None):
    """更新布局，确保DeepSeek功能区始终是主窗口宽度的1/3"""
    width = main_frame.winfo_width()
    height = main_frame.winfo_height()
    # 当窗口太小时，不更新布局，避免组件大小变为负数或零
    if width < 200 or height < 150:
        return
    # 计算各区域宽度
    deepseek_width = width // 3
    remaining_width = width - deepseek_width
    # 文件列表宽度为剩余宽度的1/4，编辑区为3/4
    folder_width = remaining_width // 4
    editor_width = remaining_width - folder_width
    # 确保各组件有最小宽度
    min_deepseek_width = 200
    min_folder_width = 100
    min_editor_width = 300
    if deepseek_width < min_deepseek_width:
        deepseek_width = min_deepseek_width
        remaining_width = width - deepseek_width
        folder_width = remaining_width // 4
        editor_width = remaining_width - folder_width
    if folder_width < min_folder_width:
        folder_width = min_folder_width
        editor_width = remaining_width - folder_width
    if editor_width < min_editor_width:
        editor_width = min_editor_width
        folder_width = remaining_width - editor_width
    # 设置各组件位置
    folder_listbox.place(x=0, y=0, width=folder_width, height=height)
    notebook.place(x=folder_width + 10, y=0, width=editor_width - 20, height=height - 10)  # 减去边距
    deepseek_frame.place(x=width - deepseek_width + 10, y=0, width=deepseek_width - 20, height=height - 10)  # 减去边距
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
def deepseek_main_window():
    """打开DeepSeek主窗口（整合聊天和修改文件功能）"""
    # 检查DeepSeek API配置
    if deepseek_client is None:
        if messagebox.askyesno("未配置 DeepSeek API", "未检测到 DeepSeek API Key，是否现在设置？"):
            set_deepseek_api()
        return
    # 清空deepseek_frame中的现有内容
    for widget in deepseek_frame.winfo_children():
        widget.destroy()
    # 添加DeepSeek标题
    title_label = tk.Label(deepseek_frame, text="DeepSeek", font=("Consolas", 12, "bold"))
    title_label.pack(fill=tk.X, padx=10, pady=(10, 5))
    # 聊天历史
    chat_history = []
    # 创建主容器，使用grid布局
    main_container = tk.Frame(deepseek_frame)
    main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    # 设置grid布局参数
    main_container.grid_rowconfigure(0, weight=1)  # 聊天显示区域占主要空间
    main_container.grid_rowconfigure(1, weight=0)  # 输入框区域固定高度
    main_container.grid_rowconfigure(2, weight=0)  # 按钮区域固定高度
    main_container.grid_columnconfigure(0, weight=1)
    # 聊天记录显示区域
    chat_display = scrolledtext.ScrolledText(main_container, wrap=tk.WORD, font=("Consolas", 10), state=tk.DISABLED)
    chat_display.grid(row=0, column=0, sticky=tk.NSEW, pady=(0, 10))
    # 输入框和发送按钮区域
    input_frame = tk.Frame(main_container)
    input_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, 10))
    input_frame.grid_columnconfigure(0, weight=1)
    # 文本输入框
    input_entry = tk.Entry(input_frame, font=("Consolas", 10))
    input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    # 修改记录
    modifications = []
    # 底部按钮区域
    button_frame = tk.Frame(main_container)
    button_frame.grid(row=2, column=0, sticky=tk.EW, pady=(0, 5))
    def handle_deepseek_request():
        """处理DeepSeek请求，根据用户输入决定是聊天还是修改文件"""
        message = input_entry.get().strip()
        if not message:
            return
        # 清空输入框
        input_entry.delete(0, tk.END)
        # 获取当前文档内容（如果有）
        tab_data = get_current_tab_data()
        doc_content = ""
        text_widget = None
        if tab_data:
            text_widget = tab_data['text_widget']
            doc_content = text_widget.get("1.0", tk.END + "-1c").strip()
        # 检查用户输入是否包含修改文件的关键词
        modify_keywords = ["修改", "编辑", "更改", "调整", "更新", "重写", "删除", "添加", "替换"]
        is_modify_request = any(keyword in message for keyword in modify_keywords)
        # 构建发送内容
        history_text = "\n".join([f"用户: {h[0]}\nDeepSeek: {h[1]}" for h in chat_history])
        if doc_content:
            send_content = f"聊天记录（没有则空）：\n{history_text}\n\n当前文档内容：\n{doc_content}\n\n{message}"
        else:
            send_content = f"聊天记录（没有则空）：\n{history_text}\n\n{message}"
        # 显示用户消息
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"用户：{message}\n")
        chat_display.config(state=tk.DISABLED)
        chat_display.see(tk.END)
        try:
            if is_modify_request and text_widget and doc_content:
                # 调用DeepSeek API进行修改
                response = deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是一个代码修改助手，请根据用户指令修改提供的文本内容。如果需要提供说明，请在修改后的内容前加上'说明：'，然后在修改后的内容前加上'修改后：'。"},
                        {"role": "user", "content": send_content}
                    ],
                    stream=False
                )
                response_content = response.choices[0].message.content
                # 处理API返回的内容，提取说明和修改后的文本
                explanation = ""
                modified_content = ""
                if "修改后：" in response_content:
                    # 分离说明和修改后的内容
                    parts = response_content.split("修改后：", 1)
                    if len(parts) > 1:
                        explanation = parts[0].replace("说明：", "").strip()
                        modified_content = parts[1].strip()
                    else:
                        modified_content = response_content.strip()
                else:
                    modified_content = response_content.strip()
                # 处理内容，移除多余的换行符
                doc_content = doc_content.rstrip('\n')
                modified_content = modified_content.rstrip('\n')
                # 显示修改结果（在编辑区中带颜色标记）
                text_widget.config(state=tk.NORMAL)
                text_widget.delete("1.0", tk.END)
                # 添加红色框标记原始内容
                text_widget.insert(tk.END, doc_content)
                text_widget.insert(tk.END, "\n\n")
                text_widget.insert(tk.END, modified_content)
                # 配置标签
                text_widget.tag_config("original", background="#ffe6e6", borderwidth=1, relief="solid")
                text_widget.tag_config("modified", background="#e6ffe6", borderwidth=1, relief="solid")
                # 应用标签
                original_end = f"1.0+{len(doc_content)}c"
                modified_start = f"1.0+{len(doc_content) + len('\n\n')}c"
                modified_end = f"1.0+{len(doc_content) + len('\n\n') + len(modified_content)}c"
                text_widget.tag_add("original", "1.0", original_end)
                text_widget.tag_add("modified", modified_start, modified_end)
                text_widget.config(state=tk.NORMAL)
                # 更新行号显示
                update_line_numbers()
                # 保存修改记录
                modifications.append((doc_content, modified_content, text_widget))
                # 显示修改项的撤销/保留按钮
                update_modify_buttons()
                # 显示AI回答
                chat_display.config(state=tk.NORMAL)
                if explanation:
                    chat_display.insert(tk.END, f"DeepSeek：{explanation}\n\n")
                else:
                    chat_display.insert(tk.END, f"DeepSeek：已完成修改\n\n")
                chat_display.config(state=tk.DISABLED)
                chat_display.see(tk.END)
            else:
                # 调用DeepSeek API进行聊天
                response = deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是一个有帮助的助手"},
                        {"role": "user", "content": send_content},
                    ],
                    stream=False
                )
                result = response.choices[0].message.content
                # 显示AI回答
                chat_display.config(state=tk.NORMAL)
                chat_display.insert(tk.END, f"DeepSeek：{result}\n\n")
                chat_display.config(state=tk.DISABLED)
                chat_display.see(tk.END)
                # 更新历史记录
                chat_history.append((message, result))
        except Exception as e:
            messagebox.showerror("错误", f"调用DeepSeek API失败。错误信息: {str(e)}")
    def update_modify_buttons():
        """更新修改项按钮"""
        # 清空现有按钮
        for widget in button_frame.winfo_children():
            widget.destroy()
        if modifications:
            # 全部按钮区域
            all_buttons_frame = tk.Frame(button_frame)
            all_buttons_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
            def undo_all_modifications():
                """撤销所有修改"""
                if modifications:
                    modifications.clear()
                    update_modify_buttons()
                    # 清除编辑区内容
                    tab_data = get_current_tab_data()
                    if tab_data:
                        text_widget = tab_data['text_widget']
                        text_widget.config(state=tk.NORMAL)
                        text_widget.delete("1.0", tk.END)
                        text_widget.config(state=tk.NORMAL)
                    messagebox.showinfo("成功", "已撤销所有修改")
            def apply_all_modifications():
                """应用所有修改"""
                if modifications:
                    # 应用最终修改
                    text_widget = modifications[-1][2]
                    text_widget.config(state=tk.NORMAL)
                    text_widget.delete("1.0", tk.END)
                    text_widget.insert("1.0", modifications[-1][1])
                    text_widget.config(state=tk.NORMAL)
                    modifications.clear()
                    update_modify_buttons()
                    messagebox.showinfo("成功", "已应用所有修改")
            # 添加全部撤销和全部保留按钮
            tk.Button(all_buttons_frame, text="全部撤销", command=undo_all_modifications).pack(side=tk.LEFT, padx=5)
            tk.Button(all_buttons_frame, text="全部保留", command=apply_all_modifications).pack(side=tk.LEFT, padx=5)
    # 发送按钮
    send_button = tk.Button(input_frame, text="发送", command=handle_deepseek_request)
    send_button.pack(side=tk.RIGHT)
    # 绑定回车键
    input_entry.bind('<Return>', lambda e: handle_deepseek_request())
    input_entry.focus_set()
def use_deepseek():
    deepseek_main_window()
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
# 初始化DeepSeek功能区
try:
    deepseek_main_window()
except Exception:
    pass
def _save_file(event=None):
    save_file()
    return "break"
def _run_python_file(event=None):
    run_python_file()
    return "break"
def _new_tab(event=None):
    create_new_tab()
    return "break"
# 绑定 notebook 事件与关闭回调（确保只绑定一次）
notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
notebook.bind("<Button-3>", show_tab_context_menu)   # 鼠标右键显示菜单（Windows）
root.bind("<Control-s>", _save_file)
root.bind("<F5>", _run_python_file)
root.bind("<Control-n>", _new_tab)
root.protocol("WM_DELETE_WINDOW", on_closing)
file_menu.add_separator()
file_menu.add_command(label="更新历史", command=show_log)
root.mainloop()