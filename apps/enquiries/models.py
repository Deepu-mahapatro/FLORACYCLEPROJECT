"""
Enquiry / Quote Request model.
"""
from django.db import models
from django.conf import settings
 
 
class Enquiry(models.Model):
    # Optional link to a registered product
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='enquiries'
    )
 
    # Customer info
    customer_name = models.CharField(max_length=120)
    email         = models.EmailField()
    phone         = models.CharField(max_length=15)
    quantity      = models.CharField(max_length=60)   # free-text e.g. "50 packs"
    message       = models.TextField(blank=True)
 
    # Admin tracking
    is_responded  = models.BooleanField(default=False)
    submitted_on  = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table  = 'fc_enquiries'
        ordering  = ['-submitted_on']
        verbose_name_plural = 'Enquiries'
 
    def __str__(self):
        return f'{self.customer_name} — {self.product or "General"}'
