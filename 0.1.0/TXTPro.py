import tkinter as tk
from tkinter import filedialog, messagebox

root = tk.Tk()
root.title("TXTPro")
root.resizable(False, False)
root.geometry("500x250")

current_file_path = None

def select_file():
    global current_file_path
    file_path = filedialog.askopenfilename(
        title="选择文件",
        filetypes=[("文本文件", "*.txt")]
    )
    if file_path:
        current_file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", content)
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败: {str(e)}")

def save_file():
    global current_file_path
    if current_file_path:
        try:
            content = text_widget.get("1.0", tk.END + "-1c")
            with open(current_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("成功", "文件已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {str(e)}")
    else:
        messagebox.showwarning("提示", "请先选择文件")

button_frame = tk.Frame(root)
button_frame.pack(pady=10, padx=10, anchor="w")

select_file_button = tk.Button(button_frame, text="选择文件", command=select_file)
select_file_button.pack(side="left", padx=(0, 10))

save_button = tk.Button(button_frame, text="保存", command=save_file)
save_button.pack(side="left")

text_widget = tk.Text(root, wrap=tk.WORD)
text_widget.pack(pady=10, padx=10, fill="both", expand=True)

root.mainloop()