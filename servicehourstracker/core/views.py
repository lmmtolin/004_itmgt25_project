from django.http import HttpResponse
from django.template import loader

def index(request):
    # Load the template
    template = loader.get_template("core/index.html")
    products = [
        {"name": "Americano", "price": 110},
        {"name": "Cappuccino", "price": 140},
    ]
    context = {
        "product_data": products
    }
    return HttpResponse(template.render(context, request))