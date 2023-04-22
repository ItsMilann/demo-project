from django.db.models import Model, CharField, IntegerField


class Product(Model): # inheritance
    id = IntegerField(primary_key=True)
    name = CharField(max_length=20)
    codename = CharField(max_length=20)
    price = IntegerField()
    discount_percent = IntegerField()

