from django.db import models
import os
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.db.models import Avg
# Create your models here.

class All_User(AbstractUser):
       is_customer = models.BooleanField(default=False)
       is_service_provider = models.BooleanField(default=False)
       phone_number = models.CharField( max_length=15, blank=True, null=True , unique=True)
       def __str__(self):
              return self.username
       
       
def profile_image(instance, filename):
       ext= filename.split('.')[-1]
       filename = f"{instance.user.username}_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.{ext}"
       return os.path.join('profile_pics', filename)


def banner_image(instance, filename):
       ext= filename.split('.')[-1]
       filename = f"{instance.user.username}_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.{ext}"
       return os.path.join('banner_pics', filename)

def previous_work_image(instance, filename):
       ext= filename.split('.')[-1]
       filename = f"{instance.service_provider.username}_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.{ext}"
       return os.path.join('previous_work_images', filename)

class CustomerProfileModel(models.Model):
       user = models.OneToOneField(All_User, on_delete=models.CASCADE )
       profileImage = models.ImageField(upload_to=profile_image, blank=True, null=True)
       username = models.CharField(max_length=100, blank=True, null=True)
       mobile_no = models.CharField(max_length=15, blank=True, null=True ,unique=True)
       email= models.EmailField(max_length=254, blank=True, null=True)
       district = models.CharField(max_length=100, blank=True, null=True)
       city = models.CharField(max_length=100, blank=True, null=True)
       address = models.TextField(blank=True, null=True )
       

       def __str__(self):
              return f"{self.user.username}'s customer profile"

class ProviderProfileModel(models.Model):
       user = models.OneToOneField(All_User, on_delete=models.CASCADE)
       profileImage = models.ImageField(upload_to=profile_image, blank=True, null=True)
       username = models.CharField(max_length=100, blank=True, null=True)
       service_name = models.CharField(max_length=100, blank=True, null=True)
       banner_image = models.ImageField(upload_to=banner_image, blank=True, null=True)
       about_content = models.TextField(blank=True, null=True)
       mobile_no = models.CharField(max_length=15, blank=True, null=True ,unique=True)
       email= models.EmailField(max_length=254, blank=True, null=True)
       district = models.CharField(max_length=100, blank=True, null=True)
       city = models.CharField(max_length=100, blank=True, null=True)
       address = models.TextField(blank=True, null=True )
       slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)

       def save(self, *args, **kwargs):
              if not self.slug:
                     combined = f"{self.user.username}-{self.service_name}-{self.district}-{self.city}"
                     self.slug = slugify(combined)
              super().save(*args, **kwargs)

       def __str__(self):
              return f"{self.user.username}'s service provider profile"   

class Previous_Work(models.Model):
    service_provider = models.ForeignKey(ProviderProfileModel, on_delete=models.CASCADE)
    service_title = models.CharField(max_length=100, blank=False, null=False)
    service_image = models.ImageField(upload_to=previous_work_image, blank=False, null=False)
    service_description = models.TextField(blank=False, null=False)
    
    def __str__(self):
        return f"{self.service_provider.username}'s previous work at {self.service_title}"
 

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reject', 'Reject'),
        ('accept', 'Accept'),
        ('complete', 'Complete'),
        ('cancel', 'Cancel'),
    ]

    SERVICE_TYPE_CHOICES = [
        ('basic_service', 'Basic Service'),
        ('standard_service', 'Standard Service'),
        ('full_service', 'Full Service'),
    ]

    customer = models.ForeignKey(CustomerProfileModel, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ProviderProfileModel, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_mobile = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    full_address = models.TextField()
    service_type = models.CharField(max_length=100, choices=SERVICE_TYPE_CHOICES, default='basic_service')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_date = models.DateField()
    booking_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking: {self.service_provider.user.username} by {self.customer.user.username} - {self.status}"


class BookingReviews(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(CustomerProfileModel, on_delete=models.CASCADE, related_name='customer_reviews')
    service_provider = models.ForeignKey(ProviderProfileModel, on_delete=models.CASCADE, related_name='provider_reviews')
    rating = models.PositiveSmallIntegerField(default=1)
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.user.username} → {self.service_provider.user.username} ({self.rating}⭐)"


class AverageRating(models.Model):
    service_provider = models.OneToOneField(ProviderProfileModel, on_delete=models.CASCADE, related_name='average_rating')
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=1)

    def __str__(self):
        return f"Average rating for {self.service_provider.user.username}: {self.rating}⭐"