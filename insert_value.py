from datetime import timedelta
from variable import (
    startDate, endDate,
    # Brand & Seller
    query_brand, query_select_brand_id,
    query_seller, query_select_seller_id,
    # Category & Customer
    query_category, query_select_sub_category_id,query_select_main_category_id_name,
    query_customer,query_select_customer_id,
    # Product
    query_product, query_select_product_id,
    # Promotion & Promotion Product
    query_promotion, query_select_promotion_id,
    query_promotion_product, query_select_promotion_product_id,
    # truncate table
    query_truncate_all,
    # list data for inserting
    categories_tree,
    promotion_names,
    promotion_types,
    discount_types,
    genders,

)

from numpy.ma import count
from datetime import datetime
import psycopg2
from faker import Faker
import numpy as np
from config import load_config
import random
import uuid

fake = Faker(['vi_VN','en_US'])
Faker.seed(42)
random.seed(42)
# Insert query 

def truncate_all_tables(cur):
    cur.execute(query_truncate_all)

def insert_brand(cur, count =20):
    brand_data=[]
    for i in range(count):
        name = fake.company()
        country = fake.country()
        created_at = fake.date_time_between(
            start_date=startDate,
            end_date=endDate
        )
        brand_data.append((name,country,created_at))
    cur.executemany(query_brand,brand_data)
    cur.execute(query_select_brand_id)
    # brand_ids = [r[0] for r in cur.fetchall()]
    # return brand_ids
    result = []
    for r in cur.fetchall():   # r là từng dòng, ví dụ: (1,)
        result.append(r[0])   # r[0] lấy ra số 1 bên trong tuple
    return result

# 5 main + 20 sub-categories   
def insert_category(cur):
    main_cat_data =[]
    # chạy lấy key của category_tree ra để thêm ở level main
    for main_name in categories_tree.keys():
        created_at = fake.date_time_between(start_date=startDate, end_date=endDate)
        main_cat_data.append((main_name,1,None,created_at))
    cur.executemany(query_category,main_cat_data)
    cur.execute(query_select_main_category_id_name)
    # lấy danh sách ID mục cha ra để random gắn cho danh mục con
    main_cat_ids = dict(cur.fetchall())
    # chạy lấy value của list sub_category và gắn cho parent_id
    sub_cat_data=[]
    for main_name,sub_list in categories_tree.items():
        parent_id = main_cat_ids[main_name]

        for sub_name in sub_list:
            created_at= fake.date_time_between(start_date=startDate,end_date=endDate)
            sub_cat_data.append((sub_name,2,parent_id,created_at))
    cur.executemany(query_category,sub_cat_data)

    cur.execute(query_select_sub_category_id)
    sub_cat_ids = [r[0] for r in cur.fetchall()]
    return sub_cat_ids
     
# seller 50 Vietnam-based sellers
def insert_seller(cur,count = 50):
    seller_data=[]
    for i in range(count):
        name = fake.company()
        join_date= fake.date_between(
            start_date=startDate,
            end_date=endDate
        )
        seller_type = random.choice(['Official', 'Marketplace'])
        rating = round(random.uniform(1.0,5.0),1)
        country = "Vietnam"
        seller_data.append((name,join_date,seller_type,rating,country))
    cur.executemany(query_seller,seller_data)
    cur.execute(query_select_seller_id)
    result = []
    for r in cur.fetchall():   # r là từng dòng, ví dụ: (1,)
        result.append(r[0])   # r[0] lấy ra số 1 bên trong tuple
    return result

# customer 30000 ~167 orders/customer over 5 months
def insert_customer(cur,count=30000,batch_size=5000):
    """"""
    customer_data = []
    batch = []
    total_inserted = 0
    for i in range(count):
        gender = random.choice(genders)
        name = fake.name_male() if gender == 'Male' else fake.name_female()
        email = f"user_{i}_{uuid.uuid4().hex[:6]}@gmail.com"
        phone = f"09({i:08d})"
        address = fake.street_address()
        city = fake.city()
        created_at = fake.date_time_between(start_date=startDate, end_date=endDate)
        batch.append((name,email,phone,gender,address,city,created_at))
        if len(batch) >= batch_size:
            cur.executemany(query_customer, batch)
            total_inserted += len(batch)
            print(f"Đã nạp: {total_inserted:,} / {count:,} khách hàng")
            batch = []
    if batch:
        cur.executemany(query_customer, batch)
        total_inserted += len(batch)
        print(f"Đã nạp: {total_inserted:,} / {count:,} khách hàng")
        batch = []

    cur.executemany(query_customer,customer_data)
    cur.execute(query_select_customer_id)
    customer_ids = [r[0] for r in cur.fetchall()]
    return customer_ids
    
