CREATE DATABASE IF NOT EXISTS sm_mall;
USE sm_mall;

CREATE TABLE customers (
  customer_id INT,
  first_name VARCHAR(45),
  last_name VARCHAR(45),
  store_id INT,
  PRIMARY KEY (customer_id)
);

CREATE TABLE stores (
  store_id INT AUTO_INCREMENT,
  store_name VARCHAR(45),
  category VARCHAR(45),
  PRIMARY KEY (store_id)
);

CREATE TABLE products (
  product_id INT AUTO_INCREMENT,
  product_name VARCHAR(45),
  price DECIMAL(10,2),
  store_id VARCHAR(45),
  PRIMARY KEY (product_id)
);
