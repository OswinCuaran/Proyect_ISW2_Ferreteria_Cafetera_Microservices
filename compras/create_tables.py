import time
from sqlalchemy import text
from database import engine

TABLES = [
    """
    CREATE TABLE IF NOT EXISTS purchase_orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        number VARCHAR(20) NOT NULL UNIQUE,
        supplier_id INT NOT NULL,
        destination_warehouse_id INT NOT NULL,
        user_id BIGINT NOT NULL,
        status ENUM('BORRADOR', 'ENVIADA', 'RECIBIDA_PARCIAL', 'RECIBIDA', 'CANCELADA') NOT NULL DEFAULT 'BORRADOR',
        issue_date DATE NOT NULL,
        expected_date DATE NULL,
        notes VARCHAR(255) NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS purchase_order_items (
        order_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity_ordered DECIMAL(12,3) NOT NULL,
        unit_price DECIMAL(14,2) NOT NULL,
        PRIMARY KEY (order_id, product_id),
        FOREIGN KEY (order_id) REFERENCES purchase_orders(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS receptions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT NOT NULL,
        user_id BIGINT NOT NULL,
        notes VARCHAR(255) NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES purchase_orders(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS reception_items (
        reception_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity_received DECIMAL(12,3) NOT NULL,
        PRIMARY KEY (reception_id, product_id),
        FOREIGN KEY (reception_id) REFERENCES receptions(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS product_returns (
        id INT AUTO_INCREMENT PRIMARY KEY,
        type ENUM('CLIENTE', 'PROVEEDOR') NOT NULL,
        order_id INT NULL,
        warehouse_id INT NOT NULL,
        sale_reference VARCHAR(50) NULL,
        reason VARCHAR(255) NOT NULL,
        user_id BIGINT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES purchase_orders(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS product_return_items (
        return_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity DECIMAL(12,3) NOT NULL,
        product_condition ENUM('BUEN_ESTADO', 'DEFECTUOSO') NOT NULL,
        PRIMARY KEY (return_id, product_id),
        FOREIGN KEY (return_id) REFERENCES product_returns(id)
    )
    """,
]

def create_tables():
    for attempt in range(1, 11):
        try:
            with engine.begin() as connection:
                for sql in TABLES:
                    connection.execute(text(sql))
            print("Conexión exitosa. Las tablas de compras_db están listas.")
            return
        except Exception as error:
            print(f"Intento {attempt}: no se pudo conectar o crear las tablas ({error})")
            time.sleep(3)
    raise SystemExit("No se pudieron crear las tablas de compras_db")

if __name__ == "__main__":
    create_tables()
