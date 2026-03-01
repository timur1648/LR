import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import json
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import os


class Database:
    """Класс для представления базы данных"""

    def __init__(self, name):
        self.name = name
        self.data = []  # Список записей
        self.fields = []  # Названия полей
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_record(self, record):
        """Добавление записи"""
        self.data.append(record)

    def delete_record(self, index):
        """Удаление записи по индексу"""
        if 0 <= index < len(self.data):
            return self.data.pop(index)
        return None

    def update_record(self, index, new_record):
        """Обновление записи"""
        if 0 <= index < len(self.data):
            self.data[index] = new_record
            return True
        return False

    def sort_data(self, field_index, reverse=False):
        """Сортировка данных по полю"""
        if self.data and 0 <= field_index < len(self.fields):
            self.data.sort(key=lambda x: x[field_index], reverse=reverse)

    def search_data(self, field_index, search_term):
        """Поиск данных по полю"""
        if not search_term:
            return self.data.copy()

        results = []
        for record in self.data:
            if 0 <= field_index < len(record):
                if str(search_term).lower() in str(record[field_index]).lower():
                    results.append(record)
        return results


class DatabaseManager:
    """Класс для управления несколькими базами данных"""

    def __init__(self):
        self.databases = {}
        self.current_db = None

    def create_database(self, name, fields):
        """Создание новой базы данных"""
        if name not in self.databases:
            db = Database(name)
            db.fields = fields
            self.databases[name] = db
            self.current_db = name
            return True
        return False

    def delete_database(self, name):
        """Удаление базы данных"""
        if name in self.databases:
            del self.databases[name]
            if self.current_db == name:
                self.current_db = None
            return True
        return False

    def get_current_db(self):
        """Получение текущей базы данных"""
        if self.current_db and self.current_db in self.databases:
            return self.databases[self.current_db]
        return None


