# file_manager.py

import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from datetime import datetime
import stat


class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("FileMaster Pro - Файловый менеджер")
        self.root.geometry("1200x600")

        # Текущие пути для левой и правой панелей
        self.left_path = os.path.expanduser("~")
        self.right_path = os.path.expanduser("~")

        self.setup_ui()
        self.load_left_panel()
        self.load_right_panel()

        # Привязка горячих клавиш
        self.setup_hotkeys()

    def setup_ui(self):
        """Создание пользовательского интерфейса"""

        # Главное меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Создать файл", command=lambda: self.create_file(self.get_current_panel()))
        file_menu.add_command(label="Создать папку", command=lambda: self.create_directory(self.get_current_panel()))
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Меню "Правка"
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Копировать", command=lambda: self.copy_item(self.get_current_panel()))
        edit_menu.add_command(label="Переместить", command=lambda: self.move_item(self.get_current_panel()))
        edit_menu.add_command(label="Переименовать", command=lambda: self.rename_item(self.get_current_panel()))
        edit_menu.add_command(label="Удалить", command=lambda: self.delete_item(self.get_current_panel()))

        # Меню "Вид"
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Обновить", command=self.refresh_panels)

        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

        # Основной фрейм для панелей
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Левая панель
        left_frame = ttk.LabelFrame(main_frame, text="Левая панель")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)

        self.left_path_label = ttk.Label(left_frame, text=self.left_path, relief=tk.SUNKEN)
        self.left_path_label.pack(fill=tk.X, padx=2, pady=2)

        self.left_listbox = tk.Listbox(left_frame, height=25)
        self.left_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        left_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.left_listbox.yview)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_listbox.config(yscrollcommand=left_scrollbar.set)

        # Контекстное меню для левой панели
        self.left_listbox.bind("<Button-3>", lambda e: self.show_context_menu(e, "left"))
        self.left_listbox.bind("<Double-Button-1>", lambda e: self.open_item("left"))

        # Правая панель
        right_frame = ttk.LabelFrame(main_frame, text="Правая панель")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2)

        self.right_path_label = ttk.Label(right_frame, text=self.right_path, relief=tk.SUNKEN)
        self.right_path_label.pack(fill=tk.X, padx=2, pady=2)

        self.right_listbox = tk.Listbox(right_frame, height=25)
        self.right_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        right_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.right_listbox.yview)
        right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_listbox.config(yscrollcommand=right_scrollbar.set)

        # Контекстное меню для правой панели
        self.right_listbox.bind("<Button-3>", lambda e: self.show_context_menu(e, "right"))
        self.right_listbox.bind("<Double-Button-1>", lambda e: self.open_item("right"))

        # Панель инструментов
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(toolbar, text="Копировать", command=lambda: self.copy_item(self.get_current_panel())).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Переместить", command=lambda: self.move_item(self.get_current_panel())).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Удалить", command=lambda: self.delete_item(self.get_current_panel())).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Переименовать", command=lambda: self.rename_item(self.get_current_panel())).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Создать папку", command=lambda: self.create_directory(self.get_current_panel())).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Создать файл", command=lambda: self.create_file(self.get_current_panel())).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Поиск", command=self.search_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Свойства", command=lambda: self.show_properties(self.get_current_panel())).pack(
            side=tk.LEFT, padx=2)

        # Статусная строка
        self.status_bar = ttk.Label(self.root, text="Готов к работе", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_hotkeys(self):
        """Настройка горячих клавиш"""
        self.root.bind("<F5>", lambda e: self.copy_item(self.get_current_panel()))
        self.root.bind("<F6>", lambda e: self.move_item(self.get_current_panel()))
        self.root.bind("<F8>", lambda e: self.delete_item(self.get_current_panel()))
        self.root.bind("<F2>", lambda e: self.rename_item(self.get_current_panel()))
        self.root.bind("<F7>", lambda e: self.create_directory(self.get_current_panel()))
        self.root.bind("<Control-f>", lambda e: self.search_item())

    def load_left_panel(self):
        """Загрузка содержимого левой панели"""
        self.load_panel(self.left_listbox, self.left_path, self.left_path_label)

    def load_right_panel(self):
        """Загрузка содержимого правой панели"""
        self.load_panel(self.right_listbox, self.right_path, self.right_path_label)

    def load_panel(self, listbox, path, path_label):
        """Загрузка содержимого панели"""
        listbox.delete(0, tk.END)

        try:
            # Добавляем родительский каталог
            if path != os.path.dirname(path):
                listbox.insert(tk.END, "..")

            # Получаем список файлов и папок
            items = os.listdir(path)

            # Сортируем: сначала папки, потом файлы
            dirs = []
            files = []

            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    dirs.append(f"[Папка] " + item)
                else:
                    size = os.path.getsize(full_path)
                    files.append(f"[Файл] {item} ({self.format_size(size)})")

            # Добавляем в список
            for dir in sorted(dirs):
                listbox.insert(tk.END, dir)
            for file in sorted(files):
                listbox.insert(tk.END, file)

            path_label.config(text=path)
            self.update_status(f"Загружено: {len(dirs)} папок, {len(files)} файлов")

        except PermissionError:
            messagebox.showerror("Ошибка", "Нет прав доступа к каталогу")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def get_current_panel(self):
        """Определение текущей активной панели"""
        if self.root.focus_get() == self.left_listbox:
            return "left"
        else:
            return "right"

    def open_item(self, panel):
        """Открытие элемента (папки или файла)"""
        if panel == "left":
            listbox = self.left_listbox
            current_path = self.left_path
        else:
            listbox = self.right_listbox
            current_path = self.right_path

        selection = listbox.curselection()
        if not selection:
            return

        item_text = listbox.get(selection[0])

        # Обработка перехода вверх
        if item_text == "..":
            new_path = os.path.dirname(current_path)
        else:
            # Извлекаем имя элемента
            if item_text.startswith("[Папка] "):
                item_name = item_text[8:]
            else:
                item_name = item_text.split(" [")[0][8:] if item_text.startswith("[Файл] ") else item_text

            new_path = os.path.join(current_path, item_name)

        # Если это папка - переходим
        if os.path.isdir(new_path):
            if panel == "left":
                self.left_path = new_path
                self.load_left_panel()
            else:
                self.right_path = new_path
                self.load_right_panel()
        # Если это файл - открываем для просмотра/редактирования
        else:
            self.edit_file(new_path)

    def edit_file(self, filepath):
        """Редактирование текстового файла"""
        try:
            # Создаем окно редактирования
            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"Редактирование: {os.path.basename(filepath)}")
            edit_window.geometry("600x400")

            # Текстовое поле
            text_area = tk.Text(edit_window, wrap=tk.WORD)
            text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Загружаем содержимое файла
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    text_area.insert('1.0', content)
            except UnicodeDecodeError:
                with open(filepath, 'r', encoding='cp1251') as f:
                    content = f.read()
                    text_area.insert('1.0', content)

            # Кнопки
            button_frame = ttk.Frame(edit_window)
            button_frame.pack(fill=tk.X, padx=5, pady=5)

            def save_file():
                try:
                    content = text_area.get('1.0', tk.END)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    messagebox.showinfo("Успех", "Файл сохранен")
                    edit_window.destroy()
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))

            ttk.Button(button_frame, text="Сохранить", command=save_file).pack(side=tk.LEFT, padx=2)
            ttk.Button(button_frame, text="Отмена", command=edit_window.destroy).pack(side=tk.LEFT, padx=2)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")

    def create_file(self, panel):
        """Создание нового файла"""
        if panel == "left":
            current_path = self.left_path
        else:
            current_path = self.right_path

        filename = simpledialog.askstring("Создание файла", "Введите имя файла:")
        if filename:
            filepath = os.path.join(current_path, filename)
            try:
                with open(filepath, 'w') as f:
                    f.write("")
                self.refresh_panels()
                self.update_status(f"Файл {filename} создан")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def create_directory(self, panel):
        """Создание новой папки"""
        if panel == "left":
            current_path = self.left_path
        else:
            current_path = self.right_path

        dirname = simpledialog.askstring("Создание папки", "Введите имя папки:")
        if dirname:
            dirpath = os.path.join(current_path, dirname)
            try:
                os.mkdir(dirpath)
                self.refresh_panels()
                self.update_status(f"Папка {dirname} создана")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def copy_item(self, panel):
        """Копирование элемента"""
        if panel == "left":
            source_listbox = self.left_listbox
            source_path = self.left_path
            dest_path = self.right_path
        else:
            source_listbox = self.right_listbox
            source_path = self.right_path
            dest_path = self.left_path

        selection = source_listbox.curselection()
        if not selection:
            return

        item_text = source_listbox.get(selection[0])

        # Извлекаем имя элемента
        if item_text == "..":
            return

        if item_text.startswith("[Папка] "):
            item_name = item_text[8:]
        else:
            item_name = item_text.split(" [")[0][8:] if item_text.startswith("[Файл] ") else item_text

        source_item = os.path.join(source_path, item_name)
        dest_item = os.path.join(dest_path, item_name)

        try:
            if os.path.isdir(source_item):
                shutil.copytree(source_item, dest_item)
                self.update_status(f"Папка {item_name} скопирована")
            else:
                shutil.copy2(source_item, dest_item)
                self.update_status(f"Файл {item_name} скопирован")

            self.refresh_panels()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def move_item(self, panel):
        """Перемещение элемента"""
        if panel == "left":
            source_listbox = self.left_listbox
            source_path = self.left_path
            dest_path = self.right_path
        else:
            source_listbox = self.right_listbox
            source_path = self.right_path
            dest_path = self.left_path

        selection = source_listbox.curselection()
        if not selection:
            return

        item_text = source_listbox.get(selection[0])

        if item_text == "..":
            return

        if item_text.startswith("[Папка] "):
            item_name = item_text[8:]
        else:
            item_name = item_text.split(" [")[0][8:] if item_text.startswith("[Файл] ") else item_text

        source_item = os.path.join(source_path, item_name)
        dest_item = os.path.join(dest_path, item_name)

        try:
            shutil.move(source_item, dest_item)
            self.update_status(f"Элемент {item_name} перемещен")
            self.refresh_panels()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def rename_item(self, panel):
        """Переименование элемента"""
        if panel == "left":
            listbox = self.left_listbox
            current_path = self.left_path
        else:
            listbox = self.right_listbox
            current_path = self.right_path

        selection = listbox.curselection()
        if not selection:
            return

        item_text = listbox.get(selection[0])

        if item_text == "..":
            return

        if item_text.startswith("[Папка] "):
            item_name = item_text[8:]
            item_type = "папку"
        else:
            item_name = item_text.split(" [")[0][8:] if item_text.startswith("[Файл] ") else item_text
            item_type = "файл"

        new_name = simpledialog.askstring("Переименование", f"Введите новое имя для {item_type}:",
                                          initialvalue=item_name)

        if new_name and new_name != item_name:
            old_path = os.path.join(current_path, item_name)
            new_path = os.path.join(current_path, new_name)

            try:
                os.rename(old_path, new_path)
                self.update_status(f"Элемент переименован в {new_name}")
                self.refresh_panels()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def delete_item(self, panel):
        """Удаление элемента"""
        if panel == "left":
            listbox = self.left_listbox
            current_path = self.left_path
        else:
            listbox = self.right_listbox
            current_path = self.right_path

        selection = listbox.curselection()
        if not selection:
            return

        item_text = listbox.get(selection[0])

        if item_text == "..":
            return

        if item_text.startswith("[Папка] "):
            item_name = item_text[8:]
            item_type = "папку"
        else:
            item_name = item_text.split(" [")[0][8:] if item_text.startswith("[Файл] ") else item_text
            item_type = "файл"

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить {item_type} '{item_name}'?"):
            item_path = os.path.join(current_path, item_name)

            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)

                self.update_status(f"Элемент {item_name} удален")
                self.refresh_panels()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def search_item(self):
        """Поиск файлов и папок"""
        search_term = simpledialog.askstring("Поиск", "Введите имя для поиска:")
        if not search_term:
            return

        panel = self.get_current_panel()
        if panel == "left":
            search_path = self.left_path
        else:
            search_path = self.right_path

        results = []

        for root, dirs, files in os.walk(search_path):
            for dir in dirs:
                if search_term.lower() in dir.lower():
                    results.append(os.path.join(root, dir))

            for file in files:
                if search_term.lower() in file.lower():
                    results.append(os.path.join(root, file))

        # Показываем результаты
        if results:
            result_window = tk.Toplevel(self.root)
            result_window.title("Результаты поиска")
            result_window.geometry("500x300")

            result_listbox = tk.Listbox(result_window)
            result_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            for result in results[:100]:  # Ограничиваем 100 результатами
                result_listbox.insert(tk.END, result)

            def open_selected():
                selection = result_listbox.curselection()
                if selection:
                    path = result_listbox.get(selection[0])
                    if os.path.isdir(path):
                        if panel == "left":
                            self.left_path = path
                            self.load_left_panel()
                        else:
                            self.right_path = path
                            self.load_right_panel()
                    else:
                        self.edit_file(path)
                    result_window.destroy()

            ttk.Button(result_window, text="Открыть", command=open_selected).pack(pady=5)

            self.update_status(f"Найдено {len(results)} элементов")
        else:
            messagebox.showinfo("Поиск", "Ничего не найдено")

    def show_properties(self, panel):
        """Просмотр свойств элемента"""
        if panel == "left":
            listbox = self.left_listbox
            current_path = self.left_path
        else:
            listbox = self.right_listbox
            current_path = self.right_path

        selection = listbox.curselection()
        if not selection:
            # Показываем свойства текущего каталога
            item_path = current_path
            item_name = os.path.basename(current_path) or current_path
        else:
            item_text = listbox.get(selection[0])

            if item_text == "..":
                item_path = os.path.dirname(current_path)
                item_name = ".."
            else:
                if item_text.startswith("[Папка] "):
                    item_name = item_text[8:]
                else:
                    item_name = item_text.split(" [")[0][8:] if item_text.startswith("[Файл] ") else item_text

                item_path = os.path.join(current_path, item_name)

        try:
            stats = os.stat(item_path)

            # Формируем информацию о свойствах
            properties = f"Имя: {item_name}\n"
            properties += f"Полный путь: {item_path}\n"
            properties += f"Тип: {'Папка' if os.path.isdir(item_path) else 'Файл'}\n"
            properties += f"Размер: {self.format_size(stats.st_size)}\n"
            properties += f"Дата создания: {datetime.fromtimestamp(stats.st_ctime)}\n"
            properties += f"Дата изменения: {datetime.fromtimestamp(stats.st_mtime)}\n"
            properties += f"Дата доступа: {datetime.fromtimestamp(stats.st_atime)}\n"

            # Атрибуты (для Windows)
            if os.name == 'nt':
                attrs = []
                if stats.st_file_attributes & stat.FILE_ATTRIBUTE_READONLY:
                    attrs.append("Только чтение")
                if stats.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN:
                    attrs.append("Скрытый")
                if stats.st_file_attributes & stat.FILE_ATTRIBUTE_SYSTEM:
                    attrs.append("Системный")

                properties += f"Атрибуты: {', '.join(attrs) if attrs else 'Нет'}\n"

            # Права доступа (для Unix)
            if os.name != 'nt':
                mode = stats.st_mode
                permissions = ""
                permissions += "r" if mode & stat.S_IRUSR else "-"
                permissions += "w" if mode & stat.S_IWUSR else "-"
                permissions += "x" if mode & stat.S_IXUSR else "-"
                permissions += "r" if mode & stat.S_IRGRP else "-"
                permissions += "w" if mode & stat.S_IWGRP else "-"
                permissions += "x" if mode & stat.S_IXGRP else "-"
                permissions += "r" if mode & stat.S_IROTH else "-"
                permissions += "w" if mode & stat.S_IWOTH else "-"
                permissions += "x" if mode & stat.S_IXOTH else "-"

                properties += f"Права доступа: {permissions}\n"

            messagebox.showinfo("Свойства", properties)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def format_size(self, size):
        """Форматирование размера файла"""
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} ТБ"

    def show_context_menu(self, event, panel):
        """Показ контекстного меню"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Открыть", command=lambda: self.open_item(panel))
        context_menu.add_separator()
        context_menu.add_command(label="Копировать", command=lambda: self.copy_item(panel))
        context_menu.add_command(label="Переместить", command=lambda: self.move_item(panel))
        context_menu.add_command(label="Переименовать", command=lambda: self.rename_item(panel))
        context_menu.add_command(label="Удалить", command=lambda: self.delete_item(panel))
        context_menu.add_separator()
        context_menu.add_command(label="Свойства", command=lambda: self.show_properties(panel))

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def refresh_panels(self):
        """Обновление обеих панелей"""
        self.load_left_panel()
        self.load_right_panel()

    def update_status(self, message):
        """Обновление статусной строки"""
        self.status_bar.config(text=message)

    def show_about(self):
        """Информация о программе"""
        about_text = """FileMaster Pro v1.0

Файловый менеджер с двухпанельным интерфейсом

Разработано в соответствии с ТЗ
Функции:
- Управление файлами и папками
- Просмотр и редактирование
- Копирование, перемещение, удаление
- Поиск и свойства
- Изменение атрибутов

Горячие клавиши:
F5 - Копировать
F6 - Переместить
F7 - Создать папку
F8 - Удалить
F2 - Переименовать
Ctrl+F - Поиск"""

        messagebox.showinfo("О программе", about_text)


def main():
    root = tk.Tk()
    app = FileManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()