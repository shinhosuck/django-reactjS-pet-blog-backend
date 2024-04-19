from django.db import models
from PIL import Image
from django.contrib.auth.models import User 




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="user_images/default.png", upload_to="user_images", null=True, blank=True)
    # image_url = models.URLField(null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"


    def save(self, *args, **kwargs):
        if not self.image:
            self.image = 'user_images/default.png'
        super(Profile, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.width > 400 or img.height > 400:
            new_img = (300, 300)
            img.thumbnail(new_img)
            img.save(self.image.path)
