from variable import query_select_promotion_id
from variable import query_select_promotion_product_id
from variable import query_select_product_id
from variable import query_select_customer_id
from variable import query_select_seller_id
from variable import query_select_sub_category_id
from variable import query_select_main_category_id_name
from variable import query_select_brand_id
from config_engine import get_engine
import pandas as pd
from sqlalchemy import  text
from faker import Faker
import random
import uuid
from datetime import datetime, timedelta
from variable import (
    VN_PREFIXES,unique_suffixes,
    startDate, endDate,
    categories_tree, promotion_names, promotion_types, discount_types, genders,
    query_truncate_all
)
fake = Faker(['vi_VN', 'en_US'])
Faker.seed(42)
random.seed(42)
engine = get_engine()

def truncate_all_tables():
    with engine.begin() as conn:
        conn.execute(text(query_truncate_all))
        print("Đã làm sạch toàn bộ database!\n")

def insert_brand(count=20):
    brands = []
    for _ in range(count):
        brands.append({
            'brand_name': fake.company(),
            'country': fake.country(),
            'created_at': fake.date_time_between(start_date=startDate, end_date=endDate)
        })
    df = pd.DataFrame(brands)
    df.to_sql('brand',con=engine,if_exists='append',index=False)
    return pd.read_sql(query_select_brand_id,con=engine)['brand_id'].tolist()


def insert_category():
    main_cats = [{
        'category_name': name,
        'level': 1,
        'parent_category_id': None,
        'created_at': fake.date_time_between(start_date=startDate, end_date=endDate)
    } for name in categories_tree.keys()]

    pd.DataFrame(main_cats).to_sql('category', con=engine, if_exists='append', index=False)
    df_main = pd.read_sql(query_select_main_category_id_name,con=engine)
    main_cat_ids = dict(zip(df_main['category_name'],df_main['category_id']))
    sub_cats = []
    for main_name, sub_list in categories_tree.items():
        parent_id = main_cat_ids[main_name]
        for sub_name in sub_list:
            sub_cats.append({
                'category_name': sub_name,
                'level': 2,
                'parent_category_id': parent_id,
                'created_at': fake.date_time_between(start_date=startDate, end_date=endDate)
            })
    pd.DataFrame(sub_cats).to_sql('category',con=engine,if_exists='append',index=False)
    return pd.read_sql(query_select_sub_category_id, con=engine)['category_id'].tolist()

def insert_seller(count=50):
    sellers = [{
        'seller_name': fake.company(),
        'join_date': fake.date_between(start_date=startDate, end_date=endDate),
        'seller_type': random.choice(['Official', 'Marketplace']),
        'rating': round(random.uniform(1.0, 5.0), 1),
        'country': 'Vietnam'
    } for _ in range(count)]
    pd.DataFrame(sellers).to_sql('seller',con=engine,if_exists='append',index=False)
    return pd.read_sql(query_select_seller_id,con=engine)['seller_id'].tolist()

def insert_customer(count=30000, batch_size=5000):
    customers = []
    for i in range(count):
        gender = random.choice(genders)
        name = fake.name_male() if gender == 'Male' else fake.name_female()
        customers.append({
            'customer_name': name,
            'email': f"user_{i}_{uuid.uuid4().hex[:6]}@gmail.com",
            'phone': f"{random.choice(VN_PREFIXES)}{unique_suffixes[i]}",
            'gender': gender,
            'address': fake.street_address(),
            'city': fake.city(),
            'created_at': fake.date_time_between(start_date=startDate, end_date=endDate)
        })
    df = pd.DataFrame(customers)
    df.to_sql('customer', con=engine, if_exists='append', index=False, chunksize=batch_size)
    return pd.read_sql(query_select_customer_id, con=engine)['customer_id'].tolist()

