from datetime import datetime
query_brand = """
    INSERT INTO brand (brand_name,country,created_at)
    VALUES(%s, %s, %s)
    ON CONFLICT (brand_name) DO NOTHING
    RETURNING brand_id;
"""
query_category = """
    INSERT INTO category (category_name, level, parent_category_id,created_at)
    VALUES(%s, %s, %s, %s)
    ON CONFLICT (category_name) DO NOTHING
"""

query_seller = """
    INSERT INTO seller (seller_name,join_date,seller_type,rating,country)
    VALUES(%s, %s, %s,%s,%s)
    RETURNING seller_id;
"""

query_customer ="""
    INSERT INTO customer (customer_name, email, phone, gender, address, city, created_at)
    VALUES (%s,%s,%s,%s,%s,%s,%s);
"""
#  ON CONFLICT (email, phone) DO NOTHING;
query_product = """
    INSERT INTO product (
        sku, product_name, category_id, brand_id, seller_id,
        price, stock_qty, rating, is_active, created_at, created_by,
        updated_at, updated_by, is_deleted, deleted_at, deleted_by
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

query_promotion = """
    INSERT INTO promotion (
        promotion_name, promotion_type, discount_type, discount_value,
        start_date, end_date, created_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

query_promotion_product = """
    INSERT INTO promotion_product (promotion_id, product_id, created_at)
    VALUES (%s, %s, %s)
    ON CONFLICT (promotion_id, product_id) DO NOTHING;
"""

query_select_brand_id = """SELECT brand_id FROM brand;"""
query_select_sub_category_id = """SELECT category_id FROM category WHERE level = 2;"""
query_select_seller_id = """SELECT seller_id FROM seller;"""
query_select_product_id="SELECT product_id FROM product;"
query_select_promotion_id = "SELECT promotion_id FROM promotion;"
query_select_promotion_product_id = "SELECT promo_product_id FROM promotion_product;"
query_truncate_all = """
    TRUNCATE TABLE 
        promotion_product,
        promotion,
        product,
        customer,
        seller,
        category,
        brand
    RESTART IDENTITY CASCADE;
"""

startDate = datetime(2024,1,1)
endDate = datetime(2024,12,31)

categories_tree = {
        'Điện tử & Công nghệ': [
            "Điện thoại thông minh", "Laptop & Máy tính", "Tai nghe không dây", "Đồng hồ thông minh"
        ],
        'Thời trang & Phụ kiện': [
            "Áo sơ mi nam", "Quần jean nữ", "Giày thể thao", "Túi xách thời trang"
        ],
        'Nhà cửa & Đời sống': [
            "Bàn ghế phòng khách", "Nồi chiên không dầu", "Chăn ga gối nệm", "Đèn trang trí"
        ],
        'Sắc đẹp & Sức khỏe': [
            "Kem chống nắng", "Son môi cao cấp", "Nước hoa chính hãng", "Sữa rửa mặt"
        ],
        'Sách & Văn phòng phẩm': [
            "Sách Kỹ năng sống", "Sách Kinh tế", "Sách Lập trình CNTT", "Bút viết & Vở ghi"
        ]
    }

