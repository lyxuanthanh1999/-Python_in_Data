import psycopg2
from config import load_config

def create_tables():
    config = load_config()
    commands = (
        """
       CREATE TABLE brand (
        brand_id SERIAL PRIMARY KEY,
        brand_name VARCHAR(100) NOT NULL UNIQUE,
        country VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )

    """,
    """
        CREATE TABLE category (
            category_id SERIAL PRIMARY KEY,
            category_name VARCHAR(100) NOT NULL UNIQUE,
            parent_category_id INT,
            level SMALLINT NOT NULL CHECK (level IN(1,2)),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_parent_category_id
                FOREIGN KEY (parent_category_id)
                REFERENCES category (category_id)
                ON DELETE SET NULL
        )
    """,
    """
        CREATE TABLE seller (
            seller_id SERIAL PRIMARY KEY,
            seller_name VARCHAR(150),
            join_date DATE,
            seller_type VARCHAR(50),
            rating DECIMAL(2,1),
            country VARCHAR(50),
            CONSTRAINT ck_seller_type CHECK(seller_type IN ('Official', 'Marketplace')),
            CONSTRAINT ck_rating CHECK (rating >= 0 AND rating <= 5)
        )
    """,
    """
        CREATE TABLE customer (	
            customer_id SERIAL PRIMARY KEY,
            customer_name VARCHAR(150) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            phone VARCHAR(20) UNIQUE,
            gender VARCHAR(10),
            address VARCHAR(255),
            city VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT ck_gender CHECK(gender IN ('Male', 'Female'))
        )
    """,
    """
        CREATE TABLE product (
            product_id SERIAL PRIMARY KEY,

            sku VARCHAR(64) UNIQUE NOT NULL,
            product_name VARCHAR(200) NOT NULL,
            category_id INT NOT NULL,
            brand_id INT NOT NULL,
            seller_id INT NOT NULL,
            price DECIMAL(12,2) NOT NULL,
            stock_qty INT NOT NULL DEFAULT 0,
            rating DECIMAL(2,1) DEFAULT 5.0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            created_by VARCHAR(150) NOT NULL,
            updated_at TIMESTAMP,
            updated_by VARCHAR(150),
            is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
            deleted_at TIMESTAMP,
            deleted_by VARCHAR(150),
        
            CONSTRAINT fk_category_id
                FOREIGN KEY (category_id)
                REFERENCES category (category_id)
                ON DELETE RESTRICT,
            CONSTRAINT fk_brand_id
                FOREIGN KEY (brand_id)
                REFERENCES brand (brand_id)
                ON DELETE RESTRICT,
            CONSTRAINT fk_seller_id
                FOREIGN KEY (seller_id)
                REFERENCES seller (seller_id)
                ON DELETE RESTRICT,
            CONSTRAINT ck_price CHECK (price > 0),
            CONSTRAINT ck_rating CHECK ( rating >= 0 AND rating <= 5 ),
            CONSTRAINT ck_stock_qty CHECK ( stock_qty >= 0 )
        )
    """,
    """
        CREATE TABLE orders(
            order_id SERIAL PRIMARY KEY,
            customer_id INT NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) NOT NULL,
            total_amount DECIMAL(12,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT ck_total_amount CHECK(total_amount >= 0),
            CONSTRAINT ck_created_at CHECK(created_at >= order_date),
            CONSTRAINT ck_status CHECK(status IN ('PLACED','PAID','SHIPPED','DELIVERED','CANCELLED','RETURNED')),
            CONSTRAINT fk_customer_id
                FOREIGN KEY (customer_id)
                REFERENCES customer (customer_id)
			ON DELETE RESTRICT
        )
    """,
    """
        CREATE TABLE order_item(
            order_item_id BIGSERIAL PRIMARY KEY,
            order_id INT NOT NULL,
            product_id INT NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            quantity INT NOT NULL,
            unit_price DECIMAL(12,2) NOT NULL,
            subtotal DECIMAL(12,2) NOT NULL,
	        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	
            CONSTRAINT fk_order_id
                FOREIGN KEY (order_id)
                REFERENCES orders (order_id)
                ON DELETE RESTRICT,
	        CONSTRAINT fk_product_id
		        FOREIGN KEY (product_id)
		        REFERENCES product(product_id)
		        ON DELETE RESTRICT,

	        CONSTRAINT ck_quantity CHECK (quantity > 0),
            CONSTRAINT ck_unit_price CHECK (unit_price > 0),
	        CONSTRAINT ck_subtotal CHECK (subtotal = quantity * unit_price),
	        CONSTRAINT ck_created_at CHECK (created_at >= order_date)
    )
    """,
    """
        CREATE TABLE promotion(
            promotion_id SERIAL PRIMARY KEY,
            promotion_name VARCHAR(100) NOT NULL,
            promotion_type VARCHAR(50) NOT NULL,
            discount_type VARCHAR(20) NOT NULL,
            discount_value NUMERIC(10,2) NOT NULL,
            start_date DATE,
            end_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT ck_discount_type CHECK (discount_type IN ('percentage','fixed_amount')),
            CONSTRAINT ck_discount_value CHECK (discount_value > 0 AND (discount_type = 'fixed_amount' OR discount_value <= 100)),
            CONSTRAINT ck_start_date CHECK (start_date >= DATE(created_at)),
            CONSTRAINT ck_end_date CHECK (end_date >= start_date)
	
        )
    """,
    """
        CREATE TABLE promotion_product(
            promo_product_id SERIAL PRIMARY KEY,
            promotion_id INT NOT NULL,
            product_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT uq_promotion_id_product_id UNIQUE(promotion_id, product_id),
	        CONSTRAINT fk_promotion_id
                FOREIGN KEY(promotion_id)
                REFERENCES promotion(promotion_id)
                ON DELETE RESTRICT,
	        CONSTRAINT fk_product_id
	            FOREIGN KEY(product_id)
	            REFERENCES product(product_id)
	            ON DELETE RESTRICT
        )
    """,
    )
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                for command in commands:
                    cur.execute(command)
                
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed')
    
if __name__ == '__main__':
    create_tables()