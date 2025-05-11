from django.db import models

# Create your models here.
class Stream(models.Model):
    url = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True,blank=True)

    def __str__(self):
        return self.url