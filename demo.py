import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
import psycopg2
from psycopg2.extras import execute_values
from config import load_config

# Khởi tạo Faker hỗ trợ tiếng Việt
fake = Faker(['vi_VN', 'en_US'])
Faker.seed(42)
random.seed(42)


# ==========================================
# 1. BẢNG BRAND (20 rows)
# ==========================================
def insert_brands(cur, count=20):
    print(f"-> Đang chèn {count} brands...")
    sample_brands = [
        "Apple", "Samsung", "Sony", "LG", "Xiaomi", "Asus", "Dell", "HP",
        "Nike", "Adidas", "Uniqlo", "Zara", "Panasonic", "Philips", "Casio",
        "Logitech", "Anker", "Oppo", "Vivo", "Lenovo"
    ]
    # Nếu cần nhiều hơn 20 thì random thêm
    brands_data = []
    for i in range(count):
        name = sample_brands[i] if i < len(sample_brands) else f"{fake.company()} {i}"
        country = fake.country()
        brands_data.append((name, country))

    query = """
        INSERT INTO brand (brand_name, country)
        VALUES %s
        ON CONFLICT (brand_name) DO NOTHING
        RETURNING brand_id;
    """
    execute_values(cur, query, brands_data)
    cur.execute("SELECT brand_id FROM brand;")
    brand_ids = [r[0] for r in cur.fetchall()]
    return brand_ids


# ==========================================
# 2. BẢNG CATEGORY (25 rows: 5 cha + 20 con)
# ==========================================
def insert_categories(cur):
    print("-> Đang chèn 25 categories (5 main + 20 sub)...")
    main_categories = [
        ("Điện tử & Công nghệ", 1, None),
        ("Thời trang & Phụ kiện", 1, None),
        ("Nhà cửa & Đời sống", 1, None),
        ("Sắc đẹp & Sức khỏe", 1, None),
        ("Sách & Văn phòng phẩm", 1, None)
    ]
    
    # Chèn 5 danh mục chính (Level 1)
    insert_query = """
        INSERT INTO category (category_name, level, parent_category_id)
        VALUES (%s, %s, %s) RETURNING category_id, category_name;
    """
    main_cat_map = {}
    for name, level, parent in main_categories:
        cur.execute(insert_query, (name, level, parent))
        cat_id = cur.fetchone()[0]
        main_cat_map[name] = cat_id

    # 20 danh mục con (Level 2), mỗi danh mục chính có 4 con
    sub_categories = [
        # Điện tử (Main 1)
        ("Điện thoại & Tablet", 2, main_cat_map["Điện tử & Công nghệ"]),
        ("Laptop & Máy tính bàn", 2, main_cat_map["Điện tử & Công nghệ"]),
        ("Tai nghe & Âm thanh", 2, main_cat_map["Điện tử & Công nghệ"]),
        ("Đồng hồ thông minh", 2, main_cat_map["Điện tử & Công nghệ"]),
        # Thời trang (Main 2)
        ("Áo thun & Áo sơ mi", 2, main_cat_map["Thời trang & Phụ kiện"]),
        ("Quần jean & Kaki", 2, main_cat_map["Thời trang & Phụ kiện"]),
        ("Giày thể thao", 2, main_cat_map["Thời trang & Phụ kiện"]),
        ("Túi xách & Balo", 2, main_cat_map["Thời trang & Phụ kiện"]),
        # Nhà cửa (Main 3)
        ("Nội thất phòng khách", 2, main_cat_map["Nhà cửa & Đời sống"]),
        ("Dụng cụ nhà bếp", 2, main_cat_map["Nhà cửa & Đời sống"]),
        ("Chăn ga gối đệm", 2, main_cat_map["Nhà cửa & Đời sống"]),
        ("Đèn trang trí", 2, main_cat_map["Nhà cửa & Đời sống"]),
        # Sắc đẹp (Main 4)
        ("Chăm sóc da mặt", 2, main_cat_map["Sắc đẹp & Sức khỏe"]),
        ("Son môi & Trang điểm", 2, main_cat_map["Sắc đẹp & Sức khỏe"]),
        ("Nước hoa chính hãng", 2, main_cat_map["Sắc đẹp & Sức khỏe"]),
        ("Thực phẩm chức năng", 2, main_cat_map["Sắc đẹp & Sức khỏe"]),
        # Sách (Main 5)
        ("Sách Kỹ năng sống", 2, main_cat_map["Sách & Văn phòng phẩm"]),
        ("Sách Kinh tế & Quản trị", 2, main_cat_map["Sách & Văn phòng phẩm"]),
        ("Sách Lập trình & CNTT", 2, main_cat_map["Sách & Văn phòng phẩm"]),
        ("Văn phòng phẩm & Bút viết", 2, main_cat_map["Sách & Văn phòng phẩm"])
    ]

    execute_values(cur, """
        INSERT INTO category (category_name, level, parent_category_id)
        VALUES %s;
    """, sub_categories)

    # Lấy danh sách category con để sau này gắn sản phẩm vào
    cur.execute("SELECT category_id FROM category WHERE level = 2;")
    sub_category_ids = [r[0] for r in cur.fetchall()]
    return sub_category_ids


