from typing import TYPE_CHECKING
import itertools
import flet as ft
from data_store import DataStore

if TYPE_CHECKING:
    from board_list import BoardList

class Item(ft.Container):
    id_counter = itertools.count(start=1)

    def __init__(
        self,
        list: "BoardList",
        store: DataStore,
        item_text: str,
        priority: str = "Baixa",
        description: str = "",
        tags: list[str] = None,  # Novo campo para tags
        item_id: int = None,
        completed: bool = False
    ):
        self.item_id = item_id if item_id is not None else next(Item.id_counter)
        self.store: DataStore = store
        self.list = list
        self.item_text = item_text
        self.priority = priority
        self.description = description
        self.tags = tags if tags is not None else []  # Lista de tags, vazia por padrão
        self.completed = completed

        self.checkbox = ft.Checkbox(
            label=f"{self.item_text}",
            width=200,
            value=self.completed,
            on_change=self.update_status,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
        )
        self.card_item = ft.Card(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                self.checkbox,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        border_radius=ft.border_radius.all(5),
                        padding=ft.padding.all(10),
                        on_click=self.open_edit_dialog,
                    )
                ],
                width=200,
                wrap=True,
            ),
            elevation=1,
            data=self.list,
            color=self.get_priority_color(),
        )

        self.view = ft.Draggable(
            group="items",
            content=ft.DragTarget(
                group="items",
                content=self.card_item,
                on_accept=self.drag_accept,
                on_leave=self.drag_leave,
                on_will_accept=self.drag_will_accept,
            ),
            data=self,
        )
        super().__init__(content=self.view)

    def get_priority_color(self):
        colors = {
            "Baixa": ft.Colors.GREEN_100,
            "Média": ft.Colors.ORANGE_100,
            "Alta": ft.Colors.RED_100,
        }
        return colors.get(self.priority, ft.Colors.GREY_100)

    def open_edit_dialog(self, e):
        def close_dlg(e):
            if name_field.value:
                self.item_text = name_field.value
                self.checkbox.label = self.item_text
                self.priority = priority_dropdown.value
                self.description = description_field.value
                self.tags = [tag.strip() for tag in tags_field.value.split(",") if tag.strip()]  # Converte texto em lista
                self.card_item.color = self.get_priority_color()
                self.store.remove_item(self.list.board_list_id, self.item_id)
                self.store.add_item(self.list.board_list_id, self)
                self.list.apply_filters(None)
                self.page.update()
            self.page.close(dialog)

        name_field = ft.TextField(label="Nome da Tarefa", value=self.item_text)
        priority_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Baixa"),
                ft.dropdown.Option("Média"),
                ft.dropdown.Option("Alta"),
            ],
            value=self.priority,
            label="Prioridade",
            width=200,
        )
        description_field = ft.TextField(
            label="Descrição",
            value=self.description,
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=200,
        )
        tags_field = ft.TextField(
            label="Tags (separadas por vírgula)",
            value=", ".join(self.tags),
            width=200,
        )

        dialog = ft.AlertDialog(
            title=ft.Text("Detalhes da Tarefa"),
            content=ft.Column(
                [
                    name_field,
                    priority_dropdown,
                    description_field,
                    tags_field,
                    ft.ElevatedButton(text="Guardar", on_click=close_dlg),
                ],
                tight=True,
                spacing=10,
            ),
        )
        self.page = self.list.page
        self.page.open(dialog)

    def update_status(self, e):
        self.completed = self.checkbox.value
        self.store.remove_item(self.list.board_list_id, self.item_id)
        self.store.add_item(self.list.board_list_id, self)
        self.list.apply_filters(None)
        self.page.update()

    def drag_accept(self, e):
        src = self.page.get_control(e.src_id)

        if src.content.content == e.control.content:
            self.card_item.elevation = 1
            self.list.set_indicator_opacity(self, 0.0)
            e.control.update()
            return

        if src.data.list == self.list:
            self.list.add_item(chosen_control=src.data, swap_control=self)
            self.card_item.elevation = 1
            e.control.update()
            return

        self.list.add_item(
            item_text=src.data.item_text,
            priority=src.data.priority,
            description=src.data.description,
            tags=src.data.tags,  # Passa as tags ao mover
            completed=src.data.completed,
            swap_control=self
        )
        src.data.list.remove_item(src.data)
        self.list.set_indicator_opacity(self, 0.0)
        self.card_item.elevation = 1
        self.page.update()

    def drag_will_accept(self, e):
        if e.data == "true":
            self.list.set_indicator_opacity(self, 1.0)
        self.card_item.elevation = 20 if e.data == "true" else 1
        self.page.update()

    def drag_leave(self, e):
        self.list.set_indicator_opacity(self, 0.0)
        self.card_item.elevation = 1
        self.page.update()