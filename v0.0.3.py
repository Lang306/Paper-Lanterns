import random
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, Menu, Scale, HORIZONTAL
import sys
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

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

# 获取资源路径（兼容打包）
def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容 PyInstaller 打包 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# GUI 应用类
class FateBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔮 命运之书")
        self.root.geometry("390x580")
        self.root.resizable(False, False)

        # --- 新增：文本缩放比例（默认140%）
        self.text_scale = 140  # 100% ~ 1000%
        self.original_scale = 140  # 用于取消时恢复

        self.book = load_book(txt_path)
        self.last_question = ""
        self.last_answer = ""

        # --- 新增：创建菜单栏 ---
        self.menu_bar = Menu(root)
        self.root.config(menu=self.menu_bar)

        self.settings_menu = Menu(self.menu_bar, tearoff=0)
        self.settings_menu.add_command(label="设置...", command=self.open_settings)
        self.menu_bar.add_cascade(label="⚙️ 设置", menu=self.settings_menu)

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

        # 导出按钮（初始禁用）
        self.export_button = tk.Button(root, text="📷 导出结果", font=("微软雅黑", 12), bg="#CF99DA", fg="white", state=tk.DISABLED, command=self.export_result)
        self.export_button.pack(pady=10)

        # --- 新增：初始化字体 ---
        self.update_fonts()

    def update_fonts(self):
        """根据当前 text_scale 更新所有控件的字体大小"""
        scale_factor = self.text_scale / 100.0

        # 更新各控件字体
        title_size = int(16 * scale_factor)
        label_size = int(12 * scale_factor)
        entry_size = int(11 * scale_factor)
        button_size = int(12 * scale_factor)
        thinking_size = int(10 * scale_factor)
        result_size = int(12 * scale_factor)

        self.title_label.config(font=("微软雅黑", max(title_size, 8), "bold"))
        self.question_label.config(font=("微软雅黑", max(label_size, 8)))
        self.question_entry.config(font=("微软雅黑", max(entry_size, 8)))
        self.ask_button.config(font=("微软雅黑", max(button_size, 8)))
        self.thinking_label.config(font=("微软雅黑", max(thinking_size, 8)))
        self.result_text.config(font=("微软雅黑", max(result_size, 8)))
        self.export_button.config(font=("微软雅黑", max(button_size, 8)))

    def open_settings(self):
        """打开设置对话框"""
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("⚙️ 设置")
        self.settings_window.geometry("350x200")
        self.settings_window.resizable(False, False)
        self.settings_window.transient(self.root)  # 置于主窗口上方
        self.settings_window.grab_set()  # 模态窗口

        # 存储当前值，用于取消操作
        temp_scale = self.text_scale

        # 标签
        tk.Label(self.settings_window, text="调整文本大小 (100% - 1000%)", font=("微软雅黑", 12)).pack(pady=10)

        # 滑动条
        scale_var = tk.IntVar(value=self.text_scale)
        scale_slider = Scale(
            self.settings_window,
            from_=100,
            to=1000,
            orient=HORIZONTAL,
            variable=scale_var,
            length=300,
            label="缩放比例"
        )
        scale_slider.pack(pady=10)

        # 实时更新回调
        def on_scale_change(val):
            nonlocal temp_scale
            temp_scale = int(val)
            self.text_scale = temp_scale
            self.update_fonts()

        scale_slider.config(command=on_scale_change)

        # 按钮框架
        btn_frame = tk.Frame(self.settings_window)
        btn_frame.pack(pady=20)

        def apply_settings():
            # 应用已由 on_scale_change 实现
            pass

        def ok_settings():
            apply_settings()
            self.settings_window.destroy()

        def cancel_settings():
            self.text_scale = self.original_scale
            self.update_fonts()
            self.settings_window.destroy()

        tk.Button(btn_frame, text="应用", width=10, command=apply_settings).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="确定", width=10, command=ok_settings).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", width=10, command=cancel_settings).pack(side=tk.LEFT, padx=5)

        # 当窗口关闭时，等同于取消
        self.settings_window.protocol("WM_DELETE_WINDOW", cancel_settings)

        # 保存原始值
        self.original_scale = self.text_scale

    def ask_question(self):
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showwarning("提示", "请先写下你的问题！")
            return
        self.last_question = question
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
        self.last_answer = answer
        time.sleep(0.5)
        self.thinking_label.config(text="")
        # 显示回答
        display_text = f'''{question} ? \n 命运之书说：{answer}
        '''
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, display_text)
        self.result_text.config(state=tk.DISABLED)
        self.result_text.see(tk.END)
        # 启用导出按钮
        self.export_button.config(state=tk.NORMAL)

    def export_result(self):
        if not self.last_question or not self.last_answer:
            return
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            messagebox.showerror("错误", "未安装 Pillow 库！请运行：pip install pillow")
            return
        # ========== 图片基础设置 ==========
        width, height = 700, 900
        # 创建白色背景
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        # ========== 加载系统中文字体 ==========
        # 尝试加载 Windows 系统黑体，这是最可靠的内置中文字体
        try:
            # 优先使用黑体，加粗效果好
            title_font = ImageFont.truetype("simhei.ttf", 40)  # 标题
            text_font = ImageFont.truetype("simhei.ttf", 32)   # 正文
            small_font = ImageFont.truetype("simhei.ttf", 24)  # 小字
        except IOError:
            try:
                # 备用：楷体
                title_font = ImageFont.truetype("simkai.ttf", 40)
                text_font = ImageFont.truetype("simkai.ttf", 32)
                small_font = ImageFont.truetype("simkai.ttf", 24)
            except IOError:
                # 再次失败：使用 Pillow 的默认字体（可能不完美，但能显示）
                default_font = ImageFont.load_default()
                # 创建一个包装，使其能接受 size 参数（简化处理）
                title_font = text_font = small_font = default_font
        # ========== 绘制标题 ==========
        title = "🔮 命运之书"
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = bbox[2] - bbox[0]
        draw.text(((width - title_width) // 2, 50), title, font=title_font, fill="#8B00FF")  # 深紫色
        # ========== 绘制问题 ==========
        draw.text((50, 130), "❓ 你的问题：", font=text_font, fill="#1E90FF")  # 道奇蓝
        self._draw_multiline_text(draw, self.last_question, (60, 180), text_font, width - 100, "#000000")
        # ========== 添加分隔线 ==========
        line_y = 300
        draw.line([(50, line_y), (width - 50, line_y)], fill="#DDA0DD", width=2)  # 紫色细线
        
        # ========== 绘制命运回答 ==========
        # 绘制“命运之书说：”标题（保持红色）
        draw.text((50, line_y + 50), "📜 命运之书说：", font=text_font, fill="#8B0000")  # 深红色

        # 使用彩虹字体绘制回答内容
        self._draw_multiline_text(draw, self.last_answer, (60, line_y + 100), text_font, width - 100, "#2F4F4F")  # 深墨绿
        
        # ========== 绘制底部时间（修复中文编码问题）==========
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        hour = now.strftime("%H")
        minute = now.strftime("%M")
        date_str = f"{year}年{month}月{day}日 {hour}:{minute}"
        timestamp = f"生成于 {date_str}"
        bbox = draw.textbbox((0, 0), timestamp, font=small_font)
        time_width = bbox[2] - bbox[0]
        draw.text(((width - time_width) // 2, height - 60), timestamp, font=small_font, fill="gray")
        # ========== 保存图片 ==========
        filename = f"fate_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        try:
            image.save(filename, "PNG", quality=95)
            messagebox.showinfo("导出成功", f"精美的预测图片已保存为：{filename}")
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存图片：{str(e)}")

    def _draw_multiline_text(self, draw, text, position, font, max_width, fill):
        """自动换行绘制多行文本"""
        lines = []
        line = ""
        for char in text:
            test_line = line + char
            # 估算文本宽度
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]
            except:
                width = len(test_line) * 15  # 粗略估算
            if width <= max_width:
                line = test_line
            else:
                if line:
                    lines.append(line)
                line = char
        if line:
            lines.append(line)
        x, y = position
        line_height = 40
        for line in lines:
            draw.text((x, y), line, font=font, fill=fill)
            y += line_height
    def _get_rainbow_colors(self, n):
        """生成 n 个彩虹渐变颜色 (R, G, B)"""
        colors = []
        for i in range(n):
            ratio = i / max(n - 1, 1)
            r = int(255 * (1 - ratio * 0.5))           # 红：全程高，缓慢下降
            g = int(255 * (ratio))                      # 绿：从中段开始上升
            b = int(255 * (1 - ratio))                  # 蓝：从高到低
            # 更真实的彩虹：红、橙、黄、绿、青、蓝、紫
            if ratio < 0.14:
                # 红 → 橙
                r, g, b = 255, int(165 + ratio * 300), 0
            elif ratio < 0.28:
                # 橙 → 黄
                r, g, b = 255, int(255), int(ratio * 900 - 200)
            elif ratio < 0.42:
                # 黄 → 绿
                r, g, b = int(255 - (ratio - 0.28) * 600), 255, 0
            elif ratio < 0.56:
                # 绿 → 青
                r, g, b = 0, 255, int((ratio - 0.42) * 600)
            elif ratio < 0.7:
                # 青 → 蓝
                r, g, b = 0, int(255 - (ratio - 0.56) * 600), 255
            elif ratio < 0.85:
                # 蓝 → 紫
                r, g, b = int((ratio - 0.7) * 400), 0, int(255 - (ratio - 0.7) * 300)
            else:
                # 紫 → 粉
                r, g, b = 143 + int((ratio - 0.85) * 200), 0, 255
            r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
            colors.append((r, g, b))
        return colors
    def _draw_rainbow_text(self, draw, text, position, font, max_width):
        """绘制多行彩虹文字，自动换行，每字颜色渐变"""
        lines = []
        line = ""
        for char in text:
            test_line = line + char
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]
            except:
                width = len(test_line) * 20
            if width <= max_width:
                line = test_line
            else:
                if line:
                    lines.append(line)
                line = char
        if line:
            lines.append(line)

        x, y = position
        line_height = 45  # 行高略大一点好看

        for line in lines:
            colors = self._get_rainbow_colors(len(line))
            current_x = x
            for i, char in enumerate(line):
                try:
                    bbox = draw.textbbox((0, 0), char, font=font)
                    char_width = bbox[2] - bbox[0]
                except:
                    char_width = 30
                draw.text((current_x, y), char, font=font, fill=colors[i])
                current_x += char_width
            y += line_height

# 主程序入口
if __name__ == "__main__":
    txt_path = resource_path('books.txt')
    root = tk.Tk()
    app = FateBookApp(root)

    # --- 新增：窗口居中显示 ---
    root.update_idletasks()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()