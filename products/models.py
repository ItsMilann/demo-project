from django.db.models import Model, CharField, IntegerField, ImageField


class Product(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=20)
    codename = CharField(max_length=20)
    price = IntegerField()
    image = ImageField(default="default.jpg")
    discount_percent = IntegerField()

    def __str__(self) -> str:
        return self.name
