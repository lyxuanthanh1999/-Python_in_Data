from variable import create_table_commands
import psycopg2
from config import load_config

def create_tables():
    config = load_config()
    commands = create_table_commands
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                for command in commands:
                    cur.execute(command)
                
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed')
    
if __name__ == '__main__':
    create_tables()