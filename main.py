from src.database.database_connection import create_database_connection
from src.interface.main_window import MainWindow
from src.repositories.customer_repository import CustomerRepository
from src.repositories.sale_repository import SaleRepository
from src.repositories.stock_item_repository import StockItemRepository
from src.services.customer_service import CustomerService
from src.services.sale_service import SaleService
from src.services.stock_item_service import StockItemService


def main() -> None:
    connection = create_database_connection()

    customer_service = CustomerService(CustomerRepository(connection))
    stock_item_repository = StockItemRepository(connection)
    stock_item_service = StockItemService(stock_item_repository)
    sale_service = SaleService(SaleRepository(connection), stock_item_repository)

    main_window = MainWindow(customer_service, stock_item_service, sale_service)
    main_window.mainloop()


if __name__ == "__main__":
    main()
