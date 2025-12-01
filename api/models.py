from django.db import models

# Create your models here.
class Computer(models.Model):
    name = models.CharField("name of the computer", max_length=200)

    def __str__(self):
        return self.name