# ==========================================
# 3. BẢNG SELLER (50 rows)
# ==========================================
def insert_sellers(cur, count=50):
    print(f"-> Đang chèn {count} sellers (Vietnam-based)...")
    sellers_data = []
    seller_types = ['Official', 'Marketplace']
    
    for _ in range(count):
        name = f"{fake.company()} Store"
        join_date = fake.date_between(start_date='-3y', end_date='today')
        s_type = random.choice(seller_types)
        rating = round(random.uniform(3.5, 5.0), 1)
        country = 'Vietnam'
        sellers_data.append((name, join_date, s_type, rating, country))

    query = """
        INSERT INTO seller (seller_name, join_date, seller_type, rating, country)
        VALUES %s RETURNING seller_id;
    """
    execute_values(cur, query, sellers_data)
    cur.execute("SELECT seller_id FROM seller;")
    return [r[0] for r in cur.fetchall()]


# ==========================================
# 4. BẢNG CUSTOMER (30,000 rows)
# ==========================================
def insert_customers(cur, count=30000):
    print(f"-> Đang chèn {count:,} customers (tối ưu tốc độ cao)...")
    customers_data = []
    genders = ['Male', 'Female']
    
    for i in range(count):
        gender = random.choice(genders)
        name = fake.name_male() if gender == 'Male' else fake.name_female()
        # Đảm bảo email và phone luôn là duy nhất (UNIQUE)
        email = f"user_{i}_{uuid.uuid4().hex[:6]}@gmail.com"
        phone = f"09{i:08d}"  # Tạo chuỗi 10 chữ số không bao giờ trùng lặp
        address = fake.street_address()
        city = fake.city()
        customers_data.append((name, email, phone, gender, address, city))

    query = """
        INSERT INTO customer (customer_name, email, phone, gender, address, city)
        VALUES %s;
    """
    # Batch size 5,000 rows / lần
    execute_values(cur, query, customers_data, page_size=5000)
    print(f"   ✓ Đã chèn xong {count:,} khách hàng.")


# ==========================================
# 5. BẢNG PRODUCT (3,000 rows)
# ==========================================
def insert_products(cur, brand_ids, category_ids, seller_ids, count=3000):
    print(f"-> Đang chèn {count:,} products...")
    products_data = []
    
    for i in range(count):
        sku = f"SKU-{uuid.uuid4().hex[:8].upper()}-{i}"
        name = f"Sản phẩm {fake.word().capitalize()} {fake.color_name()} {i+1}"
        category_id = random.choice(category_ids)
        brand_id = random.choice(brand_ids)
        seller_id = random.choice(seller_ids)
        price = round(random.uniform(50000, 35000000), 2)
        stock_qty = random.randint(0, 500)
        rating = round(random.uniform(3.0, 5.0), 1)
        is_active = True
        created_by = "System_Init"

        products_data.append((
            sku, name, category_id, brand_id, seller_id,
            price, stock_qty, rating, is_active, created_by
        ))

    query = """
        INSERT INTO product (
            sku, product_name, category_id, brand_id, seller_id,
            price, stock_qty, rating, is_active, created_by
        ) VALUES %s;
    """
    execute_values(cur, query, products_data, page_size=1000)
    cur.execute("SELECT product_id FROM product;")
    return [r[0] for r in cur.fetchall()]


