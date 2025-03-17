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
        self.page: ft.Page = page
        self.store: DataStore = store
        self.user: str | None = None  # Nome do usuário logado
        self.boards = []

        # Configuração da página
        self.page.title = "Flet Trello clone"
        self.page.padding = 0
        self.page.theme = ft.Theme(font_family="Verdana")
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme.page_transitions.windows = "cupertino"
        self.page.fonts = {"Pacifico": "Pacifico-Regular.ttf"}
        self.page.bgcolor = ft.Colors.BLUE_GREY_200
        self.page.on_route_change = self.route_change

        # Configuração da appbar
        self.login_profile_button = ft.PopupMenuItem(text="Log in", on_click=self.login)
        self.appbar_items = [
            self.login_profile_button,
            ft.PopupMenuItem(),  # divisor
            ft.PopupMenuItem(text="Settings"),
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
            bgcolor=ft.Colors.LIGHT_BLUE_ACCENT_700,
            actions=[
                ft.Container(
                    content=ft.PopupMenuButton(items=self.appbar_items),
                    margin=ft.margin.only(left=50, right=25),
                )
            ],
        )
        self.page.appbar = self.appbar

        # Inicializa o AppLayout (que contém o Sidebar)
        super().__init__(
            self,
            self.page,
            self.store,
            tight=True,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        # Adiciona a interface principal à página
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
                self.boards = self.store.get_boards()  # Carrega as boards do usuário logado
                print(f"Boards encontrados: {self.boards}")
                self.page.close(dialog)
                self.appbar_items[0] = ft.PopupMenuItem(text=f"{self.user}'s Profile")

                # Adiciona a view de boards e atualiza a página
                self.page.views.clear()  # Limpa a view de login
                self.page.views.append(
                    ft.View(
                        "/boards",
                        [self.appbar, self],
                        padding=ft.padding.all(0),
                        bgcolor=ft.Colors.BLUE_GREY_200,
                    )
                )
                self.page.update()  # Garante que a view esteja registrada

                # Agora atualiza a visualização das boards
                self.hydrate_all_boards_view()
                self.sidebar.sync_board_destinations()
                if len(self.boards) == 0:
                    self.create_new_board("My First Board")
                self.page.go("/boards")
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
            on_dismiss=lambda e: print("Diálogo fechado!"),
        )
        self.page.open(dialog)

    def route_change(self, e):
        troute = ft.TemplateRoute(self.page.route)
        
        # Se não houver usuário logado, força o redirecionamento para /login
        if not self.user:
            if troute.route != "/login":
                self.page.go("/login")
            return

        # Rotas permitidas apenas após login
        if troute.match("/"):
            self.page.go("/boards")
        elif troute.match("/board/:id"):
            if int(troute.id) >= len(self.store.get_boards()):
                self.page.go("/boards")
                return
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
    store.app = app  # Define o app no store após a criação
    page.add(app)

print("flet version: ", ft.version.version)
print("flet path: ", ft.__file__)
ft.app(target=main, assets_dir="../assets")