class DatabaseGUI:
    """Графический интерфейс программы"""

    def __init__(self, root):
        self.root = root
        self.root.title("Система управления базами данных")
        self.root.geometry("1200x700")

        self.manager = DatabaseManager()

        # Установка стиля
        style = ttk.Style()
        style.theme_use('clam')

        # Создание меню
        self.create_menu()

        # Создание основной панели
        self.create_main_panel()

        # Статус бар
        self.status_bar = ttk.Label(root, text="Готов к работе", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu(self):
        """Создание главного меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Создать БД", command=self.create_database_dialog)
        file_menu.add_command(label="Открыть БД", command=self.open_database)
        file_menu.add_command(label="Сохранить", command=self.save_database)
        file_menu.add_separator()
        file_menu.add_command(label="Импорт", command=self.import_data)
        file_menu.add_command(label="Экспорт", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Меню "Правка"
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Добавить запись", command=self.add_record_dialog)
        edit_menu.add_command(label="Редактировать запись", command=self.edit_record_dialog)
        edit_menu.add_command(label="Удалить запись", command=self.delete_record)
        edit_menu.add_separator()
        edit_menu.add_command(label="Сортировать", command=self.sort_dialog)
        edit_menu.add_command(label="Поиск", command=self.search_dialog)

        # Меню "Отчеты"
        report_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Отчеты", menu=report_menu)
        report_menu.add_command(label="Создать отчет", command=self.create_report)
        report_menu.add_command(label="Статистика", command=self.show_statistics)

        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="Содержание", command=self.show_help)
        help_menu.add_command(label="О программе", command=self.show_about)

    def create_main_panel(self):
        """Создание основной рабочей области"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Панель слева (список БД и информация)
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)

        ttk.Label(left_frame, text="Базы данных", font=('Arial', 12, 'bold')).pack(pady=5)

        # Список баз данных
        self.db_listbox = tk.Listbox(left_frame, height=10)
        self.db_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.db_listbox.bind('<<ListboxSelect>>', self.on_db_select)

        ttk.Button(left_frame, text="Обновить список",
                   command=self.refresh_db_list).pack(pady=5)

        # Информация о текущей БД
        self.info_frame = ttk.LabelFrame(left_frame, text="Информация", padding="5")
        self.info_frame.pack(fill=tk.BOTH, pady=10)

        self.info_text = tk.Text(self.info_frame, height=8, width=30, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH)

        # Панель справа (данные)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Панель инструментов
        toolbar = ttk.Frame(right_frame)
        toolbar.pack(fill=tk.X, pady=5)

        ttk.Button(toolbar, text="Добавить", command=self.add_record_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Изменить", command=self.edit_record_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Удалить", command=self.delete_record).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Сортировать", command=self.sort_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Поиск", command=self.search_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Обновить", command=self.refresh_table).pack(side=tk.LEFT, padx=2)

        # Таблица данных
        self.table_frame = ttk.Frame(right_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        # Создаем Treeview с прокруткой
        self.tree = ttk.Treeview(self.table_frame, show="headings")
        scrollbar_y = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)

        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Поле поиска
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Button(search_frame, text="Найти", command=self.perform_search).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="Сброс", command=self.refresh_table).pack(side=tk.LEFT, padx=5)

        self.refresh_db_list()

    def create_database_dialog(self):
        """Диалог создания новой базы данных"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Создание базы данных")
        dialog.geometry("400x300")

        ttk.Label(dialog, text="Название базы данных:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)

        ttk.Label(dialog, text="Поля (через запятую):").pack(pady=5)
        fields_entry = ttk.Entry(dialog, width=40)
        fields_entry.pack(pady=5)
        ttk.Label(dialog, text="Пример: id, имя, возраст, город").pack()

        def create():
            name = name_entry.get().strip()
            fields_str = fields_entry.get().strip()

            if not name or not fields_str:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            fields = [f.strip() for f in fields_str.split(',')]

            if self.manager.create_database(name, fields):
                messagebox.showinfo("Успех", f"База данных '{name}' создана")
                dialog.destroy()
                self.refresh_db_list()
                self.update_info()
                self.setup_table_columns(fields)
            else:
                messagebox.showerror("Ошибка", "База данных с таким именем уже существует")

        ttk.Button(dialog, text="Создать", command=create).pack(pady=20)

    def add_record_dialog(self):
        """Диалог добавления записи"""
        db = self.manager.get_current_db()
        if not db:
            messagebox.showwarning("Предупреждение", "Выберите базу данных")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление записи")
        dialog.geometry("400x400")

        entries = {}
        for i, field in enumerate(db.fields):
            ttk.Label(dialog, text=f"{field}:").pack(pady=2)
            entry = ttk.Entry(dialog, width=40)
            entry.pack(pady=2)
            entries[field] = entry

        def add():
            record = [entries[field].get().strip() for field in db.fields]

            # Проверка заполнения обязательных полей
            if not all(record):
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            db.add_record(record)
            self.refresh_table()
            self.update_info()
            dialog.destroy()
            messagebox.showinfo("Успех", "Запись добавлена")

        ttk.Button(dialog, text="Добавить", command=add).pack(pady=20)

    def edit_record_dialog(self):
        """Диалог редактирования записи"""
        db = self.manager.get_current_db()
        if not db:
            messagebox.showwarning("Предупреждение", "Выберите базу данных")
            return

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования")
            return

        index = int(self.tree.item(selection[0])['values'][0]) - 1

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование записи")
        dialog.geometry("400x400")

        entries = {}
        current_record = db.data[index]

        for i, field in enumerate(db.fields):
            ttk.Label(dialog, text=f"{field}:").pack(pady=2)
            entry = ttk.Entry(dialog, width=40)
            entry.insert(0, current_record[i])
            entry.pack(pady=2)
            entries[field] = entry

        def update():
            new_record = [entries[field].get().strip() for field in db.fields]

            if not all(new_record):
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            db.update_record(index, new_record)
            self.refresh_table()
            dialog.destroy()
            messagebox.showinfo("Успех", "Запись обновлена")

        ttk.Button(dialog, text="Обновить", command=update).pack(pady=20)

    def delete_record(self):
        """Удаление записи"""
        db = self.manager.get_current_db()
        if not db:
            messagebox.showwarning("Предупреждение", "Выберите базу данных")
            return

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            index = int(self.tree.item(selection[0])['values'][0]) - 1
            db.delete_record(index)
            self.refresh_table()
            self.update_info()

    def sort_dialog(self):
        """Диалог сортировки"""
        db = self.manager.get_current_db()
        if not db or not db.data:
            messagebox.showwarning("Предупреждение", "Нет данных для сортировки")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Сортировка")
        dialog.geometry("300x200")

        ttk.Label(dialog, text="Поле для сортировки:").pack(pady=5)

        field_var = tk.StringVar()
        field_combo = ttk.Combobox(dialog, textvariable=field_var, values=db.fields, state='readonly')
        field_combo.pack(pady=5)

        ttk.Label(dialog, text="Направление:").pack(pady=5)

        order_var = tk.BooleanVar()
        ttk.Radiobutton(dialog, text="По возрастанию", variable=order_var, value=False).pack()
        ttk.Radiobutton(dialog, text="По убыванию", variable=order_var, value=True).pack()

        def sort():
            if not field_var.get():
                messagebox.showerror("Ошибка", "Выберите поле")
                return

            field_index = db.fields.index(field_var.get())
            db.sort_data(field_index, order_var.get())
            self.refresh_table()
            dialog.destroy()

        ttk.Button(dialog, text="Сортировать", command=sort).pack(pady=20)

    def search_dialog(self):
        """Диалог поиска"""
        db = self.manager.get_current_db()
        if not db:
            messagebox.showwarning("Предупреждение", "Выберите базу данных")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Поиск")
        dialog.geometry("300x250")

        ttk.Label(dialog, text="Поле для поиска:").pack(pady=5)

        field_var = tk.StringVar()
        field_combo = ttk.Combobox(dialog, textvariable=field_var, values=db.fields, state='readonly')
        field_combo.pack(pady=5)

        ttk.Label(dialog, text="Текст для поиска:").pack(pady=5)
        search_entry = ttk.Entry(dialog, width=30)
        search_entry.pack(pady=5)

        def search():
            if not field_var.get():
                messagebox.showerror("Ошибка", "Выберите поле")
                return

            field_index = db.fields.index(field_var.get())
            search_term = search_entry.get().strip()

            results = db.search_data(field_index, search_term)
            self.display_search_results(results)
            dialog.destroy()

        ttk.Button(dialog, text="Найти", command=search).pack(pady=20)

    def perform_search(self):
        """Выполнение поиска из основного окна"""
        db = self.manager.get_current_db()
        if not db:
            return

        search_term = self.search_var.get().strip()
        if search_term:
            # Поиск по всем полям
            results = []
            for record in db.data:
                if any(search_term.lower() in str(value).lower() for value in record):
                    results.append(record)
            self.display_search_results(results)

    def display_search_results(self, results):
        """Отображение результатов поиска"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, record in enumerate(results, 1):
            self.tree.insert('', 'end', values=[i] + record)

        self.status_bar.config(text=f"Найдено записей: {len(results)}")

    def import_data(self):
        """Импорт данных из файла"""
        db = self.manager.get_current_db()
        if not db:
            messagebox.showwarning("Предупреждение", "Выберите базу данных")
            return

        file_path = filedialog.askopenfilename(
            title="Выберите файл для импорта",
            filetypes=[
                ("CSV файлы", "*.csv"),
                ("JSON файлы", "*.json"),
                ("XML файлы", "*.xml"),
                ("Excel файлы", "*.xlsx *.xls"),
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            ext = os.path.splitext(file_path)[1].lower()

            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext == '.json':
                df = pd.read_json(file_path)
            elif ext == '.xml':
                df = pd.read_xml(file_path)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif ext == '.txt':
                df = pd.read_csv(file_path, delimiter='\t')
            else:
                messagebox.showerror("Ошибка", "Неподдерживаемый формат файла")
                return

            # Проверка структуры данных
            if list(df.columns) != db.fields:
                if messagebox.askyesno("Внимание",
                                       "Структура полей не совпадает. Продолжить импорт?"):
                    # Обновляем поля
                    db.fields = list(df.columns)
                    self.setup_table_columns(db.fields)

            # Импорт данных
            for _, row in df.iterrows():
                record = [str(row[field]) if field in row else "" for field in db.fields]
                db.add_record(record)

            self.refresh_table()
            self.update_info()
            messagebox.showinfo("Успех", f"Импортировано {len(df)} записей")

        except Exception as e:
            messagebox.showerror("Ошибка импорта", str(e))

    def export_data(self):
        """Экспорт данных в файл"""
        db = self.manager.get_current_db()
        if not db or not db.data:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить файл",
            defaultextension=".csv",
            filetypes=[
                ("CSV файлы", "*.csv"),
                ("JSON файлы", "*.json"),
                ("XML файлы", "*.xml"),
                ("Excel файлы", "*.xlsx"),
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            # Создаем DataFrame
            df = pd.DataFrame(db.data, columns=db.fields)

            ext = os.path.splitext(file_path)[1].lower()

            if ext == '.csv':
                df.to_csv(file_path, index=False)
            elif ext == '.json':
                df.to_json(file_path, orient='records', indent=2)
            elif ext == '.xml':
                df.to_xml(file_path, index=False)
            elif ext in ['.xlsx']:
                df.to_excel(file_path, index=False)
            elif ext == '.txt':
                df.to_csv(file_path, sep='\t', index=False)
            else:
                messagebox.showerror("Ошибка", "Неподдерживаемый формат файла")
                return

            messagebox.showinfo("Успех", f"Данные экспортированы в {file_path}")

        except Exception as e:
            messagebox.showerror("Ошибка экспорта", str(e))

    def save_database(self):
        """Сохранение базы данных"""
        db = self.manager.get_current_db()
        if not db:
            messagebox.showwarning("Предупреждение", "Нет активной базы данных")
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить базу данных",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )

        if not file_path:
            return

        try:
            data_to_save = {
                'name': db.name,
                'fields': db.fields,
                'data': db.data,
                'created_date': db.created_date
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Успех", "База данных сохранена")

        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def open_database(self):
        """Открытие базы данных из файла"""
        file_path = filedialog.askopenfilename(
            title="Открыть базу данных",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            db = Database(data['name'])
            db.fields = data['fields']
            db.data = data['data']
            db.created_date = data.get('created_date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            self.manager.databases[db.name] = db
            self.manager.current_db = db.name

            self.refresh_db_list()
            self.setup_table_columns(db.fields)
            self.refresh_table()
            self.update_info()

            messagebox.showinfo("Успех", f"База данных '{db.name}' загружена")

        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

    def create_report(self):
        """Создание отчета"""
        db = self.manager.get_current_db()
        if not db or not db.data:
            messagebox.showwarning("Предупреждение", "Нет данных для отчета")
            return

        report_window = tk.Toplevel(self.root)
        report_window.title("Отчет по базе данных")
        report_window.geometry("600x400")

        # Создаем текстовый виджет для отчета
        report_text = tk.Text(report_window, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(report_window, command=report_text.yview)
        report_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        report_text.pack(fill=tk.BOTH, expand=True)

        # Формируем отчет
        report = []
        report.append("=" * 80)
        report.append(f"ОТЧЕТ ПО БАЗЕ ДАННЫХ: {db.name.upper()}")
        report.append("=" * 80)
        report.append(f"Дата создания: {db.created_date}")
        report.append(f"Дата отчета: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Количество записей: {len(db.data)}")
        report.append(f"Количество полей: {len(db.fields)}")
        report.append("=" * 80)
        report.append("СТРУКТУРА ПОЛЕЙ:")
        for i, field in enumerate(db.fields, 1):
            report.append(f"  {i}. {field}")
        report.append("=" * 80)
        report.append("ДАННЫЕ:")
        report.append("-" * 80)

        # Заголовки
        header = "№   " + " | ".join([f"{f:<15}" for f in db.fields])
        report.append(header)
        report.append("-" * len(header))

        # Данные
        for i, record in enumerate(db.data, 1):
            line = f"{i:<3} " + " | ".join([f"{str(val):<15}" for val in record])
            report.append(line)

        report.append("=" * 80)
        report.append("СТАТИСТИКА:")
        report.append(f"  Всего записей: {len(db.data)}")

        # Статистика по полям (для числовых полей)
        for field in db.fields:
            try:
                values = []
                for record in db.data:
                    field_index = db.fields.index(field)
                    val = record[field_index]
                    if val.replace('.', '').replace('-', '').isdigit():
                        values.append(float(val))

                if values:
                    report.append(f"\n  Поле '{field}':")
                    report.append(f"    Минимум: {min(values)}")
                    report.append(f"    Максимум: {max(values)}")
                    report.append(f"    Среднее: {sum(values) / len(values):.2f}")
            except:
                pass

        report.append("=" * 80)

        # Вставляем отчет в текстовое поле
        report_text.insert('1.0', '\n'.join(report))
        report_text.config(state=tk.DISABLED)

        # Кнопка сохранения отчета
        def save_report():
            file_path = filedialog.asksaveasfilename(
                title="Сохранить отчет",
                defaultextension=".txt",
                filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(report))
                messagebox.showinfo("Успех", "Отчет сохранен")

        ttk.Button(report_window, text="Сохранить отчет", command=save_report).pack(pady=5)

    def show_statistics(self):
        """Показать статистику по базе данных"""
        db = self.manager.get_current_db()
        if not db:
            messagebox.showwarning("Предупреждение", "Выберите базу данных")
            return

        stats_window = tk.Toplevel(self.root)
        stats_window.title("Статистика")
        stats_window.geometry("400x300")

        stats_text = tk.Text(stats_window, wrap=tk.WORD)
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        stats = []
        stats.append(f"База данных: {db.name}")
        stats.append(f"Дата создания: {db.created_date}")
        stats.append(f"Всего записей: {len(db.data)}")
        stats.append(f"Всего полей: {len(db.fields)}")
        stats.append("\nПоля:")

        for field in db.fields:
            stats.append(f"  • {field}")

        stats_text.insert('1.0', '\n'.join(stats))
        stats_text.config(state=tk.DISABLED)

    def show_help(self):
        """Показать справку"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Справка")
        help_window.geometry("600x400")

        help_text = tk.Text(help_window, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        help_content = """
        СИСТЕМА УПРАВЛЕНИЯ БАЗАМИ ДАННЫХ
        =================================

        ОСНОВНЫЕ ВОЗМОЖНОСТИ:

        1. СОЗДАНИЕ БАЗЫ ДАННЫХ
           • Файл -> Создать БД
           • Укажите название и поля через запятую

        2. РАБОТА С ДАННЫМИ
           • Добавление: кнопка "Добавить"
           • Редактирование: выбрать запись -> "Изменить"
           • Удаление: выбрать запись -> "Удалить"
           • Сортировка: кнопка "Сортировать"
           • Поиск: кнопка "Поиск" или поле поиска внизу

        3. ИМПОРТ/ЭКСПОРТ
           • Импорт: Файл -> Импорт
           • Экспорт: Файл -> Экспорт
           • Поддерживаемые форматы: CSV, JSON, XML, Excel, TXT

        4. ОТЧЕТЫ
           • Отчеты -> Создать отчет
           • Отчеты -> Статистика

        5. ВИЗУАЛИЗАЦИЯ
           • Данные отображаются в таблице
           • Возможность сортировки по столбцам

        ГОРЯЧИЕ КЛАВИШИ:
        • Ctrl+N: создать БД
        • Ctrl+O: открыть БД
        • Ctrl+S: сохранить
        • Ctrl+F: поиск
        • F5: обновить таблицу
        """

        help_text.insert('1.0', help_content)
        help_text.config(state=tk.DISABLED)

    def show_about(self):
        """Показать информацию о программе"""
        about_text = """
        Система управления базами данных
        Версия 1.0

        Лабораторная работа №6
        Разработано для учебных целей

        Функциональность:
        • Создание и управление БД
        • Импорт/экспорт данных
        • Визуализация данных
        • Создание отчетов
        • Поиск и сортировка

        © 2024
        """

        messagebox.showinfo("О программе", about_text)

    def setup_table_columns(self, fields):
        """Настройка колонок таблицы"""
        self.tree.delete(*self.tree.get_children())

        columns = ['№'] + fields
        self.tree['columns'] = columns

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=100, minwidth=50)

    def sort_by_column(self, col):
        """Сортировка по колонке"""
        db = self.manager.get_current_db()
        if not db:
            return

        if col == '№':
            return

        field_index = db.fields.index(col)
        db.sort_data(field_index)
        self.refresh_table()

    def refresh_table(self):
        """Обновление таблицы"""
        db = self.manager.get_current_db()
        if not db:
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, record in enumerate(db.data, 1):
            self.tree.insert('', 'end', values=[i] + record)

        self.status_bar.config(text=f"Всего записей: {len(db.data)}")

    def refresh_db_list(self):
        """Обновление списка баз данных"""
        self.db_listbox.delete(0, tk.END)
        for db_name in self.manager.databases.keys():
            self.db_listbox.insert(tk.END, db_name)

    def on_db_select(self, event):
        """Обработка выбора базы данных"""
        selection = self.db_listbox.curselection()
        if selection:
            db_name = self.db_listbox.get(selection[0])
            self.manager.current_db = db_name
            db = self.manager.get_current_db()

            if db:
                self.setup_table_columns(db.fields)
                self.refresh_table()
                self.update_info()

    def update_info(self):
        """Обновление информации о текущей БД"""
        db = self.manager.get_current_db()

        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete('1.0', tk.END)

        if db:
            info = f"Имя: {db.name}\n"
            info += f"Записей: {len(db.data)}\n"
            info += f"Полей: {len(db.fields)}\n"
            info += f"Создана: {db.created_date}\n\n"
            info += "Поля:\n"
            for field in db.fields:
                info += f"• {field}\n"
        else:
            info = "Нет активной БД"

        self.info_text.insert('1.0', info)
        self.info_text.config(state=tk.DISABLED)


def main():
    """Главная функция программы"""
    root = tk.Tk()
    app = DatabaseGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()