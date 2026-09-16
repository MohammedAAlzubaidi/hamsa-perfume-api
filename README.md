# Hamsa Perfume Orders API

مشروع تجريبي بسيط لربط Hamsa Voice Agent مع API للطلبات.

## الوظائف

- إنشاء طلب جديد
- متابعة حالة الطلب
- إلغاء الطلب
- عرض المنتجات
- تحديث حالة الطلب للاختبار

## المنتجات

| product_id | المنتج |
|---|---|
| 1 | عطر المسك |
| 2 | عطر الورد |
| 3 | عطر العود |

## تشغيل المشروع محليًا

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

بعدها افتح:

```text
http://127.0.0.1:8000/docs
```

راح تظهر لك Swagger UI وتقدر تجرب كل API من المتصفح.

## رفع المشروع على Render

1. ارفع ملفات المشروع إلى GitHub.
2. افتح Render وأنشئ Web Service جديد.
3. اختر Repository حق المشروع.
4. استخدم:

Build Command:

```text
pip install -r requirements.txt
```

Start Command:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

5. بعد Deploy راح يعطيك Render رابط مثل:

```text
https://your-service-name.onrender.com
```

## أهم الروابط بعد الرفع

### فحص الـAPI

```text
GET /health
```

### قائمة المنتجات

```text
GET /products
```

### متابعة طلب

```text
GET /orders/1
```

يوجد 3 طلبات تجريبية يتم إنشاؤها أول مرة تلقائيًا.

### إنشاء طلب

```text
POST /orders
```

Body:

```json
{
  "customer_name": "Fahad",
  "phone": "0501234567",
  "address": "Riyadh",
  "product_id": "1",
  "quantity": 2
}
```

### إلغاء طلب

```text
DELETE /orders/1
```

### تحديث حالة الطلب للاختبار

```text
PATCH /orders/1/status
```

Body:

```json
{
  "status": "تم الشحن"
}
```

الحالات المسموحة:

- تم استلام الطلب
- قيد التجهيز
- تم الشحن
- تم التوصيل
- تم الإلغاء

## ربطه مع Hamsa

### Tool 1: Track Order

Method:

```text
GET
```

URL:

```text
https://YOUR-RENDER-URL.onrender.com/orders/{order_id}
```

Input:

```text
order_id
```

### Tool 2: Create Order

Method:

```text
POST
```

URL:

```text
https://YOUR-RENDER-URL.onrender.com/orders
```

Body Example:

```json
{
  "customer_name": "Fahad",
  "phone": "0501234567",
  "address": "Riyadh",
  "product_id": "1",
  "quantity": 2
}
```

### Tool 3: Cancel Order

Method:

```text
DELETE
```

URL:

```text
https://YOUR-RENDER-URL.onrender.com/orders/{order_id}
```

## ملاحظة مهمة

هذا مشروع تجريبي للتعلم. قاعدة البيانات SQLite موجودة داخل السيرفر نفسه.
بعض خدمات الاستضافة قد تعيد تهيئة التخزين عند إعادة تشغيل الخدمة، لذلك للإنتاج الفعلي استخدم قاعدة بيانات دائمة مثل PostgreSQL.
