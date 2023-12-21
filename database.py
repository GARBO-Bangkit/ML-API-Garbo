import sqlalchemy, os
from dotenv import load_dotenv
from sqlalchemy import inspect, Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship
import bcrypt
from datetime import datetime
from google.cloud.sql.connector import Connector, IPTypes
import pymysql

load_dotenv()

# def get_database_engine():
#     while True:
#         try:
#             # for local test
#             username = os.getenv('DB_USER')
#             password = os.getenv('DB_PASS')
#             host = os.getenv('HOST')
#             port = os.getenv('PORT_DB')
#             dbname = os.getenv('DB_NAME')
#             engine = sqlalchemy.create_engine(
#                 "mysql+pymysql://" + username + ":" + password + "@" + host + ":" + port + "/" + dbname)
#             # db_user = os.environ.get("DB_USER")
#             # db_pass = os.environ.get("DB_PASS")
#             # db_name = os.environ.get("DB_NAME")
#             # cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
#             #
#             # # When deployed to Cloud Run, the `DB_SOCKET_PATH` will be provided by the environment.
#             # db_socket_path = os.environ.get("DB_SOCKET_PATH", "/cloudsql")
#             #
#             # # Configure SQLAlchemy engine
#             # engine = create_engine(
#             #     f"mysql+pymysql://{db_user}:{db_pass}@/{db_name}?unix_socket={db_socket_path}/{cloud_sql_connection_name}"
#             # )
#             print("Connection to the database successful!")
#             print(engine)
#             return engine
#         except Exception as e:
#             print("Error connecting to the database:", e)
#             print("Please try again.\n")

def connect_with_connector() -> sqlalchemy.engine.base.Engine:

    instance_connection_name = os.environ[
        "INSTANCE_CONNECTION_NAME"
    ]  # e.g. 'project:region:instance'
    db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    connector = Connector(ip_type)

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    return pool

engine = connect_with_connector()
Base = declarative_base()

Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()


class User(Base):
    __tablename__ = 'user'
    username = Column(String(100), primary_key=True)
    password = Column(String(100))
    name = Column(String(100))
    email = Column(String(100))
    point = Column(Integer, default=0)

    histories = relationship("History", back_populates="user")

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), ForeignKey('user.username'))
    foto = Column(String(1000))
    timestamp = Column(String(100))
    jenis_sampah = Column(String(100))

    user = relationship("User", back_populates="histories")


# Base.metadata.create_all(engine)


# users = session.query(User).all()
# for user in users:
#     print(user.point)
#
# histories = session.query(History).all()
# for history in histories:
#     print(history.username)

# select table query
def select_all(table):
    results = session.query(table).all()
    return results


def user_exists(usernameORemail, session=session):
    return session.query(User).filter(
        (User.username == usernameORemail) | (User.email == usernameORemail)
    ).first() is not None


def add_user(data):
    new_user = User(
        username=data['username'],
        name=data['name'],
        email=data['email']
    )
    # set password and hash that
    new_user.set_password(data['password'])

    session.add(new_user)
    session.commit()


def login_user(data):
    user = session.query(User).filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        return True
    else:
        return False


def add_history(username, foto, jenis_sampah):
    user = session.query(User).filter_by(username=username).first()
    if user:
        # Add points jika jenis_sampah
        if jenis_sampah.lower() in ['cardboard', 'paper']:
            user.point += 10
        if jenis_sampah.lower() in ['plastic']:
            user.point += 15
        if jenis_sampah.lower() in ['glass', 'metal']:
            user.point += 20

    new_data = History(
        username=username,
        foto=foto,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        jenis_sampah=jenis_sampah
    )

    session.add(new_data)
    session.commit()

def get_history_user(username):
    history_records = session.query(History).filter_by(username=username).all()

    history_list = [
        {
            "username": record.username,
            "foto": record.foto,
            "timestamp": record.timestamp,
            "jenis_sampah": record.jenis_sampah
        } for record in history_records
    ]

    return history_list

def get_history_user_and_jenis_sampah(username, jenis_sampah):
    history_records = session.query(History).filter(
        History.username == username,
        History.jenis_sampah == jenis_sampah
    ).all()

    history_list = [
        {
            "username": record.username,
            "foto": record.foto,
            "timestamp": record.timestamp,
            "jenis_sampah": record.jenis_sampah
        } for record in history_records
    ]

    return history_list
