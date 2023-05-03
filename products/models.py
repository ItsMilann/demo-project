from django.db.models import Model, CharField, IntegerField, ImageField, TextField, FloatField

LOREM = "Lorem ipsum dolor sit amet consectetur adipisicing elit. Quaerat tempore soluta iste ratione praesentium, totam optio at voluptate assumenda pariatur, necessitatibus laboriosam quos! A, obcaecati pariatur cumque veniam exercitationem voluptates aut itaque doloremque dolore nulla modi ullam fuga delectus rerum impedit enim veritatis natus similique animi. Culpa aperiam eaque iure!"


class Product(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=20)
    codename = CharField(max_length=20)
    description = TextField(default=LOREM)
    rating = FloatField(default=5)
    price = IntegerField()
    image = ImageField(default="default.jpg")
    discount_percent = IntegerField()

    def __str__(self) -> str:
        return self.name
