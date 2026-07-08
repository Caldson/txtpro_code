import tkinter as tk
from tkinter import filedialog, messagebox
import json, os
root = tk.Tk()
root.title("TXTPro")
root.resizable(False, False)
root.geometry("500x250")
current_file_path = None
original_content = ""
filetypes = [("文本", "*.txt"), ("Python", "*.py"), ("JSON", "*.json"), ("BAT", "*.bat"), ("Ruby", "*.rb"), ("JavaScript", "*.js"), ("HTML", "*.html"), ("任何（实验）", "*.*")]
cfiletypes = filetypes[0:-2]
applog = """当前版本：0.2.0
0.1.0：发布TXTPro软件
0.1.1：修复bug
0.2.0：修复bug并节约空间，添加大量功能，更改软件图标"""
def is_content_modified():
    global original_content
    current_content = text_widget.get("1.0", tk.END + "-1c")
    return current_content != original_content
def create_file():
    global current_file_path, original_content
    # 询问是否保存
    if current_file_path and is_content_modified():
        result = messagebox.askyesnocancel("提示", "当前文件有未保存的修改，是否保存？")
        if result is True:
            save_file()
        elif result is None:  # 取消
            return
    file_path = filedialog.asksaveasfilename(
        title="创建文件",
        defaultextension=".txt",
        filetypes=cfiletypes
    )
    if file_path:
        try:
            # 创建新文件。如果文件已存在，询问是否覆盖
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("")  # 创建文件
            current_file_path = file_path
            text_widget.delete("1.0", tk.END)
            original_content = ""
            messagebox.showinfo("成功", f"文件已创建: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"创建文件失败: {str(e)}")
def select_file():
    global current_file_path, original_content
    # 询问是否保存
    if current_file_path and is_content_modified():
        result = messagebox.askyesnocancel("提示", "当前文件有未保存的修改，是否保存？")
        if result is True:
            save_file()
        elif result is None:  # 取消
            return  # 取消整个选择文件操作，不打开文件选择对话框
    
    file_path = filedialog.askopenfilename(
        title="选择文件",
        filetypes=filetypes
    )
    if file_path:
        current_file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", content)
            original_content = content  # 保存原始内容
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败: {str(e)}")
def save_file():
    global current_file_path, original_content
    if current_file_path:
        try:
            content = text_widget.get("1.0", tk.END + "-1c")
            with open(current_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            original_content = content  # 更新原始内容
            messagebox.showinfo("成功", "文件已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {str(e)}")
    else:
        messagebox.showwarning("提示", "请先选择文件")
def convert_to_mathematical_font():
    font_map = {
        "A": "𝐴",
        "B": "𝐵",
        "C": "𝐶",
        "D": "𝐷",
        "E": "𝐸",
        "F": "𝐹",
        "G": "𝐺",
        "H": "𝐻",
        "I": "𝐼",
        "J": "𝐽",
        "K": "𝐾",
        "L": "𝐿",
        "M": "𝑀",
        "N": "𝑁",
        "O": "𝑂",
        "P": "𝑃",
        "Q": "𝑄",
        "R": "𝑅",
        "S": "𝑆",
        "T": "𝑇",
        "U": "𝑈",
        "V": "𝑉",
        "W": "𝑊",
        "X": "𝑋",
        "Y": "𝑌",
        "Z": "𝑍",
        "a": "𝑎",
        "b": "𝑏",
        "c": "𝑐",
        "d": "𝑑",
        "e": "𝑒",
        "f": "𝑓",
        "g": "𝑔",
        "h": "ℎ",
        "i": "𝑖",
        "j": "𝑗",
        "k": "𝑘",
        "l": "𝑙",
        "m": "𝑚",
        "n": "𝑛",
        "o": "𝑜",
        "p": "𝑝",
        "q": "𝑞",
        "r": "𝑟",
        "s": "𝑠",
        "t": "𝑡",
        "u": "𝑢",
        "v": "𝑣",
        "w": "𝑤",
        "x": "𝑥",
        "y": "𝑦",
        "z": "𝑧"
    }
    current_content = text_widget.get("1.0", tk.END + "-1c")
    converted_content = ""
    for char in current_content:
        if char in font_map:
            converted_content += font_map[char]
        else:
            converted_content += char
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", converted_content)
def show_log():
    messagebox.showinfo("更新历史", applog)
def on_closing():
    if current_file_path and is_content_modified(): # 是否保存
        result = messagebox.askyesnocancel("提示", "文件有未保存的修改，是否保存？")
        if result is True: # 保存
            save_file()
            root.destroy()
        elif result is False:  # 不保存
            root.destroy()
    else: # 取消
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
convert_button = tk.Button(button_frame, text="转换为Mathematical Font（实验）", command=convert_to_mathematical_font)
convert_button.pack(side="left")
# 右上角日志按钮
log_button = tk.Button(top_frame, text="更新历史", command=show_log)
log_button.pack(side="right")
# 文本框（编辑框）
text_widget = tk.Text(root, wrap=tk.WORD)
text_widget.pack(pady=10, padx=10, fill="both", expand=True)
# 绑定窗口关闭事件
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()