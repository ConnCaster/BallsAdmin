import sqlite3
import os
import sys

from third_party.ops import *

sys.path.append("../")
from third_party.ops import gen_picture_path
import configparse


def get_customers():
    connection = sqlite3.Connection(get_db_path())
    cursor = connection.cursor()
    lst = list(map(lambda x: str(x[0]), cursor.execute("SELECT DISTINCT C.nickname FROM Customers C INNER JOIN Orders O ON C.id == O.nickname").fetchall()))
    connection.close()
    return lst


# def get_id_and_nicknames_from_DB():


def get_orders(db_path: str = ""):
    if not db_path:
        db_path = get_db_path()
    connection = sqlite3.Connection(db_path)
    cursor = connection.cursor()
    s = cursor.execute(f"SELECT "
                       f"Orders.id, "
                       f"Orders.type, "
                       f"Common_Balls.type, "
                       f"Common_Balls.material, "
                       f"Common_Balls.color, "
                       f"Common_Balls.picture, "
                       f"Orders.amount, "
                       f"Common_Balls.price, "
                       f"Customers.nickname, "
                       f"Orders.notes "
                       f"FROM Orders "
                       f"INNER JOIN Customers ON Orders.nickname = Customers.id "
                       f"INNER JOIN Common_Balls ON Orders.ball = Common_Balls.id")
    common_orders = s.fetchall()
    s = cursor.execute(f"SELECT "
                       f"Orders.id, "
                       f"Orders.type, "
                       f"Shaped_Balls.type, "
                       f"Shaped_Balls.subtype, "
                       f"Orders.amount, "
                       f"Shaped_Balls.price, "
                       f"Customers.nickname, "
                       f"Orders.notes "
                       f"FROM Orders "
                       f"INNER JOIN Customers ON Orders.nickname = Customers.id "
                       f"INNER JOIN Shaped_Balls ON Orders.ball = Shaped_Balls.id AND Orders.type = 'shaped'")
    shaped_orders = s.fetchall()
    s = cursor.execute(f"SELECT "
                       f"amount, "
                       f"Customers.nickname "
                       f"FROM Orders "
                       f"INNER JOIN Customers ON Orders.nickname = Customers.id AND orders.type = 'Blow up'")
    blowup_orders = s.fetchall()
    connection.close()
    return common_orders, shaped_orders, blowup_orders


async def add_item(update):
    await update.message.reply_text("Для начала выберете тип шарика, написав его тип [фигурный или обычный]")


if __name__ == "__main__":
    print(get_customers())
    # get_db_path()