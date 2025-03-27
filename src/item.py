from typing import TYPE_CHECKING
import itertools
import flet as ft
from data_store import DataStore
import spacy
from spacy.cli import download
from langdetect import detect

if TYPE_CHECKING:
    from board_list import BoardList

class Item(ft.Container):
    id_counter = itertools.count(start=1)

    # Verifica e instala o modelo de inglês
    try:
        nlp_en = spacy.load("en_core_web_sm")
    except OSError:
        print("Baixando modelo 'en_core_web_sm'...")
        download("en_core_web_sm")
        nlp_en = spacy.load("en_core_web_sm")

    # Verifica e instala o modelo de português
    try:
        nlp_pt = spacy.load("pt_core_news_sm")
    except OSError:
        print("Baixando modelo 'pt_core_news_sm'...")
        download("pt_core_news_sm")
        nlp_pt = spacy.load("pt_core_news_sm")

    def __init__(
        self,
        list: "BoardList",
        store: DataStore,
        item_text: str,
        priority: str = "Baixa",
        description: str = "",
        tags: list[str] = None,
        item_id: int = None,
        completed: bool = False
    ):
        self.item_id = item_id if item_id is not None else next(Item.id_counter)
        self.store: DataStore = store
        self.list = list
        self.item_text = item_text
        self.priority = priority
        self.description = description
        self.tags = tags if tags is not None else []
        self.completed = completed
        self.page = list.page

        # Checkbox sem label
        self.checkbox = ft.Checkbox(
            value=self.completed,
            on_change=self.update_status,
        )
        self.title_text = ft.Text(
            value=self.item_text,
            max_lines=1,  
            overflow=ft.TextOverflow.ELLIPSIS,  
            style=ft.TextStyle(color=ft.Colors.BLACK),
            width=140,  
        )

        self.card_item = ft.Card(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [self.checkbox, self.title_text],  # Checkbox e texto lado a lado
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5,  # Espaço entre checkbox e texto
                        ),
                        border_radius=ft.border_radius.all(5),
                        padding=ft.padding.all(10),
                        on_click=self.open_edit_dialog,
                    )
                ],
                width=200,  # Largura total do cartão
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
            "Media": ft.Colors.ORANGE_100,
            "Alta": ft.Colors.RED_100,
        }
        return colors.get(self.priority, ft.Colors.GREY_100)

    def detect_language(self, text: str) -> str:
        try:
            lang = detect(text)
            if lang.startswith("pt"):
                return "pt"
            elif lang.startswith("en"):
                return "en"
            else:
                return "en"
        except:
            return "en"

    def suggest_tags(self):
        text_to_analyze = f"{self.item_text} {self.description}".strip()
        if not text_to_analyze:
            return []
        lang = self.detect_language(text_to_analyze)
        nlp = self.nlp_pt if lang == "pt" else self.nlp_en
        doc = nlp(text_to_analyze.lower())
        tags = set()
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
                tags.add(token.text)
        for ent in doc.ents:
            tags.add(ent.text.lower())
        suggested_tags = [tag for tag in tags if len(tag) > 2]
        return suggested_tags[:5]

    def open_edit_dialog(self, e):
        def close_dlg(e):
            if name_field.value:
                self.item_text = name_field.value
                self.title_text.value = self.item_text  # Atualiza o texto exibido
                self.priority = priority_dropdown.value
                self.description = description_field.value
                self.tags = [tag.strip() for tag in tags_field.value.split(",") if tag.strip()]
                self.card_item.color = self.get_priority_color()
                self.store.remove_item(self.list.board_list_id, self.item_id)
                self.store.add_item(self.list.board_list_id, self)
                self.list.apply_filters(None)
                self.list.page.update()
            self.list.page.close(dialog)

        def open_delete_confirmation(e):
            def confirm_delete(e):
                self.list.remove_item(self)
                self.list.page.close(confirm_dialog)
                self.list.page.close(dialog)
                snack_bar = ft.SnackBar(
                    content=ft.Text(f"Item '{self.item_text}' removido com sucesso!"),
                    open=True
                )
                self.list.page.snack_bar = snack_bar
                self.list.page.update()

            def cancel_delete(e):
                self.list.page.close(confirm_dialog)

            confirm_dialog = ft.AlertDialog(
                title=ft.Text("Confirmar Exclusao"),
                content=ft.Text(f"Tem certeza que deseja excluir o item '{self.item_text}'?"),
                actions=[
                    ft.ElevatedButton("Cancelar", on_click=cancel_delete),
                    ft.ElevatedButton("Excluir", bgcolor=ft.Colors.RED_200, on_click=confirm_delete),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.list.page.open(confirm_dialog)

        def apply_suggested_tags(e):
            suggested_tags = self.suggest_tags()
            current_tags = set(self.tags)
            current_tags.update(suggested_tags)
            tags_field.value = ", ".join(current_tags)
            self.list.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Sugeridas tags em {self.detect_language(f'{self.item_text} {self.description}')}"),
                open=True
            )
            self.list.page.update()

        name_field = ft.TextField(label="Nome da Tarefa", value=self.item_text)
        priority_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Baixa"),
                ft.dropdown.Option("Media"),
                ft.dropdown.Option("Alta"),
            ],
            value=self.priority,
            label="Prioridade",
            width=200,
        )
        description_field = ft.TextField(
            label="Descricao",
            value=self.description,
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=200,
        )
        tags_field = ft.TextField(
            label="Tags (separadas por virgula)",
            value=", ".join(self.tags),
            width=200,
        )
        suggest_tags_button = ft.ElevatedButton(
            text="Sugerir Tags",
            on_click=apply_suggested_tags,
            bgcolor=ft.Colors.BLUE_200,
            color=ft.Colors.BLACK,
            width=200,
        )
        delete_button = ft.ElevatedButton(
            text="Excluir",
            bgcolor=ft.Colors.RED_200,
            color=ft.Colors.WHITE,
            on_click=open_delete_confirmation
        )

        dialog = ft.AlertDialog(
            title=ft.Text("Detalhes da Tarefa"),
            content=ft.Column(
                [
                    name_field,
                    priority_dropdown,
                    description_field,
                    tags_field,
                    suggest_tags_button,
                    ft.Row(
                        [
                            delete_button,
                            ft.ElevatedButton(text="Guardar", on_click=close_dlg),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                tight=True,
                spacing=10,
                width=200,
            ),
        )
        self.list.page.open(dialog)

    def update_status(self, e):
        self.completed = self.checkbox.value
        self.store.remove_item(self.list.board_list_id, self.item_id)
        self.store.add_item(self.list.board_list_id, self)
        self.list.apply_filters(None)
        self.list.page.update()

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
            tags=src.data.tags,
            completed=src.data.completed,
            swap_control=self
        )
        src.data.list.remove_item(src.data)
        self.list.set_indicator_opacity(self, 0.0)
        self.card_item.elevation = 1
        self.list.page.update()

    def drag_will_accept(self, e):
        if e.data == "true":
            self.list.set_indicator_opacity(self, 1.0)
        self.card_item.elevation = 20 if e.data == "true" else 1
        self.list.page.update()

    def drag_leave(self, e):
        self.list.set_indicator_opacity(self, 0.0)
        self.card_item.elevation = 1
        self.list.page.update()