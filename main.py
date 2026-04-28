import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class TrainingPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner / План тренировок")
        self.root.geometry("680x550")
        self.root.resizable(False, False)

        self.data_file = "workouts.json"
        self.workouts = []
        self.workout_types = ["Бег", "Силовая", "Йога", "Плавание", "Велосипед", "HIIT", "Другое"]

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        # --- Ввод данных ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить тренировку", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_date = ttk.Entry(input_frame, width=15)
        self.entry_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Тип тренировки:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.combo_type = ttk.Combobox(input_frame, values=self.workout_types, state="readonly", width=15)
        self.combo_type.grid(row=1, column=1, padx=5, pady=5)
        self.combo_type.current(0)

        ttk.Label(input_frame, text="Длительность (мин):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_duration = ttk.Entry(input_frame, width=15)
        self.entry_duration.grid(row=2, column=1, padx=5, pady=5)

        self.btn_add = ttk.Button(input_frame, text="Добавить тренировку", command=self._add_workout)
        self.btn_add.grid(row=0, column=2, rowspan=3, padx=10, pady=5)

        # --- Фильтрация ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="По типу:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_filter_type = ttk.Combobox(filter_frame, values=["Все"] + self.workout_types, state="readonly", width=15)
        self.combo_filter_type.grid(row=0, column=1, padx=5, pady=5)
        self.combo_filter_type.current(0)

        ttk.Label(filter_frame, text="По дате (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_filter_date = ttk.Entry(filter_frame, width=15)
        self.entry_filter_date.grid(row=0, column=3, padx=5, pady=5)

        self.btn_filter = ttk.Button(filter_frame, text="Применить фильтр", command=self._apply_filter)
        self.btn_filter.grid(row=0, column=4, padx=5, pady=5)

        self.btn_reset = ttk.Button(filter_frame, text="Сбросить", command=self._reset_filter)
        self.btn_reset.grid(row=0, column=5, padx=5, pady=5)

        # --- Таблица ---
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(table_frame, columns=("date", "type", "duration"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("type", width=150, anchor="center")
        self.tree.column("duration", width=100, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # --- Сохранение/Загрузка ---
        io_frame = ttk.Frame(self.root)
        io_frame.pack(fill="x", padx=10, pady=10)

        self.btn_save = ttk.Button(io_frame, text="💾 Сохранить в JSON", command=self._save_data)
        self.btn_save.pack(side="left", padx=5)

        self.btn_load = ttk.Button(io_frame, text="📂 Загрузить из JSON", command=self._load_data)
        self.btn_load.pack(side="left", padx=5)

    def _validate_input(self):
        date_str = self.entry_date.get().strip()
        type_str = self.combo_type.get().strip()
        duration_str = self.entry_duration.get().strip()

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Дата должна быть в формате ГГГГ-ММ-ДД.")
            return False, None, None, None

        try:
            duration = float(duration_str)
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Длительность должна быть положительным числом.")
            return False, None, None, None

        return True, date_str, type_str, duration

    def _add_workout(self):
        valid, date_str, type_str, duration = self._validate_input()
        if not valid:
            return

        new_workout = {"date": date_str, "type": type_str, "duration": duration}
        self.workouts.append(new_workout)
        self._refresh_table(self.workouts)
        messagebox.showinfo("Успех", "Тренировка успешно добавлена!")

        self.entry_date.delete(0, tk.END)
        self.entry_duration.delete(0, tk.END)

    def _apply_filter(self):
        filter_type = self.combo_filter_type.get()
        filter_date = self.entry_filter_date.get().strip()

        filtered = self.workouts[:]
        if filter_type != "Все":
            filtered = [w for w in filtered if w["type"] == filter_type]
        if filter_date:
            try:
                datetime.strptime(filter_date, "%Y-%m-%d")
                filtered = [w for w in filtered if w["date"] == filter_date]
            except ValueError:
                messagebox.showwarning("Предупреждение", "Дата фильтра должна быть в формате ГГГГ-ММ-ДД")
                return

        self._refresh_table(filtered)

    def _reset_filter(self):
        self.combo_filter_type.current(0)
        self.entry_filter_date.delete(0, tk.END)
        self._refresh_table(self.workouts)

    def _refresh_table(self, data):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for w in data:
            self.tree.insert("", tk.END, values=(w["date"], w["type"], w["duration"]))

    def _save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.workouts, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранение", "Данные успешно сохранены в JSON.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные:\n{e}")

    def _load_data(self):
        if not os.path.exists(self.data_file):
            self.workouts = []
            self._refresh_table([])
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.workouts = json.load(f)
            self._refresh_table(self.workouts)
            messagebox.showinfo("Загрузка", "Данные успешно загружены.")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Файл JSON поврежден или имеет неверный формат.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlannerApp(root)
    root.mainloop()
