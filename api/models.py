from django.db import models

class Company(models.Model):
    name = models.CharField("name of the company", max_length=200)

    def __str__(self):
        return self.name

class Component(models.Model):
    name = models.CharField("name of the component", max_length=200)
    constructor = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

class Processor(Component):
    core_count = models.PositiveSmallIntegerField("Number of cores")

class Memory(Component):
    MEMORY_KIND_CHOICES = {
        "1": "DDR1",
        "2": "DDR2",
        "3": "DDR3",
        "4": "DDR4",
        "5": "DDR5"
    }

    kind = models.CharField(max_length=1, choices=MEMORY_KIND_CHOICES)
    size = models.PositiveBigIntegerField("Capacity")
    speed = models.PositiveBigIntegerField("Speed")

class Drive(Component):
    DRIVE_KIND_CHOICES = {
        "H": "HDD",
        "S": "SSD"
    }
    kind = models.CharField(max_length=1, choices=DRIVE_KIND_CHOICES)
    size = models.PositiveBigIntegerField("Capacity")

class GraphicsCard(Component):
    pass

class Computer(models.Model):
    name = models.CharField("name of the computer", max_length=200)
    components = models.ManyToManyField(Component)

    def __str__(self):
        return self.name
