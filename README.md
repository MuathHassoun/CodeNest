# 💻 Code Nest

**Code Nest** is a lightweight desktop GUI application built with Python's `tkinter` library. Its primary purpose is to store and organize code snippets in various file formats inside a dedicated directory on the user's machine.

---

## 🚀 App Concept

The application provides a simple environment where users can:

- **Create new files** with any extension (`.py`, `.java`, `.txt`, `.md`, etc.).
- **Edit file content** through an integrated editor.
- **Save and update changes** directly to the file.
- **View a list of files** stored in a dedicated folder under the user's home directory (`~/my-code-vault`).
- **Add initial content** while creating a new file.
- **Use keyboard shortcuts** to improve productivity.

---

## 🧠 Key Features

### ✅ Split UI Layout

- **Left Panel:** Displays all files inside the application's storage folder.
- **Right Panel:** A powerful code editor with word wrapping, dark theme styling, and monospace programming fonts.

### ✍️ File Creation

When clicking the **`+ New File`** button:
- A popup window appears asking for:
  - File name.
  - File extension.
  - Optional initial content.
- The new file is saved inside `~/my-code-vault`.

### 💾 Save & Update

- You can update the currently open file by clicking the **`Update`** button.
- Or use the shortcut **`Ctrl + S`** to save quickly.

### ⌨️ Supported Shortcuts

| Shortcut         | Action                    |
|------------------|----------------------------|
| `Ctrl + S`       | Save the current file      |
| `Ctrl + A`       | Select all text            |
| `Ctrl + Z`       | Undo                       |
| `Ctrl + Y`       | Redo                       |
| `Ctrl + C`       | Copy                       |
| `Ctrl + X`       | Cut                        |
| `Ctrl + D`       | Duplicate the current line |

---

## 📁 Storage Directory

- All files are automatically saved in a dedicated folder at:

