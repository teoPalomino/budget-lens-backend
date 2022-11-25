from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """A User Profile with a phone number and a user model
    """
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    telephone_number = PhoneNumberField(null=False, blank=False, unique=True)
    one_time_code = models.PositiveBigIntegerField(default=0)

    @receiver(post_save, sender='users.UserProfile')
    def post_save_user(sender, instance, created, *args, **kwargs):
        from category.models import Category
        Category.objects.bulk_create([
                Category(category_name='room',category_toggle_star=False,user_id=instance.id),
                Category(category_name='tax',category_toggle_star=False,user_id=instance.id),
                Category(category_name='parking',category_toggle_star=False,user_id=instance.id),
                Category(category_name='service',category_toggle_star=False,user_id=instance.id),
                Category(category_name='fee',category_toggle_star=False,user_id=instance.id),
                Category(category_name='delivery',category_toggle_star=False,user_id=instance.id),
                Category(category_name='product',category_toggle_star=False,user_id=instance.id),
                Category(category_name='food',category_toggle_star=False,user_id=instance.id),
                Category(category_name='alcohol',category_toggle_star=False,user_id=instance.id),
                Category(category_name='tobacco',category_toggle_star=False,user_id=instance.id),
                Category(category_name='transportation',category_toggle_star=False,user_id=instance.id),
                Category(category_name='fuel',category_toggle_star=False,user_id=instance.id),
                Category(category_name='discount',category_toggle_star=False,user_id=instance.id),
                Category(category_name='payment',category_toggle_star=False,user_id=instance.id),
                Category(category_name='Other',category_toggle_star=False,user_id=instance.id),
            ])
