import copy
import datetime
import json
import os


class TableData:

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.current_filename = "Бележки 1.json"
        self.columns = []
        self.rows = []
        self.last_saved_time = ""

        self.load_table("Бележки 1")

    def save_data(self):
        filepath = os.path.join(self.data_dir, self.current_filename)
        data = {"columns": self.columns, "rows": self.rows}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.last_saved_time = datetime.datetime.now().strftime("%H:%M:%S")

    def load_table(self, table_name):
        self.current_filename = f"{table_name}.json"
        filepath = os.path.join(self.data_dir, self.current_filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.columns = data.get(
                    "columns", ["Заглавие", "Количество", "Бележка"]
                )
                self.rows = data.get("rows", [])
        else:
            self.columns = ["Заглавие", "Количество", "Бележка"]
            self.rows = []
            self.save_data()

        self.last_saved_time = datetime.datetime.now().strftime("%H:%M:%S")

    def list_tables(self):
        files = [
            f[:-5] for f in os.listdir(self.data_dir) if f.endswith(".json")
        ]
        if not files:
            files = ["Бележки 1"]
        return files

    def create_new_table(self, table_name):
        self.load_table(table_name)

    def duplicate_table(self, new_table_name):
        copied_columns = copy.deepcopy(self.columns)
        copied_rows = copy.deepcopy(self.rows)

        self.current_filename = f"{new_table_name}.json"
        self.columns = copied_columns
        self.rows = copied_rows
        self.save_data()

    def delete_current_table(self):
        filepath = os.path.join(self.data_dir, self.current_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        remaining = self.list_tables()
        self.load_table(remaining[0])

    def add_row(self):
        new_row = [
            {"value": "", "bold": False, "color": "default"}
            for _ in self.columns
        ]
        self.rows.append(new_row)
        self.save_data()

    def duplicate_row(self, row_idx):
        if 0 <= row_idx < len(self.rows):
            copied_row = copy.deepcopy(self.rows[row_idx])
            self.rows.insert(row_idx + 1, copied_row)
            self.save_data()

    def delete_row(self, row_idx):
        if 0 <= row_idx < len(self.rows):
            self.rows.pop(row_idx)
            self.save_data()

    def move_row(self, row_idx, direction):
        new_idx = row_idx + direction
        if 0 <= new_idx < len(self.rows):
            self.rows[row_idx], self.rows[new_idx] = (
                self.rows[new_idx],
                self.rows[row_idx],
            )
            self.save_data()

    def add_column(self, col_name):
        self.columns.append(col_name)
        for row in self.rows:
            row.append({"value": "", "bold": False, "color": "default"})
        self.save_data()

    def rename_column(self, col_idx, new_name):
        if 0 <= col_idx < len(self.columns):
            self.columns[col_idx] = new_name
            self.save_data()

    def move_column(self, col_idx, direction):
        """
        direction: -1 за наляво, 1 за надясно
        """
        new_idx = col_idx + direction
        if 0 <= new_idx < len(self.columns):
            # Размяна в имената на колоните
            self.columns[col_idx], self.columns[new_idx] = (
                self.columns[new_idx],
                self.columns[col_idx],
            )

            # Размяна на клетките за всяка редица
            for row in self.rows:
                if col_idx < len(row) and new_idx < len(row):
                    row[col_idx], row[new_idx] = row[new_idx], row[col_idx]

            self.save_data()

    def delete_column(self, col_idx):
        if 0 <= col_idx < len(self.columns):
            self.columns.pop(col_idx)
            for row in self.rows:
                if col_idx < len(row):
                    row.pop(col_idx)
            self.save_data()

    def sort_rows_by_column(self, col_idx, reverse=False):
        if 0 <= col_idx < len(self.columns):
            self.rows.sort(
                key=lambda r: (
                    r[col_idx]["value"].strip().lower()
                    if col_idx < len(r)
                    else ""
                ),
                reverse=reverse,
            )
            self.save_data()

    def update_cell_value(self, row_idx, col_idx, value):
        if 0 <= row_idx < len(self.rows) and 0 <= col_idx < len(self.columns):
            self.rows[row_idx][col_idx]["value"] = value
            self.save_data()

    def toggle_cell_bold(self, row_idx, col_idx):
        if 0 <= row_idx < len(self.rows) and 0 <= col_idx < len(self.columns):
            current = self.rows[row_idx][col_idx].get("bold", False)
            self.rows[row_idx][col_idx]["bold"] = not current
            self.save_data()

    def set_cell_color(self, row_idx, col_idx, color):
        if 0 <= row_idx < len(self.rows) and 0 <= col_idx < len(self.columns):
            self.rows[row_idx][col_idx]["color"] = color
            self.save_data()