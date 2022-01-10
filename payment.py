import logging
from typing import Union

from liqpay import LiqPay
import config
import requests
import pytz
from datetime import datetime

class Payment:
    def __init__(self):
        self.liqpay = LiqPay(config.public_key, config.private_key)
        self.data_const = {
            "version": "3",
            "public_key": config.public_key,
        }

    def generate_new_url_for_pay(self, order_id, amount, text='') -> Union[str, None]:
        """
        Отримання від платіжної системи нового посилання на оплату
        :param order_id: унікальний id, який використовуються отримання інформації від платіжної системи по конкретній
                        оплаті
        :param amount: сума до сплати
        :param text: коментар, який бачить клієнт на сторінці оплати
        :return: url для оплати
        """
        # детальніше https://www.liqpay.ua/documentation/api/aquiring/checkout/doc
        # копіювання сталої частини даних для платежу
        data = {k: v for k, v in self.data_const.items()}
        # створення даних по поточному платежу
        data['action'] = "pay"
        data["amount"] = amount
        data["currency"] = "UAH"
        data["language"] = "uk"
        data["description"] = f"Оплата замовлення в боті. {text}"
        data["order_id"] = order_id
        data['server_url'] = 'http://[your_url]'
        data_to_sign = self.liqpay.data_to_sign(data)
        params = {'data': data_to_sign,
                  'signature': self.liqpay.cnb_signature(data)}
        res = None
        try:
            res = requests.post(url='https://www.liqpay.ua/api/3/checkout/', data=params)
            if res.status_code == 200:
                return res.url
            else:
                logging.warning(f"time {datetime.now(pytz.timezone('Europe/Kiev'))}| incorrect status code form response - {res.status_code}, must be 200, "
                                f"data- {data}, params - {params}")
                return
        except:
            logging.exception(f'error getting response from liqpay, '
                              f'res - {res}, data- {data}, params - {params}')

    def get_order_status_from_liqpay(self, order_id) -> Union[dict, bool]:
        data = {k: v for k, v in self.data_const.items()}
        data["action"] = "status"
        data["order_id"] = order_id
        res = self.liqpay.api("request", data)
        if res.get("action") == "pay":
            if res.get('public_key') == config.public_key:
                return res
        return False
        '''
        {'result': 'ok', 'payment_id': 1111111111, 'action': 'pay', 'status': 'success', 'version': 3, 'type': 'buy',
         'paytype': 'privat24', 'public_key': [liqpay_public_key], 'acq_id': 555555, 'order_id': [your_order_id],
         'liqpay_order_id': '0TG1RB583639561432457126', 'description': 'Оплата замовлення в боті. ',
         'sender_phone': '380681111111', 'sender_card_mask2': '111111*11', 'sender_card_bank': 'pb',
         'sender_card_type': 'mc', 'sender_card_country': 804, 'amount': 2.0, 'currency': 'UAH',
         'sender_commission': 0.0, 'receiver_commission': 0.05, 'agent_commission': 0.0, 'amount_debit': 2.0,
         'amount_credit': 2.0, 'commission_debit': 0.0, 'commission_credit': 0.05, 'currency_debit': 'UAH',
         'currency_credit': 'UAH', 'sender_bonus': 0.0, 'amount_bonus': 0.0, 'authcode_debit': '111111',
         'rrn_debit': '000000000000', 'mpi_eci': '4', 'is_3ds': False, 'language': 'uk', 'create_date': 1639511462410,
         'end_date': 1639511465021, 'transaction_id': 1111111111}'''
