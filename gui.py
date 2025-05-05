import tkinter as tk
from tkinter import filedialog, messagebox
from ttf_inspector import TTFInspector

def choose_file():
    file_path = filedialog.askopenfilename(
        title="选择字体文件",
        filetypes=[("TrueType Font", "*.ttf"), ("All Files", "*.*")]
    )
    if file_path:
        font_path_var.set(file_path)

def run_inspector():
    font_path = font_path_var.get()
    language = lang_var.get()
    if not font_path:
        messagebox.showwarning("提示", "请先选择字体文件！")
        return
    try:
        inspector = TTFInspector(
            font_path,
            language=language,
            lang_file='lang_pack.json',
            unicode_file='unicode_ranges.json'
        )

        # 收集报告文本
        char_count = inspector.count_characters()
        axes = inspector.get_variable_axes()
        range_counts = inspector.count_unicode_ranges()
        metadata = inspector.get_font_metadata()
        total_ranges = {key: end - start + 1 for key, (start, end) in inspector.unicode_ranges.items()}

        report_lines = []
        report_lines.append(inspector.lang_pack['report_title'])
        report_lines.append(inspector.lang_pack['char_count'].format(font=font_path, count=char_count))
        if axes:
            report_lines.append(inspector.lang_pack['axes'].format(axes=', '.join(axes)))
        else:
            report_lines.append(inspector.lang_pack['no_axes'])
        report_lines.append(inspector.lang_pack['section'])
        for key, count in range_counts.items():
            name = inspector.lang_pack['section_names'].get(key, key)
            total = total_ranges[key]
            percent = count / total * 100 if total > 0 else 0
            report_lines.append(inspector.lang_pack['section_item'].format(name=name, count=count, total=total, percent=percent))
        report_lines.append("\n" + inspector.lang_pack['metadata']['title'])
        for meta_key, value in metadata.items():
            label = inspector.lang_pack['metadata'].get(meta_key, meta_key)
            report_lines.append(f"    - {label}: {value}")

        # 弹窗显示文字报告
        messagebox.showinfo("检查报告", "\n".join(report_lines))

        # 显示图表
        inspector.visualize(range_counts, total_ranges)

    except Exception as e:
        messagebox.showerror("错误", f"检查失败: {e}")

# 主窗口
root = tk.Tk()
root.title("字体检查工具")

# 选择文件部分
font_path_var = tk.StringVar()
tk.Label(root, text="字体文件:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=font_path_var, width=40).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="浏览...", command=choose_file).grid(row=0, column=2, padx=10, pady=10)

# 语言选择部分
lang_var = tk.StringVar(value='cn')
tk.Label(root, text="语言:").grid(row=1, column=0, padx=10, pady=10)
tk.Radiobutton(root, text="中文", variable=lang_var, value='cn').grid(row=1, column=1, sticky='w')
tk.Radiobutton(root, text="English", variable=lang_var, value='en').grid(row=1, column=1, sticky='e')

# 执行按钮
tk.Button(root, text="运行检查", command=run_inspector, bg="lightgreen").grid(row=2, column=0, columnspan=3, pady=20)

root.mainloop()
