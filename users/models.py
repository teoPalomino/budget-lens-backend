from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """A User Profile with a phone number, a user model, and an email to forward receipts
    """
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    telephone_number = PhoneNumberField(null=False, blank=False, unique=True)
    one_time_code = models.PositiveBigIntegerField(default=0)
    forwardingEmail = models.EmailField(max_length=254, null=True)

    @receiver(post_save, sender='users.UserProfile')
    def post_save_user(sender, instance, created, *args, **kwargs):
        from category.models import Category
        if created:
            Category.objects.bulk_create([
                Category(category_name='room', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_hotel_24'),
                Category(category_name='tax', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_monetization_on_24'),
                Category(category_name='parking', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_local_parking_24'),
                Category(category_name='service', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_cleaning_services_24'),
                Category(category_name='fee', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_attach_money_24'),
                Category(category_name='delivery', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_delivery_dining_24'),
                Category(category_name='product', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_inventory_24'),
                Category(category_name='food', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_fastfood_24'),
                Category(category_name='alcohol', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_wine_bar_24'),
                Category(category_name='tobacco', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_smoking_rooms_24'),
                Category(category_name='transportation', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_local_taxi_24'),
                Category(category_name='fuel', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_local_gas_station_24'),
                Category(category_name='discount', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_discount_24'),
                Category(category_name='payment', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_payment_24'),
                Category(category_name='Other', category_toggle_star=False, user_id=instance.id, icon='ic_baseline_category_24'),
            ])
