import random
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys
import os

# 读取命运之书内容
def load_book(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            return ["命运之书空白无言……", "今日天机不可泄露", "静心等待时机"]
        return lines
    except FileNotFoundError:
        return ["⚠️ 未找到 books.txt 文件，请确保它在程序目录中。"]

# GUI 应用类
class FateBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔮 命运之书")
        self.root.geometry("390x520")
        self.root.resizable(False, False)
        self.book = load_book(txt_path)

        # 标题标签
        self.title_label = tk.Label(root, text="🔮 欢迎来到命运之书", font=("微软雅黑", 16, "bold"), fg="purple")
        self.title_label.pack(pady=10)

        # 问题输入框
        self.question_label = tk.Label(root, text="写下你的问题：", font=("微软雅黑", 12))
        self.question_label.pack(pady=5)

        self.question_entry = tk.Entry(root, width=50, font=("微软雅黑", 11))
        self.question_entry.pack(pady=5)
        self.question_entry.bind("<Return>", lambda event: self.ask_question())

        # 提问按钮
        self.ask_button = tk.Button(root, text="📜 提问", font=("微软雅黑", 12), bg="#4CAF50", fg="white", command=self.ask_question)
        self.ask_button.pack(pady=10)

        # 正在思考动画
        self.thinking_label = tk.Label(root, text="", font=("微软雅黑", 10), fg="gray")
        self.thinking_label.pack(pady=5)

        # 显示回答区域（支持换行）
        self.result_text = scrolledtext.ScrolledText(
            root, 
            width=50, 
            height=8, 
            font=("微软雅黑", 12), 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            bg="#f9f9f9"
        )
        self.result_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    def ask_question(self):
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showwarning("提示", "请先写下你的问题！")
            return

        # 显示“正在翻动书页”
        self.thinking_label.config(text="📖 正在翻动书页...")
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.root.update()

        # 模拟延迟
        time.sleep(0.5)
        for _ in range(3):
            self.thinking_label.config(text=self.thinking_label.cget("text") + ".")
            self.root.update()
            time.sleep(0.5)

        # 获取回答
        answer = random.choice(self.book)
        time.sleep(0.5)
        self.thinking_label.config(text="")

        # 显示回答
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, f"命运之书说：\n\n{answer}\n")
        self.result_text.config(state=tk.DISABLED)
        self.result_text.see(tk.END)

def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容 PyInstaller 打包 """
    try:
        # PyInstaller 创建临时文件夹，路径在 sys._MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 主程序入口
if __name__ == "__main__":
    txt_path = resource_path('books.txt')
    root = tk.Tk()
    app = FateBookApp(root)
    root.mainloop()