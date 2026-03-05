import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Nedvizhimost:
  owner: str
  date: str
  cost: int


class PropertyParser:
  @staticmethod
  def parse(line: str) -> Nedvizhimost:
    start = line.find('"')
    end = line.find('"', start + 1)
    
    owner = line[start + 1:end]
    parts = line[end + 1:].split()
    date = parts[0]
    cost = int(parts[1])
  
    return Nedvizhimost(owner, date, cost)

class FileManager:
  @staticmethod
  def load_properties(file_path: str) -> List[Nedvizhimost]:
    properties = []
    try:
      with open(file_path, 'r', encoding='utf-8') as f:
        for num, line in enumerate(f, 1):
          line = line.strip()
          if line:
            try:
              properties.append(PropertyParser.parse(line))
            except ValueError as e:
              raise ValueError(f"Строка {num}: {str(e)}")
    except FileNotFoundError:
      raise FileNotFoundError(f"Файл не найден: {file_path}")
    return properties

  @staticmethod
  def save_properties(file_path: str, props: List[Nedvizhimost]) -> None:
    with open(file_path, 'w', encoding='utf-8') as f:
      for p in props:
        f.write(f'"{p.owner}" {p.date} {p.cost}\n')


class AddPropertyDialog:
  def __init__(self, parent: tk.Tk):
    self.window = tk.Toplevel(parent)
    self.window.title("Добавить объект")
    self.window.geometry("400x200")
    self.window.resizable(False, False)
    self.result = None
    self._setup()

  def _setup(self) -> None:
    frame = tk.Frame(self.window, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    tk.Label(frame, text="Владелец:").grid(row=0, column=0, sticky=tk.W, pady=5)
    self.owner_var = tk.StringVar()
    tk.Entry(frame, textvariable=self.owner_var, width=30).grid(row=0, column=1, pady=5)
    
    tk.Label(frame, text="Дата:").grid(row=1, column=0, sticky=tk.W, pady=5)
    self.date_var = tk.StringVar()
    tk.Entry(frame, textvariable=self.date_var, width=30).grid(row=1, column=1, pady=5)
    
    tk.Label(frame, text="Стоимость:").grid(row=2, column=0, sticky=tk.W, pady=5)
    self.cost_var = tk.StringVar()
    tk.Entry(frame, textvariable=self.cost_var, width=30).grid(row=2, column=1, pady=5)
    
    button_frame = tk.Frame(self.window)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="OK", command=self._ok,
              bg="#4CAF50", fg="white", padx=20).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Отмена", command=self.window.destroy,
              bg="#757575", fg="white", padx=20).pack(side=tk.LEFT, padx=5)

  def _ok(self) -> None:
    owner = self.owner_var.get().strip()
    date = self.date_var.get().strip()
    cost = self.cost_var.get().strip()
    int(cost)
    self.result = {'owner': owner, 'date': date, 'cost': cost}
    self.window.destroy()

class PropertyGUI:
  def __init__(self, root: tk.Tk):
    self.root = root
    self.root.title("Недвижимость")
    self.root.geometry("700x500")
    self.properties: List[Nedvizhimost] = []
    self.current_file: Optional[str] = None
    self._setup_ui()

  def _setup_ui(self) -> None:
    menubar = tk.Menu(self.root)
    self.root.config(menu=menubar)
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Файл", menu=file_menu)
    file_menu.add_command(label="Открыть", command=self._open_file)
    file_menu.add_command(label="Сохранить", command=self._save_file)
    file_menu.add_separator()
    file_menu.add_command(label="Выход", command=self.root.quit)
    
    title_frame = tk.Frame(self.root)
    title_frame.pack(pady=10)
    tk.Label(title_frame, text="Список объектов недвижимости",
             font=("Arial", 14, "bold")).pack()
    
    table_frame = tk.Frame(self.root)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    scrollbar = ttk.Scrollbar(table_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    self.tree = ttk.Treeview(table_frame,
                             columns=("Владелец", "Дата", "Стоимость"),
                             height=15, yscrollcommand=scrollbar.set)
    scrollbar.config(command=self.tree.yview)
    
    self.tree.column("#0", width=0, stretch=tk.NO)
    self.tree.column("Владелец", anchor=tk.W, width=250)
    self.tree.column("Дата", anchor=tk.CENTER, width=100)
    self.tree.column("Стоимость", anchor=tk.E, width=150)
    
    self.tree.heading("Владелец", text="Владелец", anchor=tk.W)
    self.tree.heading("Дата", text="Дата", anchor=tk.CENTER)
    self.tree.heading("Стоимость", text="Стоимость (руб.)", anchor=tk.E)
    self.tree.pack(fill=tk.BOTH, expand=True)
    
    button_frame = tk.Frame(self.root)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Добавить", command=self._add_property,
              bg="#4CAF50", fg="white", padx=10, pady=5).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Удалить", command=self._delete_property,
              bg="#f44336", fg="white", padx=10, pady=5).pack(side=tk.LEFT, padx=5)

  def _open_file(self) -> None:
    file_path = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not file_path:
      return
    try:
      self.properties = FileManager.load_properties(file_path)
      self.current_file = file_path
      self._refresh_table()
      messagebox.showinfo("Загружено", f"Загружено {len(self.properties)} объектов")
    except (FileNotFoundError, ValueError) as e:
      messagebox.showerror(f"Ошибка при загрузке:\n{str(e)}")

  def _save_file(self) -> None:
    if not self.current_file:
      file_path = filedialog.asksaveasfilename(
          defaultextension=".txt",
          filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
      )
      if not file_path:
        return
      self.current_file = file_path
    try:
      FileManager.save_properties(self.current_file, self.properties)
      messagebox.showinfo("file save", "file saved")
    except Exception as e:
      messagebox.showerror(f"Ошибка при сохранении:\n{str(e)}")

  def _add_property(self) -> None:
    dialog = AddPropertyDialog(self.root)
    self.root.wait_window(dialog.window)
    if dialog.result:
      try:
        prop = Nedvizhimost(
            owner=dialog.result['owner'],
            date=dialog.result['date'],
            cost=int(dialog.result['cost'])
        )
        self.properties.append(prop)
        self._refresh_table()
      except ValueError as e:
        messagebox.showerror("Ошибка", f"Ошибка:\n{str(e)}")

  def _delete_property(self) -> None:
    selected = self.tree.selection()
    if not selected:
      messagebox.showwarning("Предупреждение", "Выберите объект для удаления")
      return
    if messagebox.askyesno("Подтверждение", "Удалить выбранный объект?"):
      index = self.tree.index(selected[0])
      self.properties.pop(index)
      self._refresh_table()

  def _refresh_table(self) -> None:
    for item in self.tree.get_children():
      self.tree.delete(item)
    for prop in self.properties:
      cost_str = f"{prop.cost:,}".replace(",", " ")
      self.tree.insert("", tk.END, values=(prop.owner, prop.date, cost_str))

def main() -> None:
  root = tk.Tk()
  PropertyGUI(root)
  root.mainloop()


if __name__ == "__main__":
  main()