# ==========================================
# 6. BẢNG PROMOTION (30 rows)
# ==========================================
def insert_promotions(cur, count=30):
    print(f"-> Đang chèn {count} promotions...")
    promos_data = []
    promo_types = ['Flash Sale', 'Mega Sale', 'Khuyến mãi hè', 'Tết Nguyên Đán', 'Black Friday']
    
    for i in range(count):
        name = f"Campaign {random.choice(promo_types)} #{i+1}"
        p_type = random.choice(promo_types)
        discount_type = random.choice(['percentage', 'fixed_amount'])
        
        if discount_type == 'percentage':
            discount_value = round(random.uniform(5, 50), 2)  # 5% -> 50%
        else:
            discount_value = round(random.uniform(20000, 500000), 2)  # Giảm 20k -> 500k
            
        start_date = fake.date_between(start_date='-2m', end_date='+2m')
        end_date = start_date + timedelta(days=random.randint(3, 15))
        
        promos_data.append((name, p_type, discount_type, discount_value, start_date, end_date))

    query = """
        INSERT INTO promotion (
            promotion_name, promotion_type, discount_type, discount_value, start_date, end_date
        ) VALUES %s;
    """
    execute_values(cur, query, promos_data)
    cur.execute("SELECT promotion_id FROM promotion;")
    return [r[0] for r in cur.fetchall()]


# ==========================================
# 7. BẢNG PROMOTION_PRODUCT (500 rows)
# ==========================================
def insert_promotion_products(cur, promo_ids, product_ids, target_count=500):
    print(f"-> Đang chèn {target_count} promotion_products (mỗi promo ~15 products)...")
    
    # Dùng set để đảm bảo không trùng cặp (promotion_id, product_id)
    unique_pairs = set()
    
    # Mỗi promotion chọn ngẫu nhiên khoảng 15-20 products
    for promo_id in promo_ids:
        sample_size = min(len(product_ids), random.randint(14, 18))
        chosen_products = random.sample(product_ids, sample_size)
        for prod_id in chosen_products:
            unique_pairs.add((promo_id, prod_id))
            if len(unique_pairs) >= target_count:
                break
        if len(unique_pairs) >= target_count:
            break

    # Nếu chưa đủ 500 thì random bổ sung
    while len(unique_pairs) < target_count:
        p_id = random.choice(promo_ids)
        pr_id = random.choice(product_ids)
        unique_pairs.add((p_id, pr_id))

    pairs_data = list(unique_pairs)
    query = """
        INSERT INTO promotion_product (promotion_id, product_id)
        VALUES %s
        ON CONFLICT (promotion_id, product_id) DO NOTHING;
    """
    execute_values(cur, query, pairs_data)
    print(f"   ✓ Đã gán thành công {len(pairs_data)} sản phẩm vào các chương trình khuyến mãi.")


# ==========================================
# HÀM CHÍNH (MAIN ORCHESTRATOR)
# ==========================================
def main():
    config = load_config()
    conn = None
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**config)
        
        with conn:
            with conn.cursor() as cur:
                # 1. Brands
                brand_ids = insert_brands(cur, count=20)
                
                # 2. Categories
                sub_category_ids = insert_categories(cur)
                
                # 3. Sellers
                seller_ids = insert_sellers(cur, count=50)
                
                # 4. Customers
                insert_customers(cur, count=30000)
                
                # 5. Products
                product_ids = insert_products(cur, brand_ids, sub_category_ids, seller_ids, count=3000)
                
                # 6. Promotions
                promo_ids = insert_promotions(cur, count=30)
                
                # 7. Promotion Products
                insert_promotion_products(cur, promo_ids, product_ids, target_count=500)
                
        print("\n🎉 HOÀN TẤT TẤT CẢ DỮ LIỆU MOCK DATA THÀNH CÔNG!")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH NẠP DATA: {error}")
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")


if __name__ == '__main__':
    main()
