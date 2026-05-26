"""
PickupRequest model — flower waste collection scheduling.
"""
from django.db import models
from django.conf import settings
 
 
class PickupRequest(models.Model):
    FLOWER_CHOICES = [
        ('Marigold',  'Marigold (Genda)'),
        ('Rose',      'Rose'),
        ('Jasmine',   'Jasmine'),
        ('Lotus',     'Lotus'),
        ('Hibiscus',  'Hibiscus'),
        ('Mixed',     'Mixed Flowers'),
        ('Other',     'Other'),
    ]
 
    STATUS_CHOICES = [
        ('Pending',   'Pending'),
        ('Approved',  'Approved'),
        ('Collected', 'Collected'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
 
    # Submitter info (optional FK — public users may not be registered)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pickup_requests'
    )
 
    # Request fields (mirrored from the frontend form)
    full_name    = models.CharField(max_length=120)
    temple_name  = models.CharField(max_length=200)
    phone        = models.CharField(max_length=15)
    location     = models.TextField()
    flower_type  = models.CharField(max_length=20, choices=FLOWER_CHOICES)
    quantity_kg  = models.DecimalField(max_digits=8, decimal_places=2)
    pickup_date  = models.DateField()
 
    # Admin-managed
    status       = models.CharField(max_length=12, choices=STATUS_CHOICES, default='Pending')
    admin_notes  = models.TextField(blank=True)
 
    submitted_on = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table  = 'fc_pickup_requests'
        ordering  = ['-submitted_on']
        verbose_name = 'Pickup Request'
 
    def __str__(self):
        return f'{self.temple_name} — {self.flower_type} ({self.pickup_date})'
 
