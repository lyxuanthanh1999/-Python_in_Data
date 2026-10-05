
from sqlalchemy import URL
from config import load_config
from sqlalchemy import create_engine
 


def get_engine(echo=False):
    """"""
    try:
        cfg = load_config()
        # db_url = f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg.get('port', 5432)}/{cfg['database']}"
        # engine = create_engine(db_url)
        db_url = URL.create(
            drivername="postgresql+psycopg2",
            username=cfg.get("user"),
            password=cfg.get("password"),
            host=cfg.get("host"),
            port=cfg.get("port"),
            database=cfg.get("database")
        )

        engine = create_engine(db_url,echo=echo,pool_pre_ping=True)
        return engine
    except Exception as error:
        print(error)
        raise error

if __name__ == '__main__':
    engine = get_engine()
    with engine.connect() as conn:
        print('Connected SQLAlchemy with PostgreSQL success')