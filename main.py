from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import sqlite3
from pathlib import Path

app = FastAPI(
    title="Hamsa Perfume Orders API",
    description="Simple demo API for Hamsa voice agent: create, track, and cancel perfume orders.",
    version="1.0.0",
)

DB_PATH = Path(__file__).with_name("orders.db")

PRODUCTS = {
    "1": {"id": "1", "name_ar": "عطر المسك", "name_en": "Musk Perfume", "price": 120.0},
    "2": {"id": "2", "name_ar": "عطر الورد", "name_en": "Rose Perfume", "price": 110.0},
    "3": {"id": "3", "name_ar": "عطر العود", "name_en": "Oud Perfume", "price": 180.0},
}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'تم استلام الطلب'
        )
        """
    )

    cur.execute("SELECT COUNT(*) AS count FROM orders")
    count = cur.fetchone()["count"]

    if count == 0:
        sample_orders = [
            ("أحمد", "0500000001", "الرياض", "1", "عطر المسك", 1, "قيد التجهيز"),
            ("محمد", "0500000002", "جدة", "3", "عطر العود", 2, "تم الشحن"),
            ("سارة", "0500000003", "الدمام", "2", "عطر الورد", 1, "تم التوصيل"),
        ]
        cur.executemany(
            """
            INSERT INTO orders
            (customer_name, phone, address, product_id, product_name, quantity, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            sample_orders,
        )

    conn.commit()
    conn.close()


@app.on_event("startup")
def startup_event():
    init_db()


class CreateOrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=5)
    address: str = Field(..., min_length=2)
    product_id: str
    quantity: int = Field(..., ge=1, le=20)


class UpdateStatusRequest(BaseModel):
    status: str


@app.get("/")
def root():
    return {
        "success": True,
        "message": "Hamsa Perfume Orders API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"success": True, "status": "ok"}


@app.get("/products")
def get_products():
    return {
        "success": True,
        "products": list(PRODUCTS.values()),
    }


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "success": True,
        "order": dict(row),
    }


@app.post("/orders")
def create_order(data: CreateOrderRequest):
    product = PRODUCTS.get(data.product_id)
    if not product:
        raise HTTPException(status_code=400, detail="Invalid product_id. Use 1, 2, or 3.")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO orders
        (customer_name, phone, address, product_id, product_name, quantity, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.customer_name,
            data.phone,
            data.address,
            data.product_id,
            product["name_ar"],
            data.quantity,
            "تم استلام الطلب",
        ),
    )
    order_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "تم إنشاء الطلب بنجاح",
        "order_id": order_id,
        "product": product["name_ar"],
        "quantity": data.quantity,
        "status": "تم استلام الطلب",
    }


@app.delete("/orders/{order_id}")
def cancel_order(order_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    if row["status"] == "تم الإلغاء":
        conn.close()
        return {
            "success": True,
            "message": "الطلب ملغي مسبقًا",
            "order_id": order_id,
            "status": "تم الإلغاء",
        }

    if row["status"] == "تم التوصيل":
        conn.close()
        raise HTTPException(status_code=400, detail="Delivered order cannot be cancelled")

    cur.execute(
        "UPDATE orders SET status = ? WHERE order_id = ?",
        ("تم الإلغاء", order_id),
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "تم إلغاء الطلب بنجاح",
        "order_id": order_id,
        "status": "تم الإلغاء",
    }


@app.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, data: UpdateStatusRequest):
    allowed = {
        "تم استلام الطلب",
        "قيد التجهيز",
        "تم الشحن",
        "تم التوصيل",
        "تم الإلغاء",
    }

    if data.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values: {sorted(allowed)}",
        )

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT order_id FROM orders WHERE order_id = ?", (order_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    cur.execute(
        "UPDATE orders SET status = ? WHERE order_id = ?",
        (data.status, order_id),
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "order_id": order_id,
        "status": data.status,
    }
