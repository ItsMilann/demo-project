from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    DeleteView,
    DetailView,
)
from .models import Product


class AboutView(TemplateView):
    template_name = "about.html"


class ProductList(ListView):
    model = Product
    template_name = "product_list.html"
