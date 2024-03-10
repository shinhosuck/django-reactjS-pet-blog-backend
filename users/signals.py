from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from . models import Profile



# 
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs ):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs ):
    instance.profile.save()

    """
        user = request.user
        user.firstname = 'Newuser2'
        user.prfile.firstname = 'Newuser2'
        user.save()

        above snippet does not save profile.
        when the user info is saved, save_profile function will be triggered
        and saves the user's profile as well.
    """
