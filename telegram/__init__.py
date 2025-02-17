class Telegram:
    token = ""
    chat_id = ''

    @classmethod
    def get_instance(cls):
        import telebot
        return telebot.TeleBot(cls.token)

    @classmethod
    def _send(cls, message: str):
        try:
            bot = cls.get_instance()
            bot.send_message(cls.chat_id, message)
        except Exception as e:
            print(e)
            pass

    @classmethod
    def support(cls, msg):
        message = f"FanPost Support:\n New message:\n {msg}  "
        cls._send(message=message)

    @classmethod
    def new_registration(cls, email):
        message = f"FanPost:\n New user registration email: {email}"
        cls._send(message=message)

    @classmethod
    def add_to_cart(cls, product):
        message = (f"FanPost: added to the cart "
                   f"Product:\n id - {product.id} \n name - {product.name}\n price - {product.price} ")
        cls._send(message=message)

    @classmethod
    def new_buy(cls, order):
        message = f"FanPost:\n New Buy order:\n orderUuid - {order.uuid}"
        cls._send(message=message)

    @classmethod
    def new_checkout(cls, order):
        message = f"FanPost:\n New checkout order:\n orderUuid - {order.uuid}"
        cls._send(message=message)

    @classmethod
    def new_share(cls, product):
        message = (f"FanPost:\n New share "
                   f"Product:\n id - {product.id} \n name - {product.name}\n price - {product.price}")
        cls._send(message=message)

    @classmethod
    def new_reg(cls, user_email, social):
        if social == 'twitter':
            user_name = user_email
            message = (f"FanPost:\n New User registration social:\n "
                       f"User Name - {user_name} \n Social - {social}")
        else:
            message = (f"FanPost:\n New User registration social:\n "
                       f"Email - {user_email} \n Social - {social}")

        cls._send(message=message)

    @classmethod
    def new_paid(cls, order):
        message = f"FanPost:\n New Confirm payment order:\n orderUuid - {order.uuid}"
        cls._send(message=message)


__all__ = ['Telegram']
