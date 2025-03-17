import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board import Board
    from board_list import BoardList
    from user import User
    from item import Item

from data_store import DataStore
from board import Board

class JSONStore(DataStore):
    def __init__(self, filename="data.json", app=None, page=None):
        self.filename = filename
        self.data = self._load_data()
        self.current_user = None
        self.app = app
        self.page = page

    def _load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                return json.load(file)
        return {"users": []}

    def _save_data(self):
        with open(self.filename, "w") as file:
            json.dump(self.data, file, indent=4)

    def set_current_user(self, user):
        self.current_user = user
        print(f"Usuário definido: {user['name']}")

    def _get_current_user(self):
        if self.current_user:
            return self.current_user
        if self.page and self.page.client_storage.get("current_user"):
            current_user_name = self.page.client_storage.get("current_user")
            user = self.get_user(current_user_name)
            if user:
                self.current_user = user
                print(f"Usuário recuperado do client_storage: {user['name']}")
                return user
        return None

    def _get_next_board_id(self):
        user = self._get_current_user()
        if user and user["boards"]:
            return max(b["id"] for b in user["boards"]) + 1
        return 1  # Começa em 1 se não houver boards

    def add_board(self, board: "Board"):
        user = self._get_current_user()
        if user:
            new_id = self._get_next_board_id()
            board.board_id = new_id  # Define o ID do board
            print(f"Adicionando board '{board.name}' para o usuário '{user['name']}'")
            user["boards"].append({
                "id": board.board_id,
                "name": board.name,
                "lists": []
            })
            self._save_data()

    def get_board(self, id: int):
        user = self._get_current_user()
        if user:
            for board_data in user["boards"]:
                if board_data["id"] == id:
                    return Board(
                        self.app,
                        self,
                        board_data["name"],
                        self.page,
                        board_id=board_data["id"],  # Passa o ID do JSON
                        lists=board_data["lists"]
                    )
        return None

    def get_boards(self):
        user = self._get_current_user()
        if user and self.app and self.page:
            return [
                Board(
                    self.app,
                    self,
                    b["name"],
                    self.page,
                    board_id=b["id"],  # Passa o ID do JSON
                    lists=b["lists"]
                )
                for b in user["boards"]
            ]
        return []

    def update_board(self, board: "Board", update: dict):
        user = self._get_current_user()
        if user:
            for b in user["boards"]:
                if b["id"] == board.board_id:
                    b.update(update)
                    board.name = update.get("name", board.name)
                    self._save_data()
                    print(f"Board atualizado: {b['name']}")
                    break

    def remove_board(self, board: "Board"):
        user = self._get_current_user()
        if user:
            user["boards"] = [b for b in user["boards"] if b["id"] != board.board_id]
            self._save_data()

    def add_list(self, board_id: int, list: "BoardList"):
        user = self._get_current_user()
        if user:
            for board in user["boards"]:
                if board["id"] == board_id:
                    if not any(l["id"] == list.board_list_id for l in board["lists"]):
                        board["lists"].append({
                            "id": list.board_list_id,
                            "title": list.title,
                            "color": list.color,
                            "items": []
                        })
                        self._save_data()

    def get_lists_by_board(self, board_id: int):
        user = self._get_current_user()
        if user:
            for board in user["boards"]:
                if board["id"] == board_id:
                    return board["lists"]
        return []

    def remove_list(self, board_id: int, list_id: int):
        user = self._get_current_user()
        if user:
            for board in user["boards"]:
                if board["id"] == board_id:
                    board["lists"] = [l for l in board["lists"] if l["id"] != list_id]
                    self._save_data()

    def add_item(self, list_id: int, item: "Item"):
        user = self._get_current_user()
        if user:
            for board in user["boards"]:
                for list in board["lists"]:
                    if list["id"] == list_id:
                        list["items"].append({
                            "id": item.item_id,
                            "item_text": item.item_text,
                            "priority": item.priority,
                            "description": item.description,
                            "completed": item.completed
                        })
                        self._save_data()

    def get_items(self, list_id: int):
        user = self._get_current_user()
        if user:
            for board in user["boards"]:
                for list in board["lists"]:
                    if list["id"] == list_id:
                        return list["items"]
        return []

    def remove_item(self, list_id: int, item_id: int):
        user = self._get_current_user()
        if user:
            for board in user["boards"]:
                for list in board["lists"]:
                    if list["id"] == list_id:
                        list["items"] = [i for i in list["items"] if i["id"] != item_id]
                        self._save_data()

    def add_user(self, user: "User"):
        self.data["users"].append({
            "name": user.name,
            "password": user.password,
            "boards": []
        })
        self._save_data()

    def get_users(self):
        return self.data["users"]

    def get_user(self, name: str):
        for user in self.data["users"]:
            if user["name"] == name:
                return user
        return None

    def remove_user(self, name: str):
        self.data["users"] = [u for u in self.data["users"] if u["name"] != name]
        self._save_data()