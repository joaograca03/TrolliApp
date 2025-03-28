import os
import flet as ft
from app_layout import AppLayout
from board import Board
from user import User
from data_store import DataStore
from jsonstore import JSONStore

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class TrelloApp(AppLayout):
    def __init__(self, page: ft.Page, store: DataStore):
        self.page = page
        self.store = store
        self.user: str | None = None
        self.boards = []

        # Restaura o tema salvo ou usa LIGHT como padrão
        saved_theme = self.page.client_storage.get("theme_mode")
        if saved_theme == "DARK":
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT

        self.appbar_items = [
            ft.PopupMenuItem(text="Log in", on_click=self.login),
            ft.PopupMenuItem(),  # divisor
            ft.PopupMenuItem(
                text="Dark Mode" if self.page.theme_mode == ft.ThemeMode.LIGHT else "Light Mode",
                on_click=self.toggle_theme
            ),
        ]

        self.appbar = ft.AppBar(
            leading=ft.Icon(ft.Icons.GRID_GOLDENRATIO_ROUNDED),
            leading_width=100,
            title=ft.Text(
                "Trolli",
                font_family="Pacifico",
                size=32,
                text_align=ft.TextAlign.START,
            ),
            center_title=False,
            toolbar_height=75,
            actions=[
                ft.Container(
                    content=ft.PopupMenuButton(items=self.appbar_items),
                    margin=ft.margin.only(left=50, right=25),
                )
            ],
        )

        super().__init__(
            self,
            self.page,
            self.store,
            tight=True,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        self.page.title = "Flet Trello clone"
        self.page.padding = 0
        self.page.theme = ft.Theme(font_family="Verdana")
        self.page.theme_mode = self.page.theme_mode  # Usa o tema restaurado
        self.page.theme.page_transitions.windows = "cupertino"
        self.page.fonts = {"Pacifico": "Pacifico-Regular.ttf"}
        self.page.on_route_change = self.route_change
        self.page.appbar = self.appbar

        self.update_theme_colors()  # Aplica as cores iniciais com base no tema
        self.initialize_login()

    def update_theme_colors(self):
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.bgcolor = ft.Colors.GREY_900
            self.sidebar.bgcolor = ft.Colors.GREY_800
            self.appbar.bgcolor = ft.Colors.BLUE_GREY_900
        else:
            self.page.bgcolor = ft.Colors.BLUE_GREY_200
            self.sidebar.bgcolor = ft.Colors.BLUE_GREY
            self.appbar.bgcolor = ft.Colors.LIGHT_BLUE_ACCENT_700

        # Atualiza as views para refletir a cor de fundo da página
        for view in self.page.views: 
            view.bgcolor = self.page.bgcolor

        # Atualiza apenas listas válidas com page definido
        for board in self.store.get_boards():
            for list_control in board.board_lists.controls[:-1]:  
                if hasattr(list_control, 'page') and list_control.page is not None:
                    list_control.update_theme()
        self.page.update()

    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            e.control.text = "Light Mode"
            self.page.client_storage.set("theme_mode", "DARK")
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            e.control.text = "Dark Mode"
            self.page.client_storage.set("theme_mode", "LIGHT")
        self.update_theme_colors()  # Atualiza as cores de fundo
        # Se a view ativa for "Members", atualiza-a para refletir o novo tema
        if self.active_view == self.members_view:
            self.set_members_view()

    def initialize_login(self):
        self.appbar_items = [
            ft.PopupMenuItem(text="Log in", on_click=self.login),
            ft.PopupMenuItem(),  # divisor
            ft.PopupMenuItem(
                text="Dark Mode" if self.page.theme_mode == ft.ThemeMode.LIGHT else "Light Mode",
                on_click=self.toggle_theme
            ),
        ]
        self.appbar.actions[0].content = ft.PopupMenuButton(items=self.appbar_items)
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/login",
                [
                    ft.Column(
                        [
                            ft.Text("Bem-vindo ao Trolli", size=30, font_family="Pacifico"),
                            ft.ElevatedButton("Fazer Login", on_click=self.login),
                            ft.ElevatedButton("Registrar", on_click=self.register),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                ],
                bgcolor=self.page.bgcolor,  # Usa a cor dinâmica da página
            )
        )
        self.page.route = "/login"
        self.page.update()

    def login(self, e):
        def close_dlg(e):
            if user_name.value == "" or password.value == "":
                user_name.error_text = "Por favor, insira o nome de usuário"
                password.error_text = "Por favor, insira a senha"
                self.page.update()
                return

            user = self.store.get_user(user_name.value)
            if user and user["password"] == password.value:
                self.user = user_name.value
                self.page.client_storage.set("current_user", user_name.value)
                self.store.set_current_user(user)
                self.boards = self.store.get_boards()
                self.page.close(dialog)
                self.appbar_items = [
                    ft.PopupMenuItem(content=ft.Text(f"{self.user}'s Profile")),
                    ft.PopupMenuItem(),  # Divisor
                    ft.PopupMenuItem(
                        text="Dark Mode" if self.page.theme_mode == ft.ThemeMode.LIGHT else "Light Mode",
                        on_click=self.toggle_theme
                    ),
                    ft.PopupMenuItem(text="Close App", on_click=self.close_app),  # Novo botão
                ]
                self.appbar.actions[0].content = ft.PopupMenuButton(items=self.appbar_items)
                self.page.views.clear()
                self.page.views.append(
                    ft.View(
                        "/boards",
                        [self.appbar, self],
                        padding=ft.padding.all(0),
                        bgcolor=self.page.bgcolor,  
                    )
                )
                self.page.update()
                self.hydrate_all_boards_view()
                self.sidebar.refresh()  # Atualiza o Sidebar para refletir o estado do usuário
                self.sidebar.sync_board_destinations()
                if len(self.boards) == 0:
                    self.create_new_board("My First Board")
                self.page.route = "/boards"
                self.page.update()
            else:
                user_name.error_text = "Usuário ou senha inválidos"
                self.page.update()

        user_name = ft.TextField(label="Nome de usuário")
        password = ft.TextField(label="Senha", password=True)
        dialog = ft.AlertDialog(
            title=ft.Text("Por favor, insira suas credenciais de login"),
            content=ft.Column(
                [
                    user_name,
                    password,
                    ft.ElevatedButton(text="Login", on_click=close_dlg),
                ],
                tight=True,
            ),
        )
        self.page.open(dialog)

    def register(self, e):
        def close_dlg(e):
            if user_name.value == "" or password.value == "":
                user_name.error_text = "Por favor, insira o nome de usuário"
                password.error_text = "Por favor, insira a senha"
                self.page.update()
                return

            if self.store.get_user(user_name.value):
                user_name.error_text = "Usuário já existe"
                self.page.update()
                return

            new_user = User(user_name.value, password.value)
            self.store.add_user(new_user)
            self.page.close(dialog)
            self.page.snack_bar = ft.SnackBar(ft.Text("Usuário registrado com sucesso!"), open=True)
            self.page.update()

        user_name = ft.TextField(label="Nome de usuário")
        password = ft.TextField(label="Senha", password=True)
        dialog = ft.AlertDialog(
            title=ft.Text("Registrar Novo Usuário"),
            content=ft.Column(
                [
                    user_name,
                    password,
                    ft.ElevatedButton(text="Registrar", on_click=close_dlg),
                ],
                tight=True,
            ),
        )
        self.page.open(dialog)

    def close_app(self, e):
        self.page.window.close()  # Fecha a janela do aplicativo

    def route_change(self, e):
        if self.page is None:
            return
        troute = ft.TemplateRoute(self.page.route)
        
        if not self.user and troute.route != "/login":
            self.page.route = "/login"
            self.page.update()
            return

        if troute.match("/"):
            self.page.route = "/boards"
        elif troute.match("/board/:id"):
            if int(troute.id) >= len(self.store.get_boards()):
                self.page.route = "/boards"
            else:
                self.set_board_view(int(troute.id))
        elif troute.match("/boards"):
            self.set_all_boards_view()
        elif troute.match("/members"):
            if self.is_admin():
                self.set_members_view()
            else:
                self.page.route = "/boards"
        self.page.update()

    def is_admin(self):
        user = self.store._get_current_user()
        return user and user["name"] == "admin"

    def add_board(self, e):
        def close_dlg(e):
            if (hasattr(e.control, "text") and not e.control.text == "Cancel") or (
                type(e.control) is ft.TextField and e.control.value != ""
            ):
                self.create_new_board(dialog_text.value)
            self.page.close(dialog)
            self.page.update()

        def textfield_change(e):
            if dialog_text.value == "":
                create_button.disabled = True
            else:
                create_button.disabled = False
            self.page.update()

        dialog_text = ft.TextField(
            label="New Board Name", on_submit=close_dlg, on_change=textfield_change
        )
        create_button = ft.ElevatedButton(
            text="Create", bgcolor=ft.Colors.BLUE_200, on_click=close_dlg, disabled=True
        )
        dialog = ft.AlertDialog(
            title=ft.Text("Name your new board"),
            content=ft.Column(
                [
                    dialog_text,
                    ft.Row(
                        [
                            ft.ElevatedButton(text="Cancel", on_click=close_dlg),
                            create_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                tight=True,
            ),
        )
        self.page.open(dialog)
        dialog.open = True
        self.page.update()
        dialog_text.focus()

    def create_new_board(self, board_name):
        new_board = Board(self, self.store, board_name, self.page)
        self.store.add_board(new_board)
        self.boards = self.store.get_boards()
        self.hydrate_all_boards_view()
        self.sidebar.sync_board_destinations()

    def delete_board(self, e):
        self.store.remove_board(e.control.data)
        self.boards = self.store.get_boards()
        self.set_all_boards_view()
        self.sidebar.sync_board_destinations()

def main(page: ft.Page):
    store = JSONStore(app=None, page=page)
    app = TrelloApp(page, store)
    store.app = app
    page.add(app)

ft.app(target=main, assets_dir="../assets")
#ft.app(target=main, view=ft.WEB_BROWSER, host="0.0.0.0", port=3000, assets_dir="../assets")