CREATE TABLE IF NOT EXISTS customer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone_number TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stock_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    quantity_in_stock INTEGER NOT NULL DEFAULT 0,
    unit_price REAL NOT NULL,
    image_path TEXT
);

CREATE TABLE IF NOT EXISTS sale (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    sale_date_time TEXT NOT NULL,
    cancelled_at TEXT,
    FOREIGN KEY (customer_id) REFERENCES customer (id)
);

CREATE TABLE IF NOT EXISTS sold_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    stock_item_id INTEGER NOT NULL,
    quantity_sold INTEGER NOT NULL,
    unit_price_at_sale_time REAL NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sale (id),
    FOREIGN KEY (stock_item_id) REFERENCES stock_item (id)
);
