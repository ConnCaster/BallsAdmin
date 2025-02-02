from keyboard_handlers.handlers import *
from db_handlers.handlers import *
from third_party.ops import *
import configparser


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith("back|"):
        await back(query, context)

    elif query.data == 'show_orders':
        await show_orders(query)

    elif query.data == 'confirm_orders':
        pass

    elif query.data == 'edit_db':
        pass

    elif query.data == 'add_item':
        pass

    elif query.data == 'delete_item':
        pass


class Ball:
    def __init__(self, id, type, picture, amount=-1, price=-1):
        self.id = id
        self.type = type
        self.picture = picture
        self.amount = amount
        self.price = price


class CommonBall(Ball):
    Fields = ['id', 'ball_type', 'common_ball_type', 'material', 'color', 'picture', 'amount', 'price', 'nickname', 'notes']

    def __init__(self, id, type, material, color, picture, amount=-1, price=-1):
        super().__init__(id, type, picture, amount, price)
        self.material = material
        self.color = color


class ShapedBall(Ball):
    Fields = ['id', 'ball_type', 'shaped_ball_type', 'subtype', 'picture', 'amount', 'price', 'nickname', 'notes']

    def __init__(self, id, type, subtype, picture, amount=-1, price=-1):
        super().__init__(id, type, picture, amount, price)
        self.subtype = subtype


class BlowUpBall(Ball):
    Fields = ['id', 'ball_type', 'amount', 'price', 'nickname', 'notes']

    def __init__(self, id=0, amount=-1, price=-1):
        super().__init__(id, "", "", amount, price)


class Order:
    Fields = ['id', 'ball_type', 'amount', 'nickname', 'notes']  #TODO: Добавить status перед notes
    def __init__(self, id: int, ball: Ball, type: str, amount: int, nick: str, notes: str):
        # E.g.: (1, 'common', 'Hello, Kitty', 'latex', 'black', 'hello_kitty_black.jpg', 1, 65, '@akuda0')
        self.id = id
        self.ball = ball
        self.type = type
        self.amount = amount
        self.nick = nick
        #TODO: добавить извлечение статуса заказа из БД
        # self.status = status  # paid/not paid
        self.notes = notes

    def change_status(self, status, ball_id):
        config = configparser.ConfigParser()
        config.read_file("cfg_file.ini")
        config["balloon.tmp_trash"]["shaped_balls_trash"]
        connection = sqlite3.Connection(os.path.join('db', 'balls_seller.sqlite'))
        cursor = connection.cursor()
        if status == "paid":
            cursor.execute("REPLACE INTO Orders (status) VALUES (paid)")
        elif status == "delivered":
            cursor.execute(f"INSERT INTO Orders_history (ball, type, amount, nickname, status)"
                           f"VALUES ({cursor.execute("SELECT ball, type, amount, nickname, status"
                                                     f"FROM Orders WHERE id = {ball_id}")})")
            cursor.execute(f"DELETE Orders WHERE id = {ball_id}")
        connection.close()


class Orders:
    def __init__(self):
        """
        self.orders - главный контейнер со всеми заказами !!!
        """
        self.path = get_db_path()
        # TODO: blow up - создать отдельный класс для этого вида заказа
        self.orders = {"common": [], "shaped": [], "blowup": []}
        self.__get_orders_from_db()

    def __get_orders_from_db(self):
        common_orders, shaped_orders, blowup_orders = get_orders(self.path)
        for order_tuple in common_orders:
            common_ball_fields = dict(zip(CommonBall.Fields, order_tuple))
            ball = CommonBall(-1,
                              common_ball_fields['common_ball_type'],
                              common_ball_fields['material'],
                              common_ball_fields['color'],
                              common_ball_fields['picture'],
                              common_ball_fields['amount'],
                              common_ball_fields['price'])
            order_fields = dict(zip(Order.Fields, list(order_tuple[0:2]) + [order_tuple[6]] + list(order_tuple[8:])))
            order = Order(order_fields['id'],
                          ball,
                          order_fields['ball_type'],
                          order_fields['amount'],
                          order_fields['nickname'],
                          order_fields['notes'])
            self.orders["common"].append(order)
        for order_tuple in shaped_orders:
            shaped_ball_fields = dict(zip(ShapedBall.Fields, order_tuple))
            ball = ShapedBall(-1,
                              shaped_ball_fields['shaped_ball_type'],
                              shaped_ball_fields['subtype'],
                              shaped_ball_fields['picture'],
                              shaped_ball_fields['amount'],
                              shaped_ball_fields['price'])
            order_fields = dict(zip(Order.Fields, list(order_tuple[0:2]) + [order_tuple[5]] + list(order_tuple[7:])))
            order = Order(order_fields['id'],
                          ball,
                          order_fields['ball_type'],
                          order_fields['amount'],
                          order_fields['nickname'],
                          order_fields['notes'])
            self.orders["shaped"].append(order)
        for order_tuple in blowup_orders:
            blowup_balls_fields = dict(zip(BlowUpBall.Fields, order_tuple))
            ball = BlowUpBall(-1, price=blowup_balls_fields['price'])
            order_fields = dict(zip(Order.Fields, list(order_tuple[0:3]) + list(order_tuple[4:6])))
            order = Order(order_fields['id'],
                          ball,
                          order_fields['ball_type'],
                          order_fields['amount'],
                          order_fields['nickname'],
                          order_fields['notes'])
            self.orders["blowup"].append(order)

    def gen_orders_msg(self):
        all_orders = ""
        counter = 0

        all_orders += "Обычные шарики:\n"
        if self.orders["common"]:
            counter = 0
            for order in self.orders["common"]:
                all_orders += (f"[{counter+1}] -- заказано {order.amount} шт, "
                               f"итоговая стоимость - {order.amount * order.ball.price}₽ ({order.nick})\n")
                counter += 1

        all_orders += "\nФигурные шарики:\n"
        if self.orders["shaped"]:
            counter = 0
            for order in self.orders["shaped"]:
                all_orders += (f"[{counter+1}] -- заказано {order.amount} шт, "
                               f"итоговая стоимость - {order.amount * order.ball.price}₽ ({order.nick})\n")
                counter += 1

        all_orders += "\nНадуть шарики:\n"
        if self.orders["blowup"]:
            counter = 0
            for order in self.orders["blowup"]:
                all_orders += (f"[{counter+1}] -- заказано {order.amount} шт, "
                                   f"итоговая стоимость - {order.amount * order.ball.price}₽ ({order.nick})\n")
                counter += 1

        return str(all_orders)

def main():
    application = Application.builder().token("6875313175:AAHB0_46knn6bf4iapEGYVKkcTxBSeCz8pk").build()
    application.add_handler(CommandHandler(["start"], start))
    # application.add_handler(CommandHandler(["orders"], orders))
    application.add_handler(CallbackQueryHandler(button))
    # application.add_handler(MessageHandler(filters.Regex("^\d+$"),order_registrar))  # MessageHandler(filters.Regex("^(Boy|Girl|Other)$")
    application.run_polling()
    application.start()


if __name__ == "__main__":
    # config = configparser.ConfigParser()
    # path_to_config = os.path.join("config", "cfg_file.ini")
    # with open(path_to_config) as cfg_file:
    #     config.read_file(cfg_file)
    #     db_path = config["admin.db"]["db_path"]
    #
    # connection = sqlite3.Connection(db_path)
    # cursor = connection.cursor()
    #
    # s = cursor.execute("SELECT nickname from Orders").fetchall()
    # print(s)
    main()