def insert_product(count=3000, batch_size=1000):
    brand_ids = pd.read_sql(query_select_brand_id,con=engine)['brand_id'].tolist()
    seller_ids = pd.read_sql(query_select_seller_id, con=engine)['seller_id'].tolist()
    sub_category_ids = pd.read_sql(query_select_sub_category_id, con=engine)['category_id'].tolist()
    products = []
    for i in range(count):
        created_at = fake.date_time_between(start_date=startDate, end_date=endDate)
        
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

        products.append({
            'sku': f"SKU-{uuid.uuid4().hex[:8].upper()}-{i}",
            'product_name': fake.catch_phrase(),
            'category_id': random.choice(sub_category_ids),
            'brand_id': random.choice(brand_ids),
            'seller_id': random.choice(seller_ids),
            'price': round(random.uniform(100000, 50000000), 2),
            'stock_qty': random.randint(0, 500),
            'rating': round(random.uniform(3.0, 5.0), 1),
            'is_active': random.choice([True, False]),
            'created_at': created_at,
            'created_by': "Admin",
            'updated_at': updated_at,
            'updated_by': updated_by,
            'is_deleted': is_deleted,
            'deleted_at': deleted_at,
            'deleted_by': deleted_by
        })  
    df = pd.DataFrame(products)
    df.to_sql('product', con=engine, if_exists='append', index=False, chunksize=batch_size)
    return pd.read_sql(query_select_product_id, con=engine)['product_id'].tolist()  


def insert_promotion(count=30):
    promotions = []
    for _ in range(count):
        p_type = random.choice(promotion_types)
        d_type = random.choice(discount_types)
        prefix = f"{random.randint(1, 12)}.{random.randint(1, 12)}" if random.random() < 0.5 else "Siêu"
        name = f"{prefix} {random.choice(promotion_names)}"
        if d_type == 'percentage':
            d_value = round(random.choice([5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 50.0, 70.0]), 2)
        else:
            d_value = float(random.choice([20000, 50000, 100000, 150000, 200000, 500000]))
        created_at = fake.date_time_between(start_date=startDate, end_date=datetime(2025, 1, 31))
        start_date = fake.date_between(start_date=created_at.date(), end_date=created_at.date() + timedelta(days=30))
        end_date = start_date + timedelta(days=random.randint(7, 45))
        promotions.append({
            'promotion_name': name,
            'promotion_type': p_type,
            'discount_type': d_type,
            'discount_value': d_value,
            'start_date': start_date,
            'end_date': end_date,
            'created_at': created_at
        })
    df = pd.DataFrame(promotions)
    df.to_sql('promotion', con=engine, if_exists='append', index=False)
    return pd.read_sql(query_select_promotion_id, con=engine)['promotion_id'].tolist()

def insert_promotion_product(count=500, batch_size=100):
    promo_ids = pd.read_sql(query_select_promotion_id, con=engine)['promotion_id'].tolist()
    prod_ids = pd.read_sql(query_select_product_id, con=engine)['product_id'].tolist()
    used_pairs = set()
    pairs = []
    while len(pairs) < count:
        for promo_id in promo_ids:
            if len(pairs) >= count:
                break
            prod_id = random.choice(prod_ids)
            if (promo_id, prod_id) not in used_pairs:
                used_pairs.add((promo_id, prod_id))
                pairs.append((promo_id, prod_id))
    links = [{
        'promotion_id': promo_id,
        'product_id': prod_id,
        'created_at': fake.date_time_between(start_date=startDate, end_date=datetime(2025, 5, 31))
    } for promo_id, prod_id in pairs]
    df = pd.DataFrame(links)
    df.to_sql('promotion_product', con=engine, if_exists='append', index=False, chunksize=batch_size)
    return pd.read_sql(query_select_promotion_product_id, con=engine)['promo_product_id'].tolist()

def main():
        truncate_all_tables()

        brand_ids = insert_brand(count=20)
        print(f"Brand (Pandas): {len(brand_ids)} bản ghi")

        category_ids = insert_category()
        print(f"Category (Pandas): {len(category_ids)} sub-categories")

        seller_ids = insert_seller(count=50)
        print(f"Seller (Pandas): {len(seller_ids)} bản ghi")

        customer_ids = insert_customer(count=30000, batch_size=5000)
        print(f"Customer (Pandas): {len(customer_ids)} bản ghi")

        product_ids = insert_product(count=3000, batch_size=1000)
        print(f"Product (Pandas): {len(product_ids)} bản ghi")

        promotion_ids = insert_promotion(count=30)
        print(f"Promotion (Pandas): {len(promotion_ids)} bản ghi")

        promo_product_ids = insert_promotion_product(count=500, batch_size=100)
        print(f"Promotion Product (Pandas): {len(promo_product_ids)} liên kết")

if __name__ == '__main__':
    main()