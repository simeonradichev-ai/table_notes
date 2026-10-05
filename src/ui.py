import flet as ft
from src.data import TableData


def build_app(page: ft.Page):
    page.title = "Namari'e таблици"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    db = TableData()

    # Индикатор за статус на запазване
    save_status_text = ft.Row(
        [
            ft.Icon(
                ft.Icons.CHECK_CIRCLE_OUTLINE,
                color=ft.Colors.GREEN_400,
                size=16,
            ),
            ft.Text(
                f"Запазено в {db.last_saved_time}",
                size=12,
                color=ft.Colors.GREEN_400,
            ),
        ],
        spacing=4,
    )

    def update_save_status():
        save_status_text.controls[1].value = f"Запазено в {db.last_saved_time}"

    # Смяна на Тъмна / Светла тема
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_btn.icon = ft.Icons.WB_SUNNY_OUTLINED
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_btn.icon = ft.Icons.NIGHTLIGHT_ROUND
        refresh_table()

    theme_btn = ft.IconButton(
        icon=ft.Icons.NIGHTLIGHT_ROUND,
        tooltip="Смени темата (Light/Dark)",
        on_click=toggle_theme,
    )

    # Падащо меню с налични таблици
    tables_dropdown = ft.Dropdown(
        width=200,
        dense=True,
        options=[ft.dropdown.Option(t) for t in db.list_tables()],
        value=db.current_filename[:-5],
        on_select=lambda e: change_table(e.control.value),
    )

    def update_dropdown_options():
        tables_dropdown.options = [
            ft.dropdown.Option(t) for t in db.list_tables()
        ]
        tables_dropdown.value = db.current_filename[:-5]

    def change_table(table_name):
        if table_name:
            db.load_table(table_name)
            search_field.value = ""
            refresh_table()

    # Диалог за нова таблица
    def open_new_table_dialog(e):
        name_field = ft.TextField(
            label="Име на новата таблица", autofocus=True
        )

        def confirm_create(e_dlg):
            val = name_field.value.strip()
            if val:
                db.create_new_table(val)
                update_dropdown_options()
                search_field.value = ""
                refresh_table()
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Нова Таблица"),
            content=name_field,
            actions=[
                ft.Button(
                    "Отказ",
                    on_click=lambda e: setattr(dialog, "open", False)
                    or page.update(),
                ),
                ft.Button("Създай", on_click=confirm_create),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Диалог за дублиране на текущата таблица
    def open_duplicate_table_dialog(e):
        curr_name = db.current_filename[:-5]
        name_field = ft.TextField(
            value=f"{curr_name} (копие)", label="Име на копието", autofocus=True
        )

        def confirm_duplicate(e_dlg):
            val = name_field.value.strip()
            if val:
                db.duplicate_table(val)
                update_dropdown_options()
                search_field.value = ""
                refresh_table()
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Дублиране на таблицата"),
            content=name_field,
            actions=[
                ft.Button(
                    "Отказ",
                    on_click=lambda e: setattr(dialog, "open", False)
                    or page.update(),
                ),
                ft.Button("Дублирай", on_click=confirm_duplicate),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Изтриване на текущата таблица
    def open_delete_table_dialog(e):
        def confirm_delete(e_dlg):
            db.delete_current_table()
            update_dropdown_options()
            search_field.value = ""
            refresh_table()
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Изтриване на файл"),
            content=ft.Text(
                f"Сигурни ли сте, че искате да изтриете '{db.current_filename[:-5]}'?"
            ),
            actions=[
                ft.Button(
                    "Отказ",
                    on_click=lambda e: setattr(dialog, "open", False)
                    or page.update(),
                ),
                ft.Button(
                    "Изтрий файла",
                    color=ft.Colors.RED_400,
                    on_click=confirm_delete,
                ),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Диалог за настройки на колона (Включва преместване наляво/надясно)
    def open_column_dialog(col_idx, current_name):
        rename_field = ft.TextField(value=current_name, autofocus=True)

        def save_col_rename(e):
            new_name = rename_field.value.strip()
            if new_name:
                db.rename_column(col_idx, new_name)
                refresh_table()
            dialog.open = False
            page.update()

        def move_col(direction):
            db.move_column(col_idx, direction)
            refresh_table()
            dialog.open = False
            page.update()

        def sort_col(reverse=False):
            db.sort_rows_by_column(col_idx, reverse=reverse)
            refresh_table()
            dialog.open = False
            page.update()

        def confirm_delete_col(e):
            db.delete_column(col_idx)
            refresh_table()
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Настройки за '{current_name}'"),
            content=ft.Column(
                [
                    ft.Text("Име на колоната:"),
                    rename_field,
                    ft.Divider(),
                    ft.Text("Преместване на колоната:"),
                    ft.Row(
                        [
                            ft.Button(
                                "← Наляво",
                                icon=ft.Icons.ARROW_BACK,
                                disabled=(col_idx == 0),
                                on_click=lambda e: move_col(-1),
                            ),
                            ft.Button(
                                "Надясно →",
                                icon=ft.Icons.ARROW_FORWARD,
                                disabled=(col_idx == len(db.columns) - 1),
                                on_click=lambda e: move_col(1),
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Divider(),
                    ft.Text("Сортиране на редовете:"),
                    ft.Row(
                        [
                            ft.Button(
                                "А - Я (Възходящо)",
                                icon=ft.Icons.ARROW_DOWNWARD,
                                on_click=lambda e: sort_col(False),
                            ),
                            ft.Button(
                                "Я - А (Низходящо)",
                                icon=ft.Icons.ARROW_UPWARD,
                                on_click=lambda e: sort_col(True),
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                height=260,
                tight=True,
            ),
            actions=[
                ft.Button(
                    "Изтрий колоната",
                    color=ft.Colors.RED_400,
                    on_click=confirm_delete_col,
                ),
                ft.Button(
                    "Отказ",
                    on_click=lambda e: setattr(dialog, "open", False)
                    or page.update(),
                ),
                ft.Button("Запази", on_click=save_col_rename),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Поле за търсене
    search_field = ft.TextField(
        hint_text="Търсене в таблицата...",
        prefix_icon=ft.Icons.SEARCH,
        width=220,
        dense=True,
        on_change=lambda e: refresh_table(),
    )

    def on_cell_change(row_idx, col_idx, val):
        db.update_cell_value(row_idx, col_idx, val)
        update_save_status()
        save_status_text.update()

    def build_table():
        line_color = (
            ft.Colors.WHITE
            if page.theme_mode == ft.ThemeMode.DARK
            else ft.Colors.GREY_400
        )

        header_columns = []
        for c_idx, col in enumerate(db.columns):
            header_btn = ft.Button(
                content=ft.Text(col, weight=ft.FontWeight.BOLD, size=15),
                style=ft.ButtonStyle(padding=5),
                on_click=lambda e, idx=c_idx, name=col: open_column_dialog(
                    idx, name
                ),
            )
            header_columns.append(ft.DataColumn(header_btn))

        header_columns.append(ft.DataColumn(ft.Text("Действия", width=150)))

        query = search_field.value.strip().lower() if search_field.value else ""

        table_rows = []
        for row_idx, row in enumerate(db.rows):
            if query:
                row_text = " ".join(
                    [cell.get("value", "").lower() for cell in row]
                )
                if query not in row_text:
                    continue

            cells = []
            for col_idx, cell_data in enumerate(row):
                val = cell_data.get("value", "")
                is_bold = cell_data.get("bold", False)
                color = cell_data.get("color", "default")

                text_color = None
                if color == "default" or color == "black":
                    text_color = (
                        ft.Colors.WHITE
                        if page.theme_mode == ft.ThemeMode.DARK
                        else ft.Colors.BLACK
                    )
                elif color == "red":
                    text_color = (
                        ft.Colors.RED_400
                        if page.theme_mode == ft.ThemeMode.DARK
                        else ft.Colors.RED_700
                    )
                elif color == "green":
                    text_color = (
                        ft.Colors.GREEN_400
                        if page.theme_mode == ft.ThemeMode.DARK
                        else ft.Colors.GREEN_700
                    )
                elif color == "blue":
                    text_color = (
                        ft.Colors.BLUE_400
                        if page.theme_mode == ft.ThemeMode.DARK
                        else ft.Colors.BLUE_700
                    )

                field = ft.TextField(
                    value=val,
                    border=ft.InputBorder.NONE,
                    dense=True,
                    multiline=True,
                    min_lines=2,
                    max_lines=3,
                    text_style=ft.TextStyle(
                        weight=(
                            ft.FontWeight.BOLD
                            if is_bold
                            else ft.FontWeight.NORMAL
                        ),
                        color=text_color,
                    ),
                    on_change=lambda e, r=row_idx, c=col_idx: on_cell_change(
                        r, c, e.control.value
                    ),
                )

                bold_btn = ft.IconButton(
                    icon=ft.Icons.FORMAT_BOLD,
                    icon_size=16,
                    selected=is_bold,
                    tooltip="Одебели текста",
                    on_click=lambda e, r=row_idx, c=col_idx: [
                        db.toggle_cell_bold(r, c),
                        refresh_table(),
                    ],
                )

                def set_color(r, c, new_color):
                    db.set_cell_color(r, c, new_color)
                    refresh_table()

                color_menu = ft.PopupMenuButton(
                    icon=ft.Icons.COLOR_LENS_OUTLINED,
                    icon_size=16,
                    tooltip="Изберете цвят на текста",
                    items=[
                        ft.PopupMenuItem(
                            content=ft.Text("Основен цвят"),
                            on_click=lambda e,
                            r=row_idx,
                            c=col_idx: set_color(r, c, "default"),
                        ),
                        ft.PopupMenuItem(
                            content=ft.Text("Червен", color=ft.Colors.RED),
                            on_click=lambda e,
                            r=row_idx,
                            c=col_idx: set_color(r, c, "red"),
                        ),
                        ft.PopupMenuItem(
                            content=ft.Text("Зелен", color=ft.Colors.GREEN),
                            on_click=lambda e,
                            r=row_idx,
                            c=col_idx: set_color(r, c, "green"),
                        ),
                        ft.PopupMenuItem(
                            content=ft.Text("Син", color=ft.Colors.BLUE),
                            on_click=lambda e,
                            r=row_idx,
                            c=col_idx: set_color(r, c, "blue"),
                        ),
                    ],
                )

                cell_content = ft.Container(
                    width=280,
                    padding=5,
                    content=ft.Column(
                        [
                            field,
                            ft.Row(
                                [bold_btn, color_menu],
                                alignment=ft.MainAxisAlignment.END,
                                spacing=0,
                            ),
                        ],
                        spacing=2,
                    ),
                )

                cells.append(ft.DataCell(cell_content))

            # Действия за ред: Нагоре, Надолу, Дублирай, Изтрий
            btn_move_up = ft.IconButton(
                icon=ft.Icons.KEYBOARD_ARROW_UP,
                icon_size=18,
                tooltip="Премести реда нагоре",
                on_click=lambda e, r=row_idx: [
                    db.move_row(r, -1),
                    refresh_table(),
                ],
            )
            btn_move_down = ft.IconButton(
                icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                icon_size=18,
                tooltip="Премести реда надолу",
                on_click=lambda e, r=row_idx: [
                    db.move_row(r, 1),
                    refresh_table(),
                ],
            )
            btn_duplicate = ft.IconButton(
                icon=ft.Icons.COPY_ALL_OUTLINED,
                icon_size=18,
                tooltip="Дублирай този ред",
                on_click=lambda e, r=row_idx: [
                    db.duplicate_row(r),
                    refresh_table(),
                ],
            )
            delete_btn = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINED,
                icon_size=18,
                icon_color=ft.Colors.RED_400,
                tooltip="Изтрий ред",
                on_click=lambda e, r=row_idx: delete_row(r),
            )

            actions_cell = ft.Row(
                [btn_move_up, btn_move_down, btn_duplicate, delete_btn],
                spacing=0,
            )
            cells.append(ft.DataCell(actions_cell))

            table_rows.append(ft.DataRow(cells=cells))

        dt = ft.DataTable(
            data_row_min_height=90,
            data_row_max_height=130,
            columns=header_columns,
            rows=table_rows,
            border=ft.Border.all(1, line_color),
            vertical_lines=ft.BorderSide(1, line_color),
            horizontal_lines=ft.BorderSide(1, line_color),
            divider_thickness=1,
        )

        return ft.Column(
            controls=[ft.Row([dt], scroll=ft.ScrollMode.ALWAYS)],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
        )

    def add_row_click(e):
        db.add_row()
        refresh_table()

    def add_col_click(e):
        col_name_field = ft.TextField(
            label="Име на новата колона", autofocus=True
        )

        def confirm_col(e_dlg):
            col_name = col_name_field.value.strip()
            if col_name:
                db.add_column(col_name)
                refresh_table()
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Нова Колона"),
            content=col_name_field,
            actions=[
                ft.Button(
                    "Отказ",
                    on_click=lambda e: setattr(dialog, "open", False)
                    or page.update(),
                ),
                ft.Button("Добави", on_click=confirm_col),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def delete_row(row_idx):
        db.delete_row(row_idx)
        refresh_table()

    def refresh_table():
        update_save_status()
        table_container.content = build_table()
        page.update()

    table_container = ft.Container(content=build_table(), expand=True)

    page.add(
        ft.Row(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Таблици:", size=18, weight=ft.FontWeight.BOLD
                        ),
                        tables_dropdown,
                        ft.IconButton(
                            icon=ft.Icons.COPY_OUTLINED,
                            tooltip="Дублирай тази таблица",
                            on_click=open_duplicate_table_dialog,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            tooltip="Изтрий тази таблица",
                            on_click=open_delete_table_dialog,
                        ),
                        theme_btn,
                        save_status_text,
                    ]
                ),
                ft.Row(
                    [
                        search_field,
                        ft.Button(
                            "+ Нова Таблица", on_click=open_new_table_dialog
                        ),
                        ft.Button("+ Колона", on_click=add_col_click),
                        ft.Button("+ Нов ред", on_click=add_row_click),
                    ]
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        ft.Divider(),
        table_container,
    )