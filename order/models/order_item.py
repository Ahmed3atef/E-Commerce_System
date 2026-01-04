from django.db import models

class OrderItem(models.Model):
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, related_name='order_items')
    
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2) 
    

    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='order_items')

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.order_number})"

    @property
    def total_price(self):
        return self.quantity * self.price
