import flet as ft
from src.data import TableData


def build_app(page: ft.Page):
    page.title = "Namari'e таблици"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10
    page.spacing = 10
    page.scroll = ft.ScrollMode.AUTO

    db = TableData()

    # Статус за запазване
    save_status_text = ft.Text(
        f"Запазено в {db.last_saved_time}",
        size=11,
        color=ft.Colors.GREEN_400,
    )

    def update_save_status():
        save_status_text.value = f"Запазено в {db.last_saved_time}"

    # Смяна на тема
    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        theme_btn.icon = (
            ft.Icons.WB_SUNNY
            if page.theme_mode == ft.ThemeMode.DARK
            else ft.Icons.NIGHTLIGHT_ROUND
        )
        refresh_table()

    theme_btn = ft.IconButton(
        icon=ft.Icons.NIGHTLIGHT_ROUND,
        tooltip="Смени темата",
        on_click=toggle_theme,
    )

    # Меню с таблици
    tables_dropdown = ft.Dropdown(
        expand=True,
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

    # Диалог: Нова таблица
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
                ft.TextButton(
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

    # Диалог: Дублиране
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
            title=ft.Text("Дублиране на таблица"),
            content=name_field,
            actions=[
                ft.TextButton(
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

    # Диалог: Изтриване
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
                ft.TextButton(
                    "Отказ",
                    on_click=lambda e: setattr(dialog, "open", False)
                    or page.update(),
                ),
                ft.Button(
                    "Изтрий",
                    color=ft.Colors.RED_400,
                    on_click=confirm_delete,
                ),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Диалог: Настройки на колона
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
            title=ft.Text(f"Настройки: '{current_name}'"),
            content=ft.Column(
                [
                    ft.Text("Име:"),
                    rename_field,
                    ft.Divider(),
                    ft.Row(
                        [
                            ft.Button(
                                "← Наляво",
                                disabled=(col_idx == 0),
                                on_click=lambda e: move_col(-1),
                            ),
                            ft.Button(
                                "Надясно →",
                                disabled=(col_idx == len(db.columns) - 1),
                                on_click=lambda e: move_col(1),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(),
                    ft.Row(
                        [
                            ft.Button(
                                "Сортирай А-Я",
                                on_click=lambda e: sort_col(False),
                            ),
                            ft.Button(
                                "Сортирай Я-А",
                                on_click=lambda e: sort_col(True),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                height=250,
                tight=True,
            ),
            actions=[
                ft.Button(
                    "Изтрий колоната",
                    color=ft.Colors.RED_400,
                    on_click=confirm_delete_col,
                ),
                ft.TextButton(
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

    search_field = ft.TextField(
        hint_text="Търсене в таблицата...",
        prefix_icon=ft.Icons.SEARCH,
        dense=True,
        expand=True,
        on_change=lambda e: refresh_table(),
    )

    def on_cell_change(row_idx, col_idx, val):
        db.update_cell_value(row_idx, col_idx, val)
        update_save_status()
        save_status_text.update()

    def delete_row(row_idx):
        db.delete_row(row_idx)
        refresh_table()

    # Сглобяване на мобилните карти за редовете
    def build_cards_view():
        query = search_field.value.strip().lower() if search_field.value else ""
        cards = []

        for row_idx, row in enumerate(db.rows):
            if query:
                row_text = " ".join(
                    [cell.get("value", "").lower() for cell in row]
                )
                if query not in row_text:
                    continue

            fields_list = []
            for col_idx, cell_data in enumerate(row):
                col_name = (
                    db.columns[col_idx]
                    if col_idx < len(db.columns)
                    else f"Колона {col_idx+1}"
                )
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
                    label=col_name,
                    multiline=True,
                    min_lines=1,
                    max_lines=3,
                    dense=True,
                    expand=True,
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
                    icon_size=20,
                    selected=is_bold,
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
                    icon_size=20,
                    items=[
                        ft.PopupMenuItem(
                            content=ft.Text("Основен"),
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

                fields_list.append(
                    ft.Row(
                        [field, bold_btn, color_menu],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=0,
                    )
                )

            row_actions = ft.Row(
                [
                    ft.Text(
                        f"Ред #{row_idx + 1}",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.KEYBOARD_ARROW_UP,
                                tooltip="Нагоре",
                                icon_size=20,
                                on_click=lambda e, r=row_idx: [
                                    db.move_row(r, -1),
                                    refresh_table(),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                                tooltip="Надолу",
                                icon_size=20,
                                on_click=lambda e, r=row_idx: [
                                    db.move_row(r, 1),
                                    refresh_table(),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.COPY_ALL_OUTLINED,
                                tooltip="Дублирай ред",
                                icon_size=20,
                                on_click=lambda e, r=row_idx: [
                                    db.duplicate_row(r),
                                    refresh_table(),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINED,
                                tooltip="Изтрий ред",
                                icon_size=20,
                                icon_color=ft.Colors.RED_400,
                                on_click=lambda e, r=row_idx: delete_row(r),
                            ),
                        ],
                        spacing=0,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

            card_content = ft.Card(
                content=ft.Container(
                    padding=10,
                    content=ft.Column(
                        [
                            row_actions,
                            ft.Divider(height=1, thickness=1),
                            *fields_list,
                        ],
                        spacing=8,
                    ),
                ),
                elevation=2,
            )
            cards.append(card_content)

        if not cards:
            return ft.Container(
                content=ft.Text("Няма намерени данни", color=ft.Colors.GREY_500),
                alignment=ft.alignment.center,
                padding=20,
            )

        return ft.Column(controls=cards, spacing=10)

    # Лента за управление на колоните
    def build_columns_bar():
        col_buttons = []
        for c_idx, col_name in enumerate(db.columns):
            btn = ft.OutlinedButton(
                content=ft.Text(col_name, size=11, weight=ft.FontWeight.BOLD),
                on_click=lambda e, idx=c_idx, name=col_name: open_column_dialog(
                    idx, name
                ),
            )
            col_buttons.append(btn)

        add_col_btn = ft.IconButton(
            icon=ft.Icons.ADD_BOX,
            tooltip="Добави колона",
            on_click=lambda e: add_col_click(e),
        )

        return ft.Column(
            [
                ft.Text("Управление на колони:", size=11, color=ft.Colors.GREY_600),
                ft.Row(
                    [*col_buttons, add_col_btn],
                    scroll=ft.ScrollMode.AUTO,
                ),
            ],
            spacing=2,
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
                ft.TextButton(
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

    def refresh_table():
        update_save_status()
        table_container.controls = [build_columns_bar(), build_cards_view()]
        page.update()

    table_container = ft.Column(
        controls=[build_columns_bar(), build_cards_view()],
        spacing=10,
    )

    # Защитено от преливане мобилно меню
    top_menu = ft.Column(
        [
            ft.Row(
                [
                    tables_dropdown,
                    ft.IconButton(
                        icon=ft.Icons.NOTE_ADD_OUTLINED,
                        tooltip="Нова таблица",
                        on_click=open_new_table_dialog,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.COPY_OUTLINED,
                        tooltip="Дублирай таблица",
                        on_click=open_duplicate_table_dialog,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip="Изтрий таблица",
                        on_click=open_delete_table_dialog,
                    ),
                    theme_btn,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Row(
                [
                    search_field,
                    ft.Button(
                        "+ Нов Ред",
                        icon=ft.Icons.ADD,
                        on_click=add_row_click,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            save_status_text,
        ],
        spacing=8,
    )

    page.add(
        top_menu,
        ft.Divider(),
        table_container,
    )