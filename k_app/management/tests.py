from django.test import TestCase
from datetime import datetime
from .models import Product, Inventory, ShopOrder, InventoryOrder

class ModelTests(TestCase):
    def setUp(self):
        # Create some sample products
        self.product1 = Product.objects.create(name='Product 1', description='Description 1', measurement='cm', quantity=10)
        self.product2 = Product.objects.create(name='Product 2', description='Description 2', measurement='kg', quantity=20)

    def test_product_str_representation(self):
        self.assertEqual(str(self.product1), 'Product 1')
        self.assertEqual(str(self.product2), 'Product 2')

    def test_inventory_creation(self):
        # Ensure inventory is created correctly for products
        inventory1 = Inventory.objects.get(product=self.product1)
        inventory2 = Inventory.objects.get(product=self.product2)

        self.assertEqual(inventory1.quantity, 0)  # Initially, the quantity should be 0
        self.assertEqual(inventory2.quantity, 0)

    def test_shop_order_creation(self):
        # Ensure shop order is created correctly
        shop_order = ShopOrder.objects.create(user_id=1)

        self.assertFalse(shop_order.realized)
        self.assertIsNone(shop_order.realize_date)

    def test_inventory_order_creation(self):
        # Ensure inventory order is created correctly
        inventory_order = InventoryOrder.objects.create(user_id=1, quantity=5)

        self.assertFalse(inventory_order.realized)
        self.assertIsNone(inventory_order.realize_date)

    def test_shop_order_realization(self):
        # Test shop order realization and inventory update
        shop_order = ShopOrder.objects.create(user_id=1)
        shop_order.products.add(self.product1)
        shop_order.products.add(self.product2)

        # Initially, the inventory quantity should be unchanged
        inventory1 = Inventory.objects.get(product=self.product1)
        inventory2 = Inventory.objects.get(product=self.product2)
        self.assertEqual(inventory1.quantity, 0)
        self.assertEqual(inventory2.quantity, 0)

        shop_order.realized = True
        shop_order.save()

        # After realization, the inventory should be updated
        inventory1.refresh_from_db()
        inventory2.refresh_from_db()
        self.assertEqual(inventory1.quantity, -1)  # Quantity of product1 should be decreased by 1
        self.assertEqual(inventory2.quantity, -1)  # Quantity of product2 should be decreased by 1

    def test_inventory_order_realization(self):
        # Test inventory order realization and inventory update
        inventory_order = InventoryOrder.objects.create(user_id=1, quantity=5)
        inventory_order.products.add(self.product1)

        # Initially, the inventory quantity should be unchanged
        inventory1 = Inventory.objects.get(product=self.product1)
        self.assertEqual(inventory1.quantity, 0)

        inventory_order.realized = True
        inventory_order.save()

        # After realization, the inventory should be updated
        inventory1.refresh_from_db()
        self.assertEqual(inventory1.quantity, 5)  # Quantity of product1 should be increased by 5

    def test_shop_order_unrealization(self):
        # Test shop order unrealization and inventory update
        shop_order = ShopOrder.objects.create(user_id=1)
        shop_order.products.add(self.product1)
        shop_order.realized = True
        shop_order.save()

        # Initially, the inventory quantity should be updated
        inventory1 = Inventory.objects.get(product=self.product1)
        self.assertEqual(inventory1.quantity, -1)

        shop_order.realized = False
        shop_order.save()

        # After unrealization, the inventory should be updated back to its original value
        inventory1.refresh_from_db()
        self.assertEqual(inventory1.quantity, 0)

    def test_inventory_order_unrealization(self):
        # Test inventory order unrealization and inventory update
        inventory_order = InventoryOrder.objects.create(user_id=1, quantity=5)
        inventory_order.products.add(self.product1)
        inventory_order.realized = True
        inventory_order.save()

        # Initially, the inventory quantity should be updated
        inventory1 = Inventory.objects.get(product=self.product1)
        self.assertEqual(inventory1.quantity, 5)

        inventory_order.realized = False
        inventory_order.save()

        # After unrealization, the inventory should be updated back to its original value
        inventory1.refresh_from_db()
        self.assertEqual(inventory1.quantity, 0)
