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

def insert_brand(cur, count =20):
    brand_data=[]
    for i in range(count):
        name = fake.company()
        country = fake.country()
        created_at = fake.date_time_between(
            start_date=datetime(2024,1,1),
            end_date=datetime(2024,12,31)
        )
        brand_data.append((name,country,created_at))
    print(brand_data)

def main():
    config = load_config()
    conn = None
    try:
        conn = psycopg2.connect(**config)
        with conn:
            with conn.cursor() as cur:
                # Brand
                brand_ids = insert_brand(cur,count=20)
    except(Exception,psycopg2.DatabaseError)as error:
        print(error)
    finally:
        if conn is not None:
            cur.close()
            conn.close()

if __name__ == '__main__':
    main()