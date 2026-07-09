# Data Generation Spec

## Overview
Generate synthetic e-commerce datasets for raw input files.

## Scope
- customers.csv
- products.csv
- orders.csv
- order_items.csv

## Requirements
- realistic customer demographics and locations
- product categories and brands
- order dates spanning the last 24 months
- each order contains 1-5 order items
- quantity, price, discount, and line totals

## Outputs
- `data/raw/customers.csv`
- `data/raw/products.csv`
- `data/raw/orders.csv`
- `data/raw/order_items.csv`
