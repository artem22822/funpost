from engine.models import Order

def current_user(request):
    user = request.user if request.user.is_authenticated else None
    return {
        'current_user': user,
    }


def count_product(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, status=Order.CREATED).last()

        if order:
            products_count = order.products.count()
            order_uuid = order.uuid
        else:
            products_count = 0
            order_uuid = 0
    else:
        products_count = 0
        order_uuid = 0
    return {'products_count': products_count, 'order_uuid': order_uuid}


