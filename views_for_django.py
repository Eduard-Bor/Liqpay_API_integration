from django.http import HttpRequest,HttpResponse
import json
import logging
import base64
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime as dt
import payment
import pytz

import config

#skip checking for CSRF view protection
@csrf_exempt
def new_order(request:HttpRequest):
    if request.method != 'POST':
        logging.info(f"not POST method, return 404, time - {dt.now(pytz.timezone('Europe/Kiev'))}, body - {request.body}")
        return HttpResponse(status=404)

    data = request.body
    logging.info(f"new request, time - {dt.now(pytz.timezone('Europe/Kiev'))}, body={data}")
    try:
        res = process_request(data)
        if res == 404:
            return HttpResponse(status=404)
        elif not res:
            logging.info(f"request didn't change DB, time - {dt.now(pytz.timezone('Europe/Kiev'))}")
        else:
            logging.info(f"request processed correct, time - {dt.now(pytz.timezone('Europe/Kiev'))}")
    except:
        logging.exception(f"error processing request, time - {dt.now(pytz.timezone('Europe/Kiev'))}, data - {data}")
        return HttpResponse(status=500)
    return HttpResponse(status=200)


def process_request(request_data):
    """
    request data - data from request from liqpay, str or bytes
    more info - https://www.liqpay.ua/documentation/api/callback
    :return: True if DB modified, else False
    """
    res = request_data
    l = payment.Payment()
    # decode from bytes to str
    if isinstance(res, bytes):
        res_str: str = res.decode('utf-8')
    else:
        res_str: str = res
    # liqpay API replace specials symbol in anwer from server (like '+', '/' and '=')
    # replace it back
    res_str = res_str.replace('%2F', '/').replace('%2B', '+').replace('%3D', '=')
    # get param from answer res
    res_dict = {}
    for i in res_str.split('&'):
        try:
            n, v = i.split('=', 1)
            res_dict[n] = v
        except:
            logging.exception(f"parsed text for param hasn't '=', param - {i},\nall request - {res}")
    # get param data
    if not res_dict.get('signature'):
        logging.info(f"server request hasn't parametr signature, request_data:\n{request_data}")
        return 404

    original_sign = l.liqpay.str_to_sign(config.private_key + res_dict['data'] + config.private_key)
    if original_sign != res_dict['signature']:
        logging.warning(f"Signture doesn't much, original sinature {original_sign} ,"
                        f"signture from request {res_dict['signature']}, data for sign - {res_dict['data']}")
        return 404
    data_to_base64 = res_dict['data']
    data_decoded = base64.b64decode(data_to_base64).decode('utf-8')
    params = json.loads(data_decoded)
    # params => {'payment_id': 1111111111, 'action': 'pay', 'status': 'success', 'version': 3, 'type': 'buy', 'paytype': 'privat24', 'public_key': [liqpay_public_key], 'acq_id': 111111, 'order_id': [order_id], 'liqpay_order_id': 'AAAA1111111111111', 'description': 'Оплата замовлення в боті Foodicine. ', 'sender_phone': '3806811111111', 'sender_card_mask2': '111111*11', 'sender_card_bank': 'pb', 'sender_card_type': 'visa', 'sender_card_country': 804, 'amount': 1.0, 'currency': 'UAH', 'sender_commission': 0.0, 'receiver_commission': 0.03, 'agent_commission': 0.0, 'amount_debit': 1.0, 'amount_credit': 1.0, 'commission_debit': 0.0, 'commission_credit': 0.03, 'currency_debit': 'UAH', 'currency_credit': 'UAH', 'sender_bonus': 0.0, 'amount_bonus': 0.0, 'authcode_debit': '111111', 'rrn_debit': '1111111111', 'mpi_eci': '8', 'is_3ds': False, 'language': 'uk', 'create_date': 1639600598718, 'end_date': 1639600601738, 'transaction_id': 111111111}

    # there must be processing of the result
    return res
