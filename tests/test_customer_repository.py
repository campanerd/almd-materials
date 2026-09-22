from src.models.customer import Customer
from src.repositories.customer_repository import CustomerRepository


def test_save_assigns_an_id_to_the_customer(db_connection):
    repository = CustomerRepository(db_connection)
    customer = Customer(full_name="Maria Silva", address="Rua A, 123", phone_number="11999990000")

    saved_customer = repository.save(customer)

    assert saved_customer.id is not None


def test_find_by_id_returns_the_saved_customer(db_connection):
    repository = CustomerRepository(db_connection)
    saved_customer = repository.save(
        Customer(full_name="João Souza", address="Rua B, 45", phone_number="11988887777")
    )

    found_customer = repository.find_by_id(saved_customer.id)

    assert found_customer == saved_customer


def test_find_by_id_returns_none_when_customer_does_not_exist(db_connection):
    repository = CustomerRepository(db_connection)

    assert repository.find_by_id(999) is None


def test_find_all_lists_customers_ordered_by_name(db_connection):
    repository = CustomerRepository(db_connection)
    repository.save(Customer(full_name="Zeca", address="Rua Z", phone_number="1"))
    repository.save(Customer(full_name="Ana", address="Rua A", phone_number="2"))

    customers = repository.find_all()

    assert [customer.full_name for customer in customers] == ["Ana", "Zeca"]


def test_find_by_partial_name_matches_substring(db_connection):
    repository = CustomerRepository(db_connection)
    repository.save(Customer(full_name="Carlos Andrade", address="Rua C", phone_number="1"))
    repository.save(Customer(full_name="Beatriz Lima", address="Rua B", phone_number="2"))

    customers = repository.find_by_partial_name("andra")

    assert [customer.full_name for customer in customers] == ["Carlos Andrade"]


def test_update_changes_the_stored_customer_data(db_connection):
    repository = CustomerRepository(db_connection)
    saved_customer = repository.save(
        Customer(full_name="Paulo", address="Rua Antiga", phone_number="1")
    )

    saved_customer.address = "Rua Nova"
    repository.update(saved_customer)

    assert repository.find_by_id(saved_customer.id).address == "Rua Nova"


def test_delete_removes_the_customer(db_connection):
    repository = CustomerRepository(db_connection)
    saved_customer = repository.save(Customer(full_name="Rita", address="Rua R", phone_number="1"))

    repository.delete(saved_customer.id)

    assert repository.find_by_id(saved_customer.id) is None
