## Demonstrating integration payment system Liqpay API in Python
More details you can see on my [Youtube channel](https://youtu.be/P6kZQHvHsPU) (ukrainian language) 
-   install liqpay-python
```
pip install git+https://github.com/liqpay/sdk-python
```
comand 'pip install liqpay-python' doesn't work for python 3 

-   create your own .env file similar to .env_template
##How it use?
```python
from payment import Payment
p = Payment()
# get new url for checkout (web page with 10 paymnet methods) 
checkout_url = p.generate_new_url_for_pay('my_unique_order_id', 100)
# check payment status for order
res = p.get_order_status_from_liqpay('my_unique_order_id')

```
For correct processing [Liqpay Callback](https://www.liqpay.ua/documentation/uk/api/callback) in your own realisation 
you must replace back specials symbol in request from 
server (like '+', '/' and '='), more details in views_for_django.py

views_for_django.py works with framework Django