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
        self.page = page  # Armazena a referência diretamente
        self.store = store
        self.user: str | None = None  # Nome do usuário logado
        self.boards = []

        # Define appbar_items antes de qualquer uso
        self.appbar_items = [
            ft.PopupMenuItem(text="Log in", on_click=self.login),
            ft.PopupMenuItem(),  # divisor
            ft.PopupMenuItem(text="Settings"),
        ]

        # Configuração inicial da AppBar
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
            bgcolor=ft.Colors.LIGHT_BLUE_ACCENT_700,
            actions=[
                ft.Container(
                    content=ft.PopupMenuButton(items=self.appbar_items),
                    margin=ft.margin.only(left=50, right=25),
                )
            ],
        )

        # Inicializa o AppLayout
        super().__init__(
            self,
            self.page,
            self.store,
            tight=True,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        # Configuração inicial da página
        self.page.title = "Flet Trello clone"
        self.page.padding = 0
        self.page.theme = ft.Theme(font_family="Verdana")
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme.page_transitions.windows = "cupertino"
        self.page.fonts = {"Pacifico": "Pacifico-Regular.ttf"}
        self.page.bgcolor = ft.Colors.BLUE_GREY_200
        self.page.on_route_change = self.route_change
        self.page.appbar = self.appbar

        print("Inicializando TrelloApp, self.page:", self.page)

        # Configura a tela de login inicial
        self.initialize_login()

    def initialize_login(self):
        """Configura a tela de login."""
        print("Configurando tela de login, self.page:", self.page)
        self.appbar_items = [
            ft.PopupMenuItem(text="Log in", on_click=self.login),
            ft.PopupMenuItem(),  # divisor
            ft.PopupMenuItem(text="Settings"),
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
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                ],
                bgcolor=ft.Colors.BLUE_GREY_200,
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
                print(f"Usuário definido: {self.user}")
                self.page.client_storage.set("current_user", user_name.value)
                self.store.set_current_user(user)
                self.boards = self.store.get_boards()
                print(f"Boards encontrados: {self.boards}")
                self.page.close(dialog)
                self.appbar_items = [
                    ft.PopupMenuItem(text=f"{self.user}'s Profile"),
                    ft.PopupMenuItem(),  # divisor
                    ft.PopupMenuItem(text="Settings"),
                    ft.PopupMenuItem(text="Logout", on_click=self.logout),
                ]
                self.appbar.actions[0].content = ft.PopupMenuButton(items=self.appbar_items)
                self.page.views.clear()
                self.page.views.append(
                    ft.View(
                        "/boards",
                        [self.appbar, self],
                        padding=ft.padding.all(0),
                        bgcolor=ft.Colors.BLUE_GREY_200,
                    )
                )
                self.page.update()
                self.hydrate_all_boards_view()
                self.sidebar.sync_board_destinations()
                if len(self.boards) == 0:
                    self.create_new_board("My First Board")
                self.page.route = "/boards"
                self.page.update()
            else:
                user_name.error_text = "Usuário ou senha inválidos"
                self.page.update()

        print("Tentando abrir modal de login, self.page:", self.page)
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
            on_dismiss=lambda e: print("Diálogo fechado!"),
        )
        self.page.open(dialog)

    def logout(self, e):
        print(f"Logout do usuário: {self.user}, self.page antes do logout:", self.page)
        self.user = None
        self.page.client_storage.remove("current_user")
        self.store.set_current_user(None)
        self.boards = []
        self.appbar_items = [
            ft.PopupMenuItem(text="Log in", on_click=self.login),
            ft.PopupMenuItem(),  # divisor
            ft.PopupMenuItem(text="Settings"),
        ]
        self.appbar.actions[0].content = ft.PopupMenuButton(items=self.appbar_items)
        
        # Redireciona para a tela de login
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/login",
                [
                    ft.Column(
                        [
                            ft.Text("Bem-vindo ao Trolli", size=30, font_family="Pacifico"),
                            ft.ElevatedButton("Fazer Login", on_click=self.login),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                ],
                bgcolor=ft.Colors.BLUE_GREY_200,
            )
        )
        self.page.route = "/login"
        self.page.update()
        print("Após logout, self.page:", self.page)

    def route_change(self, e):
        if self.page is None:
            print("Erro: self.page é None no route_change")
            return
        troute = ft.TemplateRoute(self.page.route)
        print(f"Route change para: {troute.route}, self.page:", self.page)
        
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
            self.set_members_view()
        self.page.update()

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
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.open(dialog)
        dialog.open = True
        self.page.update()
        dialog_text.focus()

    def create_new_board(self, board_name):
        print(f"Criando novo board: {board_name}")
        new_board = Board(self, self.store, board_name, self.page)
        self.store.add_board(new_board)
        self.boards = self.store.get_boards()
        print(f"Board '{board_name}' adicionado ao JSON.")
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

print("flet version: ", ft.version.version)
print("flet path: ", ft.__file__)
ft.app(target=main, assets_dir="../assets")