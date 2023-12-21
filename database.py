import sqlalchemy, os
from dotenv import load_dotenv
from sqlalchemy import inspect, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import bcrypt
from datetime import datetime

load_dotenv()


def get_database_engine():
    while True:
        username = os.getenv('USER')
        password = os.getenv('PASSWORD')
        host = os.getenv('HOST')
        port = os.getenv('PORT_DB')
        dbname = os.getenv('DBNAME')
        engine = sqlalchemy.create_engine(
            "mysql+pymysql://" + username + ":" + password + "@" + host + ":" + port + "/" + dbname)

        try:
            print("Connection to the database successful!")
            print(engine)
            return engine
        except Exception as e:
            print("Error connecting to the database:", e)
            print("Please try again.\n")


engine = get_database_engine()
Base = declarative_base()


def get_table_names(engine=engine):
    table_names = inspect(engine).get_table_names()
    return table_names


print(get_table_names())

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


Base.metadata.create_all(engine)


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

# def filter_result(table_str, matrixColumn, matrixData):
#     # bisa mengambil data pada table dengan hanya sebuah string
#
#     # table_class = globals().get(table_str.title())
#     # if not table_class:
#     #     raise ValueError(f"Table class '{table_str}' not found.")
#
#     result = session.query(cls[table_str])
#     for i in range(len(matrixColumn)):
#         if matrixColumn[i] == "jenis":  # SOLUSI SEMENTARA UNTUK KOLOM DENGAN NAMA NYA LEBIH DARI SATU KATA
#             matrixColumn[i] = "jenis_perangkat"
#         # new_result = result.filter(getattr(cls[table_str], matrixColumn[i]) == matrixData[i])
#         new_result = result.filter(getattr(cls[table_str], matrixColumn[i]).like('%' + matrixData[i] + '%'))
#         result = new_result
#     return result
#
#
# def getTableColumns(table_name):
#     table = inspect(engine).get_columns(table_name)
#     column_names = [column['name'] for column in table]
#     return column_names
#
#
# def get_table_privilege():
#     tables = session.query(cls['table_lists']).all()
#     result = {}
#     for table in tables:
#         result[table.table_name] = table.privilege  # ini masih kurang dynamic,, misal nama kolomnya berubah
#     return result
#
#
# def add_contact(lokasi, pic, kontak):
#     new_contact = cls['contacts'](lokasi=lokasi, pic=pic, kontak=kontak)
#     session.add(new_contact)
#     session.commit()
#     # return [lokasi, pic, kontak]
#
#
# def addUser(nama, role, telegramid):
#     newUser = cls['users'](nama_telegram=nama, role=role, telegram_id=telegramid)
#     session.add(newUser)
#     session.commit()
#     return [nama, role]
#
#
# def select_all_users():
#     employees = session.query(cls['users']).all()
#     for employee in employees:
#         employeename = " - " + employee.nama_telegram + ' ' + employee.role
#         print(employeename)
#
#
# def selectByRole(telegramid):
#     users = session.query(cls['users']).filter_by(telegram_id=telegramid)
#     return users
#
#
# def updateUserStatus(id, isActive):
#     employee = session.get(cls['users'], id)
#     employee.active = isActive
#     session.commit()
#
#
# def deleteUser(id):
#     session.query(cls['users']).filter(cls['users'].id == id).delete()
#     session.commit()
#
#
# def summary_table(table, column, select_value, summary_columns):
#     summary_dictionary = {}
#     for summary_column in summary_columns:
#         query = f"""
#                 SELECT {column}, {summary_column}, COUNT(*)
#                 FROM  {table}
#                 WHERE {column} = :{column}
#                 GROUP BY {summary_column}
#                 """
#         with engine.connect() as connection:
#             results = connection.execute(text(query), {column: select_value}).fetchall()
#
#         column_name = {}
#         for value in results:
#             column_name[value[1]] = value[2]
#
#         summary_dictionary[summary_column] = column_name
#
#     return summary_dictionary
