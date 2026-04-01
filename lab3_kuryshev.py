import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from lab3_model import (
    FileManager,
    Nedvizhimost,
    PropertyModel,
    StorageError,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("property_app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AddPropertyDialog:

    def __init__(self, parent: tk.Tk) -> None:
        self.result: Optional[Nedvizhimost] = None
        self._window = tk.Toplevel(parent)
        self._window.title("Добавить объект")
        self._window.geometry("400x200")
        self._window.resizable(False, False)
        self._window.grab_set()
        self._setup_widgets()

    def _setup_widgets(self) -> None:
        frame = tk.Frame(self._window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        labels = ("Владелец:", "Дата:", "Стоимость:")
        self._owner_var = tk.StringVar()
        self._date_var = tk.StringVar()
        self._cost_var = tk.StringVar()
        variables = (self._owner_var, self._date_var, self._cost_var)

        for row, (text, var) in enumerate(zip(labels, variables)):
            tk.Label(frame, text=text).grid(row=row, column=0, sticky=tk.W, pady=5)
            tk.Entry(frame, textvariable=var, width=30).grid(row=row, column=1, pady=5)

        btn_frame = tk.Frame(self._window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="OK", command=self._on_ok,
                  bg="#4CAF50", fg="white", padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=self._window.destroy,
                  bg="#757575", fg="white", padx=20).pack(side=tk.LEFT, padx=5)

    def _on_ok(self) -> None:
        owner = self._owner_var.get().strip()
        date = self._date_var.get().strip()
        cost_str = self._cost_var.get().strip()

        if not owner:
            messagebox.showerror("Ошибка", "Имя владельца не может быть пустым.", parent=self._window)
            return
        if not date:
            messagebox.showerror("Ошибка", "Дата не может быть пустой.", parent=self._window)
            return
        try:
            cost = int(cost_str)
        except ValueError:
            messagebox.showerror("Ошибка", f"Стоимость должна быть целым числом, получено: {cost_str!r}",
                                 parent=self._window)
            return
        if cost < 0:
            messagebox.showerror("Ошибка", "Стоимость не может быть отрицательной.", parent=self._window)
            return

        self.result = Nedvizhimost(owner=owner, date=date, cost=cost)
        self._window.destroy()

    @property
    def window(self) -> tk.Toplevel:
        return self._window


class PropertyGUI:

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._root.title("Недвижимость")
        self._root.geometry("700x500")
        self._model = PropertyModel()
        self._current_file: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self._setup_menu()
        self._setup_title()
        self._setup_table()
        self._setup_buttons()

    def _setup_menu(self) -> None:
        menubar = tk.Menu(self._root)
        self._root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть", command=self._open_file)
        file_menu.add_command(label="Сохранить", command=self._save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self._root.quit)

    def _setup_title(self) -> None:
        frame = tk.Frame(self._root)
        frame.pack(pady=10)
        tk.Label(frame, text="Список объектов недвижимости",
                 font=("Arial", 14, "bold")).pack()

    def _setup_table(self) -> None:
        table_frame = tk.Frame(self._root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._tree = ttk.Treeview(
            table_frame,
            columns=("Владелец", "Дата", "Стоимость"),
            height=15,
            yscrollcommand=scrollbar.set,
            show="headings",
        )
        scrollbar.config(command=self._tree.yview)

        self._tree.column("Владелец", anchor=tk.W, width=250)
        self._tree.column("Дата", anchor=tk.CENTER, width=100)
        self._tree.column("Стоимость", anchor=tk.E, width=150)

        self._tree.heading("Владелец", text="Владелец")
        self._tree.heading("Дата", text="Дата")
        self._tree.heading("Стоимость", text="Стоимость (руб.)")
        self._tree.pack(fill=tk.BOTH, expand=True)

    def _setup_buttons(self) -> None:
        frame = tk.Frame(self._root)
        frame.pack(pady=10)
        tk.Button(frame, text="Добавить", command=self._add_property,
                  bg="#4CAF50", fg="white", padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Удалить", command=self._delete_property,
                  bg="#f44336", fg="white", padx=10, pady=5).pack(side=tk.LEFT, padx=5)

    def _open_file(self) -> None:
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            lines = FileManager.read_lines(file_path)
        except StorageError as exc:
            messagebox.showerror("Ошибка", str(exc))
            return

        errors = self._model.load_from_lines(lines)
        self._current_file = file_path
        self._refresh_table()

        summary = f"Загружено объектов: {self._model.count()}"
        if errors:
            summary += f"\n\nПропущено строк: {len(errors)}\n" + "\n".join(errors)
            messagebox.showwarning("Загрузка завершена с предупреждениями", summary)
        else:
            messagebox.showinfo("Загрузка завершена", summary)

    def _save_file(self) -> None:
        if not self._current_file:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            )
            if not file_path:
                return
            self._current_file = file_path
        try:
            FileManager.save_properties(self._current_file, self._model.properties)
            messagebox.showinfo("Сохранено", f"Файл сохранён: {self._current_file}")
        except StorageError as exc:
            messagebox.showerror("Ошибка сохранения", str(exc))

    def _add_property(self) -> None:
        dialog = AddPropertyDialog(self._root)
        self._root.wait_window(dialog.window)
        if dialog.result is not None:
            self._model.add(dialog.result)
            self._refresh_table()

    def _delete_property(self) -> None:
        selected = self._tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите объект для удаления.")
            return
        if not messagebox.askyesno("Подтверждение", "Удалить выбранный объект?"):
            return

        index = self._tree.index(selected[0])
        try:
            self._model.remove_at(index)
        except IndexError as exc:
            messagebox.showerror("Ошибка", str(exc))
            return
        self._refresh_table()

    def _refresh_table(self) -> None:
        """Clears and repopulates the Treeview from the model."""
        for item in self._tree.get_children():
            self._tree.delete(item)
        for prop in self._model.properties:
            cost_formatted = f"{prop.cost:,}".replace(",", "\u00a0")
            self._tree.insert("", tk.END, values=(prop.owner, prop.date, cost_formatted))

def main() -> None:
    root = tk.Tk()
    PropertyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()