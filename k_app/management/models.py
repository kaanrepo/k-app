import uuid
from django.contrib.auth import get_user_model
from django.db import models
from datetime import datetime

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    measurement = models.CharField(max_length=50)
    quantity = models.IntegerField()

    def __str__(self):
        return self.name


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class ShopOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    realized = models.BooleanField(default=False)
    realize_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.realize_date = None
        elif self.realized and not self.realize_date:
            self.realize_date = datetime.now()
            for product in self.products.all():
                try:
                    inventory = Inventory.objects.get(product=product)
                    inventory.quantity -= 1
                    inventory.save()
                except Inventory.DoesNotExist:
                    pass
        elif not self.realized and self.realize_date:
            self.realize_date = None
            for product in self.products.all():
                try:
                    inventory = Inventory.objects.get(product=product)
                    inventory.quantity += 1
                    inventory.save()
                except Inventory.DoesNotExist:
                    pass
        super().save(*args, **kwargs)


class InventoryOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    quantity = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    realized = models.BooleanField(default=False)
    realize_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Inventory Order {self.id}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.realize_date = None
        elif self.realized and not self.realize_date:
            self.realize_date = datetime.now()
            for product in self.products.all():
                try:
                    inventory = Inventory.objects.get(product=product)
                    inventory.quantity += self.quantity
                    inventory.save()
                except Inventory.DoesNotExist:
                    inventory = Inventory.objects.create(product=product, quantity=self.quantity)
        elif not self.realized and self.realize_date:
            self.realize_date = None
            for product in self.products.all():
                try:
                    inventory = Inventory.objects.get(product=product)
                    inventory.quantity -= self.quantity
                    inventory.save()
                except Inventory.DoesNotExist:
                    pass
        super().save(*args, **kwargs)
