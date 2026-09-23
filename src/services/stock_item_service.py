import shutil
import sqlite3
import uuid
from pathlib import Path

from src.models.stock_item import StockItem
from src.repositories.stock_item_repository import StockItemRepository

DEFAULT_IMAGES_FOLDER = Path(__file__).parent.parent.parent / "data" / "item_images"
MAX_NAME_LENGTH = 120
MAX_DESCRIPTION_LENGTH = 300


class InvalidStockItemDataError(Exception):
    pass


class StockItemService:
    def __init__(
        self,
        stock_item_repository: StockItemRepository,
        images_folder: Path = DEFAULT_IMAGES_FOLDER,
    ):
        self.stock_item_repository = stock_item_repository
        self.images_folder = images_folder

    def register_item(
        self,
        name: str,
        description: str,
        quantity_in_stock: int,
        unit_price: float,
        original_image_path: str | None = None,
    ) -> StockItem:
        name = name.strip()
        description = description.strip()

        self._validate_item_data(name, description, quantity_in_stock, unit_price)

        saved_image_path = None
        if original_image_path:
            saved_image_path = self.copy_image_to_data_folder(original_image_path)

        item = StockItem(
            name=name,
            description=description,
            quantity_in_stock=quantity_in_stock,
            unit_price=unit_price,
            image_path=saved_image_path,
        )
        return self.stock_item_repository.save(item)

    def update_item(self, item: StockItem) -> None:
        self._validate_item_data(item.name, item.description, item.quantity_in_stock, item.unit_price)
        self.stock_item_repository.update(item)

    def find_item_by_id(self, id: int) -> StockItem | None:
        return self.stock_item_repository.find_by_id(id)

    def list_all_items(self) -> list[StockItem]:
        return self.stock_item_repository.find_all()

    def find_items_by_name(self, name_fragment: str) -> list[StockItem]:
        return self.stock_item_repository.find_by_partial_name(name_fragment)

    def delete_item(self, id: int) -> None:
        try:
            self.stock_item_repository.delete(id)
        except sqlite3.IntegrityError as error:
            raise InvalidStockItemDataError(
                "Não é possível excluir um item que já foi vendido."
            ) from error

    def copy_image_to_data_folder(self, original_image_path: str) -> str:
        original_path = Path(original_image_path)
        if not original_path.is_file():
            raise InvalidStockItemDataError("A imagem escolhida não foi encontrada.")

        self.images_folder.mkdir(parents=True, exist_ok=True)

        unique_file_name = f"{uuid.uuid4().hex}{original_path.suffix}"
        destination_path = self.images_folder / unique_file_name

        try:
            shutil.copyfile(original_path, destination_path)
        except OSError as error:
            raise InvalidStockItemDataError("Não foi possível carregar a imagem escolhida.") from error

        return str(destination_path)

    @staticmethod
    def _validate_item_data(name: str, description: str, quantity_in_stock: int, unit_price: float) -> None:
        if not name:
            raise InvalidStockItemDataError("O nome do item é obrigatório.")
        if len(name) > MAX_NAME_LENGTH:
            raise InvalidStockItemDataError(f"O nome do item não pode ter mais que {MAX_NAME_LENGTH} caracteres.")
        if len(description) > MAX_DESCRIPTION_LENGTH:
            raise InvalidStockItemDataError(
                f"A descrição não pode ter mais que {MAX_DESCRIPTION_LENGTH} caracteres."
            )
        if quantity_in_stock < 0:
            raise InvalidStockItemDataError("A quantidade em estoque não pode ser negativa.")
        if unit_price < 0:
            raise InvalidStockItemDataError("O preço unitário não pode ser negativo.")
