import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import math


class Room:
    """Класс, представляющий комнату"""

    def __init__(self, x, y, width, height, name="Комната"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.color = "#E8F0F8"  # Светло-голубой по умолчанию
        self.selected = False

    def area(self):
        """Вычисление площади комнаты"""
        return self.width * self.height

    def contains_point(self, px, py):
        """Проверка, содержит ли комната точку с заданными координатами"""
        return (self.x <= px <= self.x + self.width and
                self.y <= py <= self.y + self.height)


class ArchitecturalPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Архитектурный планировщик - Лабораторная работа №5")
        self.root.geometry("1200x700")

        # Переменные для проекта
        self.rooms = []
        self.selected_room = None
        self.drag_data = {"x": 0, "y": 0, "item": None, "dragging": False}
        self.resizing = False
        self.resize_handle = None
        self.grid_size = 20  # Размер сетки для привязки

        # Настройка стилей
        self.setup_styles()

        # Создание интерфейса
        self.create_widgets()

        # Привязка событий
        self.setup_bindings()

        # Обновление статуса
        self.update_status()

    def setup_styles(self):
        """Настройка стилей для виджетов"""
        style = ttk.Style()
        style.theme_use('clam')

        # Настройка цветов
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))

    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель с элементами управления
        left_panel = ttk.Frame(main_frame, width=250, relief=tk.SUNKEN, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        # Заголовок левой панели
        ttk.Label(left_panel, text="Управление проектом", style='Title.TLabel').pack(pady=10)

        # Фрейм для создания нового проекта
        create_frame = ttk.LabelFrame(left_panel, text="Создать проект", padding="10")
        create_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(create_frame, text="Ширина (м):").pack(anchor=tk.W)
        self.project_width = ttk.Entry(create_frame, width=15)
        self.project_width.insert(0, "800")
        self.project_width.pack(fill=tk.X, pady=2)

        ttk.Label(create_frame, text="Высота (м):").pack(anchor=tk.W)
        self.project_height = ttk.Entry(create_frame, width=15)
        self.project_height.insert(0, "600")
        self.project_height.pack(fill=tk.X, pady=2)

        ttk.Button(create_frame, text="Создать новый проект",
                   command=self.create_new_project).pack(fill=tk.X, pady=5)

        # Фрейм для добавления комнат
        add_frame = ttk.LabelFrame(left_panel, text="Добавить комнату", padding="10")
        add_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(add_frame, text="Название:").pack(anchor=tk.W)
        self.room_name = ttk.Entry(add_frame, width=15)
        self.room_name.insert(0, "Гостиная")
        self.room_name.pack(fill=tk.X, pady=2)

        ttk.Label(add_frame, text="Ширина (м):").pack(anchor=tk.W)
        self.room_width = ttk.Entry(add_frame, width=15)
        self.room_width.insert(0, "200")
        self.room_width.pack(fill=tk.X, pady=2)

        ttk.Label(add_frame, text="Высота (м):").pack(anchor=tk.W)
        self.room_height = ttk.Entry(add_frame, width=15)
        self.room_height.insert(0, "150")
        self.room_height.pack(fill=tk.X, pady=2)

        ttk.Button(add_frame, text="Добавить комнату",
                   command=self.add_room).pack(fill=tk.X, pady=5)

        # Фрейм для свойств выбранной комнаты
        self.properties_frame = ttk.LabelFrame(left_panel, text="Свойства комнаты", padding="10")
        self.properties_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.properties_frame, text="Название:").pack(anchor=tk.W)
        self.edit_name = ttk.Entry(self.properties_frame, width=15)
        self.edit_name.pack(fill=tk.X, pady=2)
        self.edit_name.bind('<KeyRelease>', self.update_room_name)

        ttk.Label(self.properties_frame, text="Цвет:").pack(anchor=tk.W)
        color_frame = ttk.Frame(self.properties_frame)
        color_frame.pack(fill=tk.X, pady=2)
        self.color_preview = tk.Canvas(color_frame, width=30, height=20, bg='#E8F0F8', highlightthickness=1)
        self.color_preview.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(color_frame, text="Выбрать цвет", command=self.choose_color).pack(side=tk.LEFT)

        ttk.Button(self.properties_frame, text="Удалить комнату",
                   command=self.delete_selected_room).pack(fill=tk.X, pady=5)

        # Фрейм для информации
        info_frame = ttk.LabelFrame(left_panel, text="Информация", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.info_text = tk.Text(info_frame, height=8, width=25, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X)

        # Центральная область - холст для рисования
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Заголовок холста
        ttk.Label(canvas_frame, text="План помещения", style='Title.TLabel').pack(pady=5)

        # Холст с прокруткой
        self.canvas = tk.Canvas(canvas_frame, bg='white', width=800, height=600,
                                highlightbackground='#CCCCCC', highlightthickness=2)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Нижняя панель статуса
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(status_frame, text="Готов к работе", style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=2)

        self.coord_label = ttk.Label(status_frame, text="", style='Status.TLabel')
        self.coord_label.pack(side=tk.RIGHT, padx=10, pady=2)

        # Отключаем свойства комнаты пока ничего не выбрано
        self.set_properties_state(tk.DISABLED)

    def setup_bindings(self):
        """Настройка привязок событий"""
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Configure>", self.redraw_canvas)

        # Привязка клавиш
        self.root.bind('<Delete>', lambda e: self.delete_selected_room())
        self.root.bind('<Escape>', lambda e: self.deselect_all())

    def create_new_project(self):
        """Создание нового проекта"""
        try:
            width = float(self.project_width.get())
            height = float(self.project_height.get())

            if width <= 0 or height <= 0:
                messagebox.showerror("Ошибка", "Размеры должны быть положительными числами")
                return

            self.rooms.clear()
            self.selected_room = None
            self.deselect_all()
            self.redraw_canvas()
            self.update_status()

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")

    def add_room(self):
        """Добавление новой комнаты"""
        try:
            name = self.room_name.get().strip()
            if not name:
                name = "Комната"

            width = float(self.room_width.get())
            height = float(self.room_height.get())

            if width <= 0 or height <= 0:
                messagebox.showerror("Ошибка", "Размеры комнаты должны быть положительными числами")
                return

            # Размещаем комнату в случайном месте в пределах видимой области
            x = 50 + len(self.rooms) * 30
            y = 50 + len(self.rooms) * 30

            room = Room(x, y, width, height, name)
            self.rooms.append(room)
            self.redraw_canvas()
            self.update_status()

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")

    def redraw_canvas(self, event=None):
        """Перерисовка холста"""
        self.canvas.delete("all")

        # Рисуем сетку
        self.draw_grid()

        # Рисуем все комнаты
        for room in self.rooms:
            self.draw_room(room)

        # Обновляем информацию
        self.update_info()

    def draw_grid(self):
        """Рисование сетки"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Рисуем линии сетки
        for x in range(0, width, self.grid_size):
            self.canvas.create_line(x, 0, x, height, fill='#F0F0F0', tags="grid")

        for y in range(0, height, self.grid_size):
            self.canvas.create_line(0, y, width, y, fill='#F0F0F0', tags="grid")

    def draw_room(self, room):
        """Рисование отдельной комнаты"""
        # Основной прямоугольник комнаты
        fill_color = room.color if not room.selected else self.lighten_color(room.color, 0.9)
        outline_color = 'red' if room.selected else 'black'
        outline_width = 3 if room.selected else 1

        rect = self.canvas.create_rectangle(
            room.x, room.y, room.x + room.width, room.y + room.height,
            fill=fill_color, outline=outline_color, width=outline_width,
            tags=("room", f"room_{self.rooms.index(room)}")
        )

        # Название комнаты
        self.canvas.create_text(
            room.x + room.width / 2, room.y + room.height / 2 - 15,
            text=room.name, font=('Arial', 10, 'bold'), tags="room_text"
        )

        # Площадь
        self.canvas.create_text(
            room.x + room.width / 2, room.y + room.height / 2,
            text=f"Площадь: {room.area():.1f} м²", font=('Arial', 9), tags="room_text"
        )

        # Размеры
        self.canvas.create_text(
            room.x + room.width / 2, room.y + room.height / 2 + 15,
            text=f"{room.width}×{room.height}", font=('Arial', 9), tags="room_text"
        )

        # Маркеры для изменения размера (если комната выбрана)
        if room.selected:
            self.draw_resize_handles(room)

    def draw_resize_handles(self, room):
        """Рисование маркеров для изменения размера"""
        handle_size = 8
        handles = [
            (room.x + room.width - handle_size / 2, room.y + room.height - handle_size / 2),  # нижний правый
            (room.x + room.width - handle_size / 2, room.y - handle_size / 2),  # верхний правый
            (room.x - handle_size / 2, room.y + room.height - handle_size / 2),  # нижний левый
            (room.x - handle_size / 2, room.y - handle_size / 2),  # верхний левый
        ]

        for x, y in handles:
            self.canvas.create_rectangle(
                x, y, x + handle_size, y + handle_size,
                fill='white', outline='blue', width=2,
                tags=("resize_handle",)
            )

    def on_canvas_click(self, event):
        """Обработка клика на холсте"""
        x, y = event.x, event.y

        # Проверяем, не кликнули ли на маркер изменения размера
        items = self.canvas.find_overlapping(x - 5, y - 5, x + 5, y + 5)
        for item in items:
            tags = self.canvas.gettags(item)
            if "resize_handle" in tags and self.selected_room:
                self.resizing = True
                self.drag_data = {"x": x, "y": y, "room": self.selected_room}
                return

        # Проверяем, кликнули ли на комнату
        clicked_room = None
        for room in reversed(self.rooms):
            if room.contains_point(x, y):
                clicked_room = room
                break

        if clicked_room:
            # Выбираем комнату
            self.select_room(clicked_room)
            self.drag_data = {"x": x, "y": y, "room": clicked_room, "dragging": True}
        else:
            # Снимаем выделение
            self.deselect_all()

    def on_canvas_drag(self, event):
        """Обработка перетаскивания"""
        if self.resizing and self.selected_room:
            # Изменение размера
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]

            # Привязка к сетке
            new_width = max(50, self.selected_room.width + dx)
            new_height = max(50, self.selected_room.height + dy)

            # Округляем до ближайшего размера сетки
            new_width = round(new_width / self.grid_size) * self.grid_size
            new_height = round(new_height / self.grid_size) * self.grid_size

            self.selected_room.width = new_width
            self.selected_room.height = new_height

            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.redraw_canvas()

        elif self.drag_data.get("dragging") and self.selected_room:
            # Перемещение комнаты
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]

            # Привязка к сетке
            new_x = self.selected_room.x + dx
            new_y = self.selected_room.y + dy

            # Округляем до ближайшего узла сетки
            new_x = round(new_x / self.grid_size) * self.grid_size
            new_y = round(new_y / self.grid_size) * self.grid_size

            self.selected_room.x = new_x
            self.selected_room.y = new_y

            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.redraw_canvas()

    def on_canvas_release(self, event):
        """Обработка отпускания кнопки мыши"""
        self.drag_data = {"x": 0, "y": 0, "item": None, "dragging": False}
        self.resizing = False

    def on_mouse_move(self, event):
        """Отображение координат мыши"""
        self.coord_label.config(text=f"X: {event.x}, Y: {event.y}")

    def select_room(self, room):
        """Выбор комнаты"""
        self.deselect_all()
        room.selected = True
        self.selected_room = room

        # Обновляем поля свойств
        self.edit_name.delete(0, tk.END)
        self.edit_name.insert(0, room.name)
        self.color_preview.config(bg=room.color)

        self.set_properties_state(tk.NORMAL)
        self.redraw_canvas()

    def deselect_all(self):
        """Снятие выделения со всех комнат"""
        for room in self.rooms:
            room.selected = False
        self.selected_room = None
        self.set_properties_state(tk.DISABLED)
        self.redraw_canvas()

    def set_properties_state(self, state):
        """Установка состояния полей свойств"""
        self.edit_name.config(state=state)
        self.color_preview.config(state=state)

    def update_room_name(self, event=None):
        """Обновление названия комнаты"""
        if self.selected_room:
            self.selected_room.name = self.edit_name.get()
            self.redraw_canvas()

    def choose_color(self):
        """Выбор цвета для комнаты"""
        if self.selected_room:
            color = colorchooser.askcolor(title="Выберите цвет комнаты",
                                          initialcolor=self.selected_room.color)
            if color[1]:  # color[1] содержит шестнадцатеричное значение
                self.selected_room.color = color[1]
                self.color_preview.config(bg=color[1])
                self.redraw_canvas()

    def delete_selected_room(self):
        """Удаление выбранной комнаты"""
        if self.selected_room and messagebox.askyesno("Подтверждение",
                                                      "Удалить выбранную комнату?"):
            self.rooms.remove(self.selected_room)
            self.deselect_all()
            self.redraw_canvas()
            self.update_status()

    def lighten_color(self, color, factor):
        """Осветление цвета"""
        # Конвертируем hex в RGB
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))

        # Осветляем
        lightened = tuple(min(255, int(c * factor)) for c in rgb)

        # Конвертируем обратно в hex
        return '#{:02x}{:02x}{:02x}'.format(*lightened)

    def update_info(self):
        """Обновление информационного текста"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        total_area = sum(room.area() for room in self.rooms)

        info = f"Всего комнат: {len(self.rooms)}\n"
        info += f"Общая площадь: {total_area:.1f} м²\n\n"
        info += "Комнаты:\n"

        for i, room in enumerate(self.rooms, 1):
            info += f"{i}. {room.name}\n"
            info += f"   {room.width}×{room.height}\n"
            info += f"   {room.area():.1f} м²\n\n"

        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)

    def update_status(self):
        """Обновление статусной строки"""
        total_area = sum(room.area() for room in self.rooms)
        self.status_label.config(
            text=f"Комнат: {len(self.rooms)} | Общая площадь: {total_area:.1f} м²"
        )


def main():
    root = tk.Tk()
    app = ArchitecturalPlanner(root)
    root.mainloop()


if __name__ == "__main__":
    main()