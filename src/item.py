from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board_list import BoardList
import itertools
import flet as ft
from data_store import DataStore


class Item(ft.Container):
    id_counter = itertools.count()

    def __init__(self, list: "BoardList", store: DataStore, item_text: str, priority: str = "Baixa", description: str = ""):
        self.item_id = next(Item.id_counter)
        self.store: DataStore = store
        self.list = list
        self.item_text = item_text
        self.priority = priority  # Campo de prioridade
        self.description = description  # Campo de descrição

        # Layout da card
        self.checkbox = ft.Checkbox(label=f"{self.item_text}", width=200, on_change=self.update_status)
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
                        on_click=self.open_edit_dialog,  # Tornar a card clicável
                    )
                ],
                width=200,
                wrap=True,
            ),
            elevation=1,
            data=self.list,
            color=self.get_priority_color(),  # Cor de fundo baseada na prioridade
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
        # Define a cor de fundo com base na prioridade
        colors = {
            "Baixa": ft.Colors.GREEN_100,  # Verde claro
            "Média": ft.Colors.ORANGE_100,  # Laranja claro
            "Alta": ft.Colors.RED_100,  # Vermelho claro
        }
        return colors.get(self.priority, ft.Colors.GREY_100)  # Cinza claro como padrão

    def open_edit_dialog(self, e):
        # Diálogo para editar a card
        def close_dlg(e):
            if name_field.value:
                self.item_text = name_field.value
                self.checkbox.label = self.item_text
                self.priority = priority_dropdown.value
                self.description = description_field.value
                self.card_item.color = self.get_priority_color()  # Atualiza a cor de fundo
                self.page.update()
            self.page.close(dialog)

        # Campos do diálogo
        name_field = ft.TextField(label="Nome da Card", value=self.item_text)
        priority_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Baixa"),
                ft.dropdown.Option("Média"),
                ft.dropdown.Option("Alta"),
            ],
            value=self.priority,  # Prioridade atual
            label="Prioridade",
            width=200,
        )
        description_field = ft.TextField(
            label="Descrição",
            value=self.description,
            multiline=True,  # Campo de texto longo
            min_lines=3,
            max_lines=5,
            width=200,
        )

        dialog = ft.AlertDialog(
            title=ft.Text("Detalhes"),
            content=ft.Column(
                [
                    name_field,
                    priority_dropdown,
                    description_field,
                    ft.ElevatedButton(text="Guardar", on_click=close_dlg),
                ],
                tight=True,
                spacing=10,
            ),
        )
        self.page.open(dialog)

    def update_status(self, e):
        # Atualizar o estado da card (concluída/não concluída)
        self.list.apply_filters(None)  # Reaplicar os filtros ao mudar o estado

    def drag_accept(self, e):
        src = self.page.get_control(e.src_id)

        # skip if item is dropped on itself
        if src.content.content == e.control.content:
            self.card_item.elevation = 1
            self.list.set_indicator_opacity(self, 0.0)
            e.control.update()
            return

        # item dropped within same list but not on self
        if src.data.list == self.list:
            self.list.add_item(chosen_control=src.data, swap_control=self)
            self.card_item.elevation = 1
            e.control.update()
            return

        # item added to different list
        self.list.add_item(src.data.item_text, swap_control=self)
        # remove from the list to which draggable belongs
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