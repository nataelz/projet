from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField(blank=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["name"]
    
    def __str__(self):
        return self.name

class Component(models.Model):
    name = models.CharField(max_length=200, blank=True)
    constructor = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["constructor", "name"]

    def __str__(self):
        return f"{self.constructor} {self.name}"

class Processor(Component):
    ARCHITECTURE_CHOICES = [
        ("x86", "x86 (32-bit)"),
        ("x86-64", "x86-64 (64-bit)"),
        ("arm", "ARM")
    ]

    architecture = models.CharField(max_length=10, choices=ARCHITECTURE_CHOICES)
    frequency = models.PositiveBigIntegerField()
    core_count = models.PositiveSmallIntegerField()

class Memory(Component):
    MEMORY_TYPE = (
        ("sdr", "SDR"),
        ("ddr1", "DDR1"),
        ("ddr2", "DDR2"),
        ("ddr3", "DDR3"),
        ("ddr4", "DDR4"),
        ("ddr5", "DDR5")
    )
    size = models.PositiveBigIntegerField()
    frequency = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = "Memory Stick"
        verbose_name_plural = "Memory Sticks"
        ordering = ["constructor", "name"]

class Storage(Component):
    STORAGE_TYPE_CHOICES = [
        ("hdd", "HDD"),
        ("ssd", "SSD"),
        ("nvme", "NVMe"),
        ("eMMC", "eMMC")
    ]

    storage_type = models.CharField(max_length=10, choices=STORAGE_TYPE_CHOICES)
    size = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = "Storage Device"
        verbose_name_plural = "Storage Devices"
        ordering = ["constructor", "name"]

class GraphicsCard(Component):
    class Meta:
        verbose_name = "Graphics Card"
        verbose_name_plural = "Graphics Cards"
        ordering = ["constructor", "name"]

class Network(Component):
    NETWORK_TYPE_CHOICES = [
        ("ethernet", "Ethernet"),
        ("wifi", "Wi-Fi")
    ]

    network_type = models.CharField(max_length=10, choices=NETWORK_TYPE_CHOICES)
    speed = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = "Network Connection"
        verbose_name_plural = "Network Connections"
        ordering = ["constructor", "name"]

class Computer(models.Model):
    FORMAT_CHOICES = [
        ("desktop", "Desktop"),
        ("laptop", "Laptop"),
        ("rack", "Rack-Mounted"),
        ("mini", "Mini PC"),
        ("tablet", "Tablet")
    ]

    SITE_CHOICES =[
        ("ldlc", "LDLC")
    ]

    site = models.CharField(max_length=15, choices=SITE_CHOICES)
    constructor = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=150, blank=True)
    model_number = models.CharField(max_length=150, blank=True)
    serial_number = models.CharField(max_length=150, blank=True)
    format = models.CharField(max_length=15, choices=FORMAT_CHOICES)

    processors = models.ManyToManyField(Processor, blank=True)

    memory = models.ManyToManyField(Memory, blank=True)

    storage = models.ManyToManyField(Storage, blank=True)

    graphics_card = models.ManyToManyField(GraphicsCard, blank=True)

    network = models.ManyToManyField(Network, blank=True)

    class Meta:
        ordering = ["constructor", "model_number", "serial_number", "name"]

    def __str__(self):
        out = ""

        if self.constructor != None:
            out += f"{self.constructor} "
        
        if self.name != None:
            out += f"{self.name}"
        elif self.model_number:
            out += f"{self.model_number}"
        
        return out
