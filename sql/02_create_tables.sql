-- Create tables script
USE DATABASE ELT_WAREHOUSE;
USE SCHEMA RAW;

CREATE OR REPLACE TABLE customers (

    customer_id INTEGER,

    first_name STRING,

    last_name STRING,

    email STRING,

    phone STRING,

    city STRING,

    country STRING,

    signup_date DATE

);
CREATE OR REPLACE TABLE products (

    product_id INTEGER,

    product_name STRING,

    category STRING,

    brand STRING,

    price NUMBER(10,2),

    stock INTEGER

);
CREATE OR REPLACE TABLE orders (

    order_id INTEGER,

    customer_id INTEGER,

    order_date DATE,

    status STRING,

    payment_method STRING

);
CREATE OR REPLACE TABLE order_items (

    order_item_id INTEGER,

    order_id INTEGER,

    product_id INTEGER,

    quantity INTEGER,

    unit_price NUMBER(10,2),

    discount_percent NUMBER(5,2),

    line_total NUMBER(10,2)

);