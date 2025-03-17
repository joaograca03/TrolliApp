import flet as ft
from data_store import DataStore

class Sidebar(ft.Container):
    def __init__(self, app_layout, store: DataStore):
        self.store: DataStore = store
        self.app_layout = app_layout
        self.page = app_layout.page  # Acesso ao page via app_layout
        self.nav_rail_visible = True

        self.top_nav_items = [
            ft.NavigationRailDestination(
                label_content=ft.Text("Boards"),
                label="Boards",
                icon=ft.Icons.BOOK_OUTLINED,
                selected_icon=ft.Icons.BOOK_OUTLINED,
            ),
            ft.NavigationRailDestination(
                label_content=ft.Text("Members"),
                label="Members",
                icon=ft.Icons.PERSON,
                selected_icon=ft.Icons.PERSON,
            ),
        ]

        self.top_nav_rail = ft.NavigationRail(
            selected_index=None,
            label_type=ft.NavigationRailLabelType.ALL,
            on_change=self.top_nav_change,
            destinations=self.top_nav_items,
            bgcolor=ft.Colors.BLUE_GREY,
            extended=True,
            height=110,
        )

        self.bottom_nav_rail = ft.NavigationRail(
            selected_index=None,
            label_type=ft.NavigationRailLabelType.ALL,
            on_change=self.bottom_nav_change,
            extended=True,
            expand=True,
            bgcolor=ft.Colors.BLUE_GREY,
        )
        self.toggle_nav_rail_button = ft.IconButton(ft.Icons.ARROW_BACK)

        super().__init__(
            content=ft.Column(
                [
                    ft.Row(
                        [ft.Text("Workspace")],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(
                        bgcolor=ft.Colors.BLACK26,
                        border_radius=ft.border_radius.all(30),
                        height=1,
                        alignment=ft.alignment.center_right,
                        width=220,
                    ),
                    self.top_nav_rail,
                    ft.Container(
                        bgcolor=ft.Colors.BLACK26,
                        border_radius=ft.border_radius.all(30),
                        height=1,
                        alignment=ft.alignment.center_right,
                        width=220,
                    ),
                    self.bottom_nav_rail,
                ],
                tight=True,
            ),
            padding=ft.padding.all(15),
            margin=ft.margin.all(0),
            width=250,
            bgcolor=ft.Colors.BLUE_GREY,
            visible=self.nav_rail_visible,
        )

    def sync_board_destinations(self):
        boards = self.store.get_boards()
        self.bottom_nav_rail.destinations = [
            ft.NavigationRailDestination(
                label_content=ft.TextField(
                    value=b.name,
                    hint_text=b.name,
                    text_size=12,
                    read_only=True,
                    on_focus=self.board_name_focus,
                    on_blur=self.board_name_blur,
                    border=ft.InputBorder.NONE,
                    height=50,
                    width=150,
                    text_align=ft.TextAlign.START,
                    data=i,
                ),
                label=b.name,
                selected_icon=ft.Icons.CHEVRON_RIGHT_ROUNDED,
                icon=ft.Icons.CHEVRON_RIGHT_OUTLINED,
            )
            for i, b in enumerate(boards)
        ]
        self.update()

    def toggle_nav_rail(self, e):
        self.visible = not self.visible
        self.page.update()

    def board_name_focus(self, e):
        e.control.read_only = False
        e.control.border = ft.InputBorder.OUTLINE
        self.page.update()

    def board_name_blur(self, e):
        board_index = e.control.data
        new_name = e.control.value
        board = self.store.get_boards()[board_index]
        self.store.update_board(board, {"name": new_name})  # Atualiza o nome no store
        self.app_layout.hydrate_all_boards_view()  # Reflete a mudança na UI
        e.control.read_only = True
        e.control.border = ft.InputBorder.NONE
        self.page.update()

    def top_nav_change(self, e):
        index = e.control.selected_index if hasattr(e, "control") else e
        self.bottom_nav_rail.selected_index = None
        self.top_nav_rail.selected_index = index
        if index == 0:
            self.page.route = "/boards"
        elif index == 1:
            self.page.route = "/members"
        self.page.update()

    def bottom_nav_change(self, e):
        index = e.control.selected_index if hasattr(e, "control") else e
        self.top_nav_rail.selected_index = None
        self.bottom_nav_rail.selected_index = index
        self.page.route = f"/board/{index}"
        self.page.update()