from django.db import models

def extract_mtm_pk(field: models.ManyToManyField):
    return list(map(lambda x: x.pk, field.all()))

class Company(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField(blank=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["name"]
    
    def __str__(self):
        return self.name
    
    def to_dict(id):
        company = Company.objects.get(pk=id)

        return {
            "id": id,
            "name": company.name,
            "website": company.website,
        }

class Component(models.Model):
    name = models.CharField(max_length=200, blank=True)
    constructor = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["constructor", "name"]

    def __str__(self):
        return f"{self.constructor} {self.name}"

class Processor(Component):
    class Architecture(models.IntegerChoices):
        X86 = 0, 'x86 (32-bit)'
        AMD64 = 1, 'AMD64 (64-bit)'
        ARM = 2, 'ARM'

    architecture = models.PositiveSmallIntegerField(choices=Architecture)
    frequency = models.PositiveBigIntegerField()
    core_count = models.PositiveSmallIntegerField()

class Memory(Component):
    class MemoryType(models.IntegerChoices):
        UNKNOWN = 0, "N/A"
        SDR = 1, "SDR"
        DDR1 = 2, "DDR1"
        DDR2 = 3, "DDR2"
        DDR3 = 4, "DDR3"
        DDR4 = 5, "DDR4"
        DDR5 = 6, "DDR5"

    type = models.PositiveSmallIntegerField(choices=MemoryType)
    size = models.PositiveBigIntegerField()
    frequency = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = "Memory Stick"
        verbose_name_plural = "Memory Sticks"
        ordering = ["constructor", "name"]

class Storage(Component):
    class StorageType(models.IntegerChoices):
        HDD = 0, "HDD"
        SSD = 1, "SSD"
        NVME = 2, "NVMe"
        EMMC = 3, "eMMC"

    storage_type = models.PositiveSmallIntegerField(choices=StorageType)
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
    class NetworkType(models.IntegerChoices):
        ETH = 0, "Ethernet"
        WIFI = 1, "Wi-Fi"

    network_type = models.PositiveSmallIntegerField(choices=NetworkType)
    speed = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = "Network Connection"
        verbose_name_plural = "Network Connections"
        ordering = ["constructor", "name"]

class Computer(models.Model):
    class Site(models.IntegerChoices):
        LDLC = 0, 'LDLC'

    class Format(models.IntegerChoices):
        DESKTOP = 0, "Desktop"
        LAPTOP = 1, "Laptop"
        RACK = 2, "Rack"
        MINI = 3, "Mini PC"
        TABLET = 4, "Tablet"

    site = models.PositiveSmallIntegerField(choices=Site)
    constructor = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=150, blank=True)
    model_number = models.CharField(max_length=150, blank=True)
    serial_number = models.CharField(max_length=150, blank=True)
    format = models.PositiveSmallIntegerField(choices=Format)

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

    def to_dict(self):
        print(self.processors)

        return {
            "id": self.pk,
            "site": self.site,
            "constructor": self.constructor.pk,
            "name": self.name,
            "model_number": self.model_number,
            "serial_number": self.serial_number,
            "format": self.format,
            "processors": extract_mtm_pk(self.processors),
            "memory": extract_mtm_pk(self.memory),
            "storage": extract_mtm_pk(self.storage),
            "graphics_card": extract_mtm_pk(self.graphics_card),
            "network": extract_mtm_pk(self.network),
        }
