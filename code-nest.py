from tkinter import *
from tkinter import ttk, filedialog, simpledialog, END, INSERT, Toplevel, Text, Frame, BooleanVar, Menu, Listbox, BOTH, Label, BOTTOM, X, Y, Tk, PanedWindow, HORIZONTAL, LEFT, E
import os, subprocess

HOME_DIR = os.path.expanduser("~")
APP_DIR = os.path.join(HOME_DIR, "my-code-vault")
os.makedirs(APP_DIR, exist_ok=True)

class CodeNestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Nest")
        self.root.geometry("1000x600")
        self.files = {}
        self.current_file = None
        self.auto_save_interval = 60000
        self.theme = "dark"
        self.sidebar_visible = BooleanVar(value=True)
        self.setup_ui()
        self.setup_shortcuts()
        self.auto_save()
        self.load_files()

    def setup_ui(self):
        self.style = ttk.Style()
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        file_menu = Menu(self.menu, tearoff=0)
        file_menu.add_command(label="New File", command=self.new_file)
        file_menu.add_command(label="Open File", command=self.open_file_dialog)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Run", command=self.run_code)
        file_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        file_menu.add_checkbutton(label="Show Sidebar", onvalue=True, offvalue=False, variable=self.sidebar_visible, command=self.toggle_sidebar)
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu.add_cascade(label="File", menu=file_menu)

        self.paned = PanedWindow(self.root, orient=HORIZONTAL)
        self.paned.pack(fill=BOTH, expand=1)

        self.sidebar_frame = Frame(self.paned)
        self.sidebar = Listbox(
            self.sidebar_frame,
            bg="#1c1f26",
            fg="white"
        )
        self.sidebar.pack(side=LEFT, fill=BOTH, expand=True)
        self.sidebar.bind("<<ListboxSelect>>", self.open_file_from_sidebar)
        self.paned.add(self.sidebar_frame, minsize=100)

        self.tab_control = ttk.Notebook(self.paned)
        self.paned.add(self.tab_control)

        self.paned.bind("<B1-Motion>", self.update_sidebar_width)
        self.status_bar = Label(self.root, text="Line: 1 | Column: 0", anchor=E, bg="#2e3440", fg="white")
        self.status_bar.pack(side=BOTTOM, fill=X)
        self.set_theme()

    def update_sidebar_width(self, event):
        new_width = self.sidebar_frame.winfo_width()
        self.sidebar.config(width=max(10, int(new_width / 8)))

    def setup_shortcuts(self):
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-f>", lambda e: self.search_text())
        self.root.bind("<Control-a>", self.select_all)
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)
        self.root.bind("<Control-x>", self.cut)
        self.root.bind("<Control-c>", self.copy)
        self.root.bind("<Control-v>", self.paste)
        self.root.bind("<Control-d>", self.duplicate_line)

    def toggle_sidebar(self):
        if self.sidebar_visible.get():
            self.paned.add(self.sidebar_frame, before=self.tab_control)
        else:
            self.paned.forget(self.sidebar_frame)

    def new_file(self):
        name = simpledialog.askstring("New File", "Enter file name with extension:")
        if name:
            path = os.path.join(APP_DIR, name)
            open(path, "w", encoding="utf-8").close()
            self.sidebar.insert(END, name)
            self.open_file(path)

    def open_file_dialog(self):
        path = filedialog.askopenfilename(initialdir=APP_DIR)
        if path:
            self.open_file(path)

    def open_file_from_sidebar(self, event):
        selection = self.sidebar.curselection()
        if selection:
            filename = self.sidebar.get(selection[0])
            path = os.path.join(APP_DIR, filename)
            self.open_file(path)

    def open_file(self, path):
        for info in self.files.values():
            if info["path"] == path:
                return
        frame = Frame(self.tab_control, bg="#2e3440")
        text = Text(frame, undo=True, wrap="none", bg="#2e3440", fg="white", insertbackground="white", font=("Consolas", 12))
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
                text.insert(1.0, content)
        except:
            return
        text.pack(expand=1, fill='both')
        text.bind("<KeyRelease>", lambda e: self.update_status_bar(text))
        self.tab_control.add(frame, text=os.path.basename(path))
        self.tab_control.select(frame)
        self.files[frame] = {"path": path, "text": text}
        self.update_status_bar(text)

    def save_file(self):
        frame = self.tab_control.select()
        widget = self.root.nametowidget(frame)
        file_info = self.files.get(widget)
        if file_info:
            path = file_info["path"]
            if not path:
                path = filedialog.asksaveasfilename(defaultextension=".py", initialdir=APP_DIR)
                if not path:
                    return
                self.tab_control.tab(widget, text=os.path.basename(path))
                self.files[widget]["path"] = path
                self.sidebar.insert(END, os.path.basename(path))
            content = file_info["text"].get(1.0, END)
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)

    def auto_save(self):
        for frame, file_info in self.files.items():
            path = file_info["path"]
            if path:
                content = file_info["text"].get(1.0, END)
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
        self.root.after(self.auto_save_interval, self.auto_save)

    def run_code(self):
        frame = self.tab_control.select()
        widget = self.root.nametowidget(frame)
        file_info = self.files.get(widget)
        if file_info and file_info["path"]:
            cmd = ["python", file_info["path"]]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout + result.stderr
            self.show_output(output)

    def show_output(self, output):
        output_win = Toplevel(self.root)
        output_win.title("Output")
        text = Text(output_win, wrap="word", bg="black", fg="lime", insertbackground="white")
        text.insert(1.0, output)
        text.pack(expand=1, fill='both')

    def search_text(self):
        frame = self.tab_control.select()
        widget = self.root.nametowidget(frame)
        file_info = self.files.get(widget)
        if file_info:
            text_widget = file_info["text"]
            query = simpledialog.askstring("Search", "Enter search text:")
            if not query:
                return
            text_widget.tag_remove("highlight", "1.0", END)
            idx = "1.0"
            while True:
                idx = text_widget.search(query, idx, nocase=1, stopindex=END)
                if not idx:
                    break
                lastidx = f"{idx}+{len(query)}c"
                text_widget.tag_add("highlight", idx, lastidx)
                idx = lastidx
            text_widget.tag_config("highlight", background="yellow", foreground="black")

    def update_status_bar(self, text_widget):
        try:
            index = text_widget.index(INSERT)
            line, col = index.split(".")
            self.status_bar.config(text=f"Line: {line} | Column: {col}")
        except:
            pass

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.set_theme()
        for file_info in self.files.values():
            text = file_info["text"]
            if self.theme == "dark":
                text.config(bg="#1e1e2e", fg="#c0caf5", insertbackground="#c0caf5")
            else:
                text.config(bg="#ffffff", fg="#2c3e50", insertbackground="#2c3e50")

    def set_theme(self):
        if self.theme == "dark":
            self.root.config(bg="#1e1e2e")
            self.sidebar.config(bg="#1a1b26", fg="#c0caf5", selectbackground="#414868", selectforeground="#ffffff")
            self.status_bar.config(bg="#1a1b26", fg="#c0caf5")
            self.style.configure("TNotebook", background="#1e1e2e", foreground="#c0caf5")
            self.style.configure("TNotebook.Tab", background="#24283b", foreground="#c0caf5", lightcolor="#24283b", borderwidth=0)
        else:
            self.root.config(bg="#f4f4f5")
            self.sidebar.config(bg="#ffffff", fg="#2c3e50", selectbackground="#dcdde1", selectforeground="#2c3e50")
            self.status_bar.config(bg="#dcdde1", fg="#2c3e50")
            self.style.configure("TNotebook", background="#f4f4f5", foreground="#2c3e50")
            self.style.configure("TNotebook.Tab", background="#dcdde1", foreground="#2c3e50", lightcolor="#dcdde1", borderwidth=0)

    def select_all(self, event): self.get_current_text().tag_add("sel", "1.0", "end")
    def undo(self, event): self.get_current_text().event_generate("<<Undo>>")
    def redo(self, event): self.get_current_text().event_generate("<<Redo>>")
    def cut(self, event): self.get_current_text().event_generate("<<Cut>>")
    def copy(self, event): self.get_current_text().event_generate("<<Copy>>")
    def paste(self, event): self.get_current_text().event_generate("<<Paste>>")
    def duplicate_line(self, event):
        text = self.get_current_text()
        index = text.index("insert")
        line_num = index.split('.')[0]
        line_text = text.get(f"{line_num}.0", f"{line_num}.end")
        text.insert(f"{line_num}.end", f"\n{line_text}")

    def get_current_text(self):
        frame = self.tab_control.select()
        widget = self.root.nametowidget(frame)
        return self.files[widget]["text"]

    def load_files(self):
        self.sidebar.delete(0, END)
        for filename in os.listdir(APP_DIR):
            full_path = os.path.join(APP_DIR, filename)
            if os.path.isfile(full_path):
                self.sidebar.insert(END, filename)

root = Tk()
app = CodeNestApp(root)
root.mainloop()
