import sqlite3
import os
import sys
sys.path.append("../")
from third_party.ops import gen_picture_path
import configparser


def get_db_path():
    config = configparser.ConfigParser()
    if os.getcwd().endswith("db_handlers"):
        path_to_config = os.path.join("..", "config", "cfg_file.ini")
    else:
        path_to_config = os.path.join("config", "cfg_file.ini")
    with open(path_to_config) as cfg_file:
        config.read_file(cfg_file)
        db_path = config["admin.db"]["db_path"]
    return db_path


def get_customers():
    connection = sqlite3.Connection(get_db_path())
    cursor = connection.cursor()
    lst = list(map(lambda x: str(x[0]), cursor.execute("SELECT DISTINCT C.nickname FROM Customers C INNER JOIN Orders O ON C.id == O.nickname").fetchall()))
    connection.close()
    return lst


# def get_id_and_nicknames_from_DB():



def get_orders():
    connection = sqlite3.Connection(get_db_path())
    cursor = connection.cursor()
    s = cursor.execute(f"SELECT Orders.id, Orders.type, Common_Balls.type, Common_Balls.material, Common_Balls.color, Common_Balls.picture, Orders.amount , Common_Balls.price, Customers.nickname FROM Orders INNER JOIN Customers ON Orders.nickname = Customers.id INNER JOIN Common_Balls ON Orders.ball = Common_Balls.id")
    common_orders = s.fetchall()
    s = cursor.execute(f"SELECT Orders.id, Orders.type, Shaped_Balls.type, Shaped_Balls.subtype,  Orders.amount , Shaped_Balls.price, Customers.nickname FROM Orders INNER JOIN Customers ON Orders.nickname = Customers.id INNER JOIN Shaped_Balls ON Orders.ball = Shaped_Balls.id AND Orders.type = 'shaped'")
    shaped_orders = s.fetchall()
    s = cursor.execute(f"SELECT amount, Customers.nickname FROM Orders INNER JOIN Customers ON Orders.nickname = Customers.id AND orders.type = 'Blow up'")
    blowup_orders = s.fetchall()
    connection.close()
    return common_orders, shaped_orders, blowup_orders


async def add_item(update):
    await update.message.reply_text("Для начала выберете тип шарика, написав его тип [фигурный или обычный]")


if __name__ == "__main__":
    print(get_customers())
    # get_db_path()