"""
Product model — eco-products made from flower waste.
"""
from django.db import models
 
 
class Product(models.Model):
    ECO_SCORE_CHOICES = [('A+', 'A+'), ('A', 'A'), ('B+', 'B+'), ('B', 'B')]
 
    name        = models.CharField(max_length=150)
    emoji       = models.CharField(max_length=8, default='🌿')
    description = models.TextField()
    full_desc   = models.TextField(blank=True, help_text='Detailed description shown in product modal')
    eco_benefit = models.CharField(max_length=200)
    eco_score   = models.CharField(max_length=4, choices=ECO_SCORE_CHOICES, default='A')
    price       = models.CharField(max_length=80, help_text='e.g. ₹120 / pack of 20')
    usage       = models.TextField(blank=True)
    impact      = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    color       = models.CharField(max_length=10, default='#e8f2eb', help_text='CSS hex color for card background')
    image       = models.ImageField(upload_to='products/', null=True, blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = 'fc_products'
        ordering = ['name']
 
    def __str__(self):
        return self.name
 
