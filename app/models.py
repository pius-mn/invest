"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from .utils import generate_ref_code
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname=models.TextField(max_length=12,blank=False)
    code = models.CharField(max_length=12, blank=True)
    recommended_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='ref_by')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    signup_confirmation = models.BooleanField(default=False)
    amount = models.FloatField(default=0.00)
   
    @property
    def available_balance(self):
        return self.amount-100

    @property
    def WithDrawable_balance(self):
        return self.amount-200
    def __str__(self):
        return f"{self.user.username}-{self.code}-{self.created}-{self.amount}"

    def get_recommened_profiles(self):
        qs = Profile.objects.all()
        # my_recs = [p for p in qs if p.recommended_by == self.user]
        
        my_recs = []
        for profile in qs:
            if profile.recommended_by == self.user:
                my_recs.append(profile)
        return my_recs, self.code, self.amount, self.available_balance,self.WithDrawable_balance
   



    def save(self, *args, **kwargs):
        if self.code == "":
            code = generate_ref_code()
            self.code = code
        super().save(*args, **kwargs)
@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.save()

###############################################################################################
# from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# M-pesa Payment models

class MpesaCalls(BaseModel):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = 'Mpesa Call'
        verbose_name_plural = 'Mpesa Calls'

    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = 'Mpesa Call Back'
        verbose_name_plural = 'Mpesa Call Backs'


class MpesaDeposits(BaseModel):

    phone_number = models.TextField()
    reference = models.TextField()
    transaction_date = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Mpesa Deposit'
        verbose_name_plural = 'Mpesa Deposits'

    def __str__(self):
        return self.phone_number
 


