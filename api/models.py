from django.db import models

class Company(models.Model):
    name = models.CharField("name of the company", max_length=200)

    def __str__(self):
        return self.name

class Component(models.Model):
    name = models.CharField("name of the component", max_length=200)
    constructor = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.constructor} {self.name}"

class Computer(models.Model):
    name = models.CharField("name of the computer", max_length=200)
    components = models.ManyToManyField(Component)

    def __str__(self):
        return self.name
