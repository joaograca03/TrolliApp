from typing import TYPE_CHECKING
import itertools
import flet as ft
from item import Item
from data_store import DataStore

if TYPE_CHECKING:
    from board import Board

class BoardList(ft.Container):
    id_counter = itertools.count()

    def __init__(
        self,
        board: "Board",
        store: DataStore,
        title: str,
        page: ft.Page,
        color: str = "",
        board_list_id: int = None,
    ):
        self.page: ft.Page = page
        self.board_list_id = board_list_id if board_list_id is not None else next(BoardList.id_counter)
        self.store: DataStore = store
        self.board = board
        self.title = title
        self.color = color
        self.items = ft.Column([], tight=True, spacing=4)

        for item_data in self.store.get_items(self.board_list_id):
            new_item = Item(
                list=self,
                store=self.store,
                item_text=item_data["item_text"],
                priority=item_data["priority"],
                item_id=item_data["id"],
                completed=item_data["completed"]
            )
            self.items.controls.append(
                ft.Column([ft.Container(
                    bgcolor=ft.Colors.BLACK26,
                    border_radius=ft.border_radius.all(30),
                    height=3,
                    alignment=ft.alignment.center_right,
                    width=200,
                    opacity=0.0,
                ), new_item])
            )

        self.new_item_field = ft.TextField(
            label="new card name",
            height=50,
            bgcolor=ft.Colors.WHITE,
            on_submit=self.add_item_handler,
        )

        self.priority_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Baixa"),
                ft.dropdown.Option("Média"),
                ft.dropdown.Option("Alta"),
            ],
            value="Baixa",
            width=150,
        )

        self.priority_filter = ft.Dropdown(
            options=[
                ft.dropdown.Option("Todas"),
                ft.dropdown.Option("Baixa"),
                ft.dropdown.Option("Média"),
                ft.dropdown.Option("Alta"),
            ],
            value="Todas",
            label="Filtrar por Prioridade",
            width=150,
            on_change=self.apply_filters,
        )

        self.status_filter = ft.Dropdown(
            options=[
                ft.dropdown.Option("Todas"),
                ft.dropdown.Option("Concluídas"),
                ft.dropdown.Option("Não Concluídas"),
            ],
            value="Todas",
            label="Filtrar por Estado",
            width=150,
            on_change=self.apply_filters,
        )

        self.end_indicator = ft.Container(
            bgcolor=ft.Colors.BLACK26,
            border_radius=ft.border_radius.all(30),
            height=3,
            width=200,
            opacity=0.0,
        )

        self.edit_field = ft.Row(
            [
                ft.TextField(
                    value=self.title,
                    width=150,
                    height=40,
                    content_padding=ft.padding.only(left=10, bottom=10),
                ),
                ft.TextButton(text="Save", on_click=self.save_title),
            ]
        )

        self.header = ft.Row(
            controls=[
                ft.Text(
                    value=self.title,
                    theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                    text_align=ft.TextAlign.LEFT,
                    overflow=ft.TextOverflow.CLIP,
                    expand=True,
                ),
                ft.Container(
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(
                                content=ft.Text(
                                    value="Edit",
                                    theme_style=ft.TextThemeStyle.LABEL_MEDIUM,
                                    text_align=ft.TextAlign.CENTER,
                                    color=self.color,
                                ),
                                on_click=self.edit_title,
                            ),
                            ft.PopupMenuItem(),
                            ft.PopupMenuItem(
                                content=ft.Text(
                                    value="Delete",
                                    theme_style=ft.TextThemeStyle.LABEL_MEDIUM,
                                    text_align=ft.TextAlign.CENTER,
                                    color=self.color,
                                ),
                                on_click=self.delete_list,
                            ),
                            ft.PopupMenuItem(),
                            ft.PopupMenuItem(
                                content=ft.Text(
                                    value="Move List",
                                    theme_style=ft.TextThemeStyle.LABEL_MEDIUM,
                                    text_align=ft.TextAlign.CENTER,
                                    color=self.color,
                                )
                            ),
                        ],
                    ),
                    padding=ft.padding.only(right=-10),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.filter_column = ft.Column(
            controls=[self.priority_filter, self.status_filter],
            spacing=10,
        )

        self.inner_list = ft.Container(
            content=ft.Column(
                [
                    self.header,
                    self.filter_column,
                    self.new_item_field,
                    self.priority_dropdown,
                    ft.TextButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.ADD),
                                ft.Text("add card", color=ft.Colors.BLACK38),
                            ],
                            tight=True,
                        ),
                        on_click=self.add_item_handler,
                    ),
                    self.items,
                    self.end_indicator,
                ],
                spacing=4,
                tight=True,
                data=self.title,
            ),
            width=250,
            border=ft.border.all(2, ft.Colors.BLACK12),
            border_radius=ft.border_radius.all(5),
            bgcolor=self.color if (self.color != "") else ft.Colors.BACKGROUND,
            padding=ft.padding.only(bottom=10, right=10, left=10, top=5),
        )

        self.view = ft.DragTarget(
            group="items",
            content=ft.Draggable(
                group="lists",
                content=ft.DragTarget(
                    group="lists",
                    content=self.inner_list,
                    data=self,
                    on_accept=self.list_drag_accept,
                    on_will_accept=self.list_will_drag_accept,
                    on_leave=self.list_drag_leave,
                ),
            ),
            data=self,
            on_accept=self.item_drag_accept,
            on_will_accept=self.item_will_drag_accept,
            on_leave=self.item_drag_leave,
        )
        super().__init__(content=self.view, data=self)

    def apply_filters(self, e):
        for item_control in self.items.controls:
            item = item_control.controls[1]
            item_visible = True

            if self.priority_filter.value != "Todas":
                if item.priority != self.priority_filter.value:
                    item_visible = False

            if self.status_filter.value != "Todas":
                is_completed = item.checkbox.value
                if self.status_filter.value == "Concluídas" and not is_completed:
                    item_visible = False
                elif self.status_filter.value == "Não Concluídas" and is_completed:
                    item_visible = False

            item_control.visible = item_visible

        self.page.update()

    def item_drag_accept(self, e):
        src = self.page.get_control(e.src_id)
        self.add_item(
            item_text=src.data.item_text,
            priority=src.data.priority,
            description=src.data.description,
            completed=src.data.completed
        )
        src.data.list.remove_item(src.data)
        self.end_indicator.opacity = 0.0
        self.update()

    def item_will_drag_accept(self, e):
        if e.data == "true":
            self.end_indicator.opacity = 1.0
        self.update()

    def item_drag_leave(self, e):
        self.end_indicator.opacity = 0.0
        self.update()

    def list_drag_accept(self, e):
        src = self.page.get_control(e.src_id)
        l = self.board.content.controls
        to_index = l.index(e.control.data)
        from_index = l.index(src.content.data)
        l[to_index], l[from_index] = l[from_index], l[to_index]
        self.inner_list.border = ft.border.all(2, ft.Colors.BLACK12)
        self.page.update()

    def list_will_drag_accept(self, e):
        if e.data == "true":
            self.inner_list.border = ft.border.all(2, ft.Colors.BLACK)
        self.update()

    def list_drag_leave(self, e):
        self.inner_list.border = ft.border.all(2, ft.Colors.BLACK12)
        self.update()

    def delete_list(self, e):
        self.board.remove_list(self, e)

    def edit_title(self, e):
        self.header.controls[0] = self.edit_field
        self.header.controls[1].visible = False
        self.update()

    def save_title(self, e):
        self.title = self.edit_field.controls[0].value
        self.header.controls[0] = ft.Text(
            value=self.title,
            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
            text_align=ft.TextAlign.LEFT,
            overflow=ft.TextOverflow.CLIP,
            expand=True,
        )
        self.header.controls[1].visible = True
        self.update()

    def add_item_handler(self, e):
        if self.new_item_field.value == "":
            return
        self.add_item()

    def add_item(
        self,
        item_text: str | None = None,
        priority: str = "Baixa",
        description: str = "",
        completed: bool = False,
        chosen_control: ft.Draggable | None = None,
        swap_control: ft.Draggable | None = None,
    ):
        controls_list = [x.controls[1] for x in self.items.controls]
        to_index = (
            controls_list.index(swap_control) if swap_control in controls_list else None
        )
        from_index = (
            controls_list.index(chosen_control)
            if chosen_control in controls_list
            else None
        )
        control_to_add = ft.Column(
            [
                ft.Container(
                    bgcolor=ft.Colors.BLACK26,
                    border_radius=ft.border_radius.all(30),
                    height=3,
                    alignment=ft.alignment.center_right,
                    width=200,
                    opacity=0.0,
                )
            ]
        )

        if (from_index is not None) and (to_index is not None):
            self.items.controls.insert(to_index, self.items.controls.pop(from_index))
            self.set_indicator_opacity(swap_control, 0.0)
        elif to_index is not None:
            new_item = Item(
                self,
                self.store,
                item_text,
                priority,
                description,
                completed=completed
            )
            control_to_add.controls.append(new_item)
            self.items.controls.insert(to_index, control_to_add)
        else:
            new_item = (
                Item(
                    self,
                    self.store,
                    item_text,
                    priority,
                    description,
                    completed=completed
                )
                if item_text
                else Item(
                    self,
                    self.store,
                    self.new_item_field.value,
                    self.priority_dropdown.value,
                    "",
                    completed=False
                )
            )
            control_to_add.controls.append(new_item)
            self.items.controls.append(control_to_add)
            self.store.add_item(self.board_list_id, new_item)
            self.new_item_field.value = ""

        self.page.update()

    def remove_item(self, item: Item):
        controls_list = [x.controls[1] for x in self.items.controls]
        del self.items.controls[controls_list.index(item)]
        self.store.remove_item(self.board_list_id, item.item_id)
        self.view.update()

    def set_indicator_opacity(self, item, opacity):
        controls_list = [x.controls[1] for x in self.items.controls]
        self.items.controls[controls_list.index(item)].controls[0].opacity = opacity
        self.view.update()