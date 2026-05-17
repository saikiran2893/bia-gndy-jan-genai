#!/usr/bin/env python3
"""
db.py — Creates and seeds the demo SQLite database for MCP Day 2 Lab
---------------------------------------------------------------------------
Run ONCE before starting the lab:
    python db.py

Creates demo.db with three tables:
    customers   — 10 sample customers
    orders      — 15 sample orders linked to customers
    products    — 8 sample products
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "demo.db"


def setup():
    # Remove existing DB so we always start fresh
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Removed existing {DB_PATH.name}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── Create tables ─────────────────────────────────────────────────────────
    cur.executescript("""
        CREATE TABLE customers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT NOT NULL,
            city        TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'active',
            joined_date TEXT NOT NULL
        );

        CREATE TABLE products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            category    TEXT NOT NULL,
            price       REAL NOT NULL,
            stock       INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            quantity    INTEGER NOT NULL DEFAULT 1,
            total       REAL NOT NULL,
            status      TEXT NOT NULL DEFAULT 'pending',
            order_date  TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id)  REFERENCES products(id)
        );
    """)

    # ── Seed customers ────────────────────────────────────────────────────────
    customers = [
        ("Arjun Sharma",    "arjun@example.com",    "Chennai",   "active",   "2023-01-15"),
        ("Priya Nair",      "priya@example.com",    "Mumbai",    "active",   "2023-03-22"),
        ("Ravi Kumar",      "ravi@example.com",     "Bangalore", "active",   "2023-05-10"),
        ("Sneha Patel",     "sneha@example.com",    "Ahmedabad", "inactive", "2022-11-08"),
        ("Vikram Singh",    "vikram@example.com",   "Delhi",     "active",   "2024-01-02"),
        ("Meena Reddy",     "meena@example.com",    "Hyderabad", "active",   "2023-07-19"),
        ("Anil Verma",      "anil@example.com",     "Pune",      "active",   "2023-09-30"),
        ("Deepa Iyer",      "deepa@example.com",    "Chennai",   "inactive", "2022-06-14"),
        ("Suresh Menon",    "suresh@example.com",   "Kochi",     "active",   "2024-02-28"),
        ("Kavitha Rao",     "kavitha@example.com",  "Mysore",    "active",   "2023-12-05"),
    ]
    cur.executemany(
        "INSERT INTO customers (name, email, city, status, joined_date) VALUES (?,?,?,?,?)",
        customers
    )

    # ── Seed products ─────────────────────────────────────────────────────────
    products = [
        ("MCP Handbook",        "Books",       499.00,  50),
        ("AI Starter Kit",      "Electronics", 2999.00, 20),
        ("Python Course",       "Education",   1499.00, 100),
        ("Laptop Stand",        "Accessories", 899.00,  35),
        ("Mechanical Keyboard", "Electronics", 3499.00, 15),
        ("Notebook Pack",       "Stationery",  199.00,  200),
        ("USB-C Hub",           "Electronics", 1299.00, 40),
        ("Desk Lamp",           "Accessories", 799.00,  25),
    ]
    cur.executemany(
        "INSERT INTO products (name, category, price, stock) VALUES (?,?,?,?)",
        products
    )

    # ── Seed orders ───────────────────────────────────────────────────────────
    orders = [
        (1, 1, 2,  998.00,  "delivered", "2024-01-10"),
        (1, 3, 1, 1499.00,  "delivered", "2024-02-14"),
        (2, 2, 1, 2999.00,  "delivered", "2024-01-25"),
        (2, 5, 1, 3499.00,  "shipped",   "2024-03-01"),
        (3, 4, 2, 1798.00,  "delivered", "2024-02-05"),
        (3, 7, 1, 1299.00,  "pending",   "2024-03-10"),
        (4, 6, 3,  597.00,  "delivered", "2023-12-20"),
        (5, 1, 1,  499.00,  "delivered", "2024-01-30"),
        (5, 3, 1, 1499.00,  "shipped",   "2024-03-05"),
        (6, 8, 1,  799.00,  "pending",   "2024-03-12"),
        (7, 2, 1, 2999.00,  "delivered", "2024-02-20"),
        (7, 4, 1,  899.00,  "delivered", "2024-02-20"),
        (8, 6, 5,  995.00,  "delivered", "2023-11-15"),
        (9, 5, 1, 3499.00,  "shipped",   "2024-03-08"),
        (10,7, 2, 2598.00,  "pending",   "2024-03-11"),
    ]
    cur.executemany(
        "INSERT INTO orders (customer_id, product_id, quantity, total, status, order_date) VALUES (?,?,?,?,?,?)",
        orders
    )

    conn.commit()
    conn.close()

    print(f"✅ Created {DB_PATH.name} with:")
    print(f"   • customers table  — {len(customers)} rows")
    print(f"   • products  table  — {len(products)} rows")
    print(f"   • orders    table  — {len(orders)} rows")
    print()
    print("Next step: run your MCP server")
    print("   python server.py")
    print("   npx @modelcontextprotocol/inspector python server.py")


if __name__ == "__main__":
    setup()