# product	3,000	Each linked to seller, category, brand
def insert_product(cur,count=3000,batch_size=1000):
    """"""
    batch = []
    total_insert = 0
    cur.execute(query_select_brand_id)
    brand_ids = [r[0] for r in cur.fetchall()]
    cur.execute(query_select_seller_id)
    seller_ids = [r[0] for r in cur.fetchall()]
    cur.execute(query_select_sub_category_id)
    sub_category_ids = [r[0] for r in cur.fetchall()]
    for i in range(count):
        brand_id = random.choice(brand_ids)
        seller_id = random.choice(seller_ids)
        category_id = random.choice(sub_category_ids)
        name = fake.catch_phrase()
        sku = f"SKU-{uuid.uuid4().hex[:8].upper()}-{i}"
        price = round(random.uniform(100000,50000000),2)
        stock_qty = random.randint(0,500)
        rating = round(random.uniform(3.0, 5.0), 1)
        is_active = random.choice([True,False])
        created_at = fake.date_time_between(start_date=startDate, end_date=endDate)
        created_by = "Admin"
        if random.random() < 0.1:
            updated_at = fake.date_time_between(start_date=created_at, end_date=endDate)
            updated_by = fake.name()
        else:
            updated_at = None
            updated_by = None 
        if random.random() < 0.05:  
            is_deleted = True
            deleted_at = fake.date_time_between(start_date=created_at, end_date=endDate)
            deleted_by = fake.name()
        else:
            is_deleted = False  
            deleted_at = None  
            deleted_by = None
        batch.append((sku, name, category_id, brand_id, seller_id,
        price, stock_qty, rating, is_active, created_at, created_by, updated_at,
        updated_by, is_deleted, deleted_at, deleted_by))
        if len(batch) >= batch_size:
            cur.executemany(query_product,batch)
            total_insert += len(batch)
            print(f"Đã nạp: {total_insert:,} / {count:,} sản phẩm")
            batch = []     
    if batch:
        cur.executemany(query_product,batch)
        total_insert += len(batch)
        print(f"Đã nạp: {total_insert:,} / {count:,} sản phẩm")
        batch = []
    cur.execute(query_select_product_id)
    return [r[0] for r in cur.fetchall()]

# promotion	30	~6 campaigns/month
def insert_promotion(cur,count=30):
    """"""
    
    promotions_data = []
    for i in range(count):
        p_type = random.choice(promotion_types)
        d_type = random.choice(discount_types)
        prefix = f"{random.randint(1,12)}.{random.randint(1,12)}" if random.random() < 0.5 else "Siêu" 
        name = f"{prefix} {random.choice(promotion_names)}"
        if d_type == 'percentage':
            d_value = round(random.choice([5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 50.0, 70.0]),2)
        else:
            d_value = float(random.choice([20000, 50000, 100000, 150000, 200000, 500000]))
        created_at = fake.date_time_between(start_date=startDate, end_date=datetime(2025, 1, 31))
        start_date = fake.date_between(
            start_date=created_at.date(),
            end_date=created_at.date() + timedelta(days=30)
        )
        end_date = start_date + timedelta(days=random.randint(7,45))
        promotions_data.append((name,p_type,d_type,d_value,start_date,end_date,created_at))
    cur.executemany(query_promotion,promotions_data)
    cur.execute(query_select_promotion_id)
    return [r[0] for r in cur.fetchall()]

# promotion_product	500	Each promo applies to ~15 products
def insert_promotion_product(cur,count=500,batch_size=100):
    """"""
    cur.execute(query_select_promotion_id)
    promotion_ids = [r[0] for r in cur.fetchall()]
    
    cur.execute(query_select_product_id)
    product_ids = [r[0] for r in cur.fetchall()]
    if not promotion_ids or not product_ids:
        print("Cần có dữ liệu trong bảng promotion và product trước!")
        return []
    used_pairs = set()
    pairs = []
    while len(pairs) < count:
        for promo_id in promotion_ids:
            if len(pairs) >= count:
                break
            prod_id = random.choice(product_ids)
            if (promo_id, prod_id) not in used_pairs:
                used_pairs.add((promo_id,prod_id))
                pairs.append((promo_id, prod_id))
    batch = []
    total_insert = 0
    for promo_id, prod_id in pairs:
        created_at = fake.date_time_between(
            start_date=startDate,
            end_date=datetime(2025, 5, 31)
        )
        batch.append((promo_id, prod_id, created_at))
        if len(batch) >= batch_size:
            cur.executemany(query_promotion_product, batch)
            total_insert += len(batch)
            print(f"Đã nạp: {total_insert:,} / {count:,} liên kết promotion_product")
            batch = []
            
    if batch:
        cur.executemany(query_promotion_product, batch)
        total_insert += len(batch)
        print(f"Đã nạp: {total_insert:,} / {count:,} liên kết promotion_product")
        batch = []
    cur.execute(query_select_promotion_product_id)
    return [r[0] for r in cur.fetchall()]
    
# order	5,000,000	~1M orders/month, distributed daily
# order_item	17,500,000	Each order has 2–5 items (avg 3.5)


def main():
    config = load_config()
    conn = None
    try:
        conn = psycopg2.connect(**config)
        with conn:
            with conn.cursor() as cur:
                """"""
                truncate_all_tables(cur)
                brand_ids = insert_brand(cur,count=20)
                print("Brand IDs:",brand_ids)

                category_ids = insert_category(cur)
                print("Category IDs:",category_ids)

                seller_ids = insert_seller(cur,count=50)
                print("Seller IDs:",seller_ids)

                customer_ids = insert_customer(cur,count=30000,batch_size=5000)
                print("Customer IDs:",customer_ids)

                product_ids = insert_product(cur,count=3000,batch_size=1000)
                print("Product IDs:",product_ids)

                promotion_ids = insert_promotion(cur,count=30)
                print("Promotion IDs:",promotion_ids)

                promotion_product_ids = insert_promotion_product(cur,count=500,batch_size=100)
                print("Promotion Product IDs:",promotion_product_ids)

    except(Exception,psycopg2.DatabaseError)as error:
        print(error)
    finally:
        if conn is not None:
            cur.close()
            conn.close()

if __name__ == '__main__':
    main()