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

class ComputerProcessor(models.Model):
    computer = models.ForeignKey(
        "Computer",
        on_delete=models.CASCADE
    )

    processor = models.ForeignKey(
        Processor,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveSmallIntegerField(default=1)

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

class ComputerMemory(models.Model):
    computer = models.ForeignKey(
        "Computer",
        on_delete=models.CASCADE
    )

    memory = models.ForeignKey(
        Memory,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveSmallIntegerField(default=1)

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

class ComputerStorage(models.Model):
    computer = models.ForeignKey(
        "Computer",
        on_delete=models.CASCADE
    )

    storage = models.ForeignKey(
        Storage,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveSmallIntegerField(default=1)

class GraphicsCard(Component):
    class Meta:
        verbose_name = "Graphics Card"
        verbose_name_plural = "Graphics Cards"
        ordering = ["constructor", "name"]

class ComputerGraphicsCard(models.Model):
    computer = models.ForeignKey(
        "Computer",
        on_delete=models.CASCADE
    )

    graphics_card = models.ForeignKey(
        GraphicsCard,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveSmallIntegerField(default=1)

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

class ComputerNetwork(models.Model):
    computer = models.ForeignKey(
        "Computer",
        on_delete=models.CASCADE
    )

    network = models.ForeignKey(
        Network,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveSmallIntegerField(default=1)

class Computer(models.Model):
    SITE_CHOICES = {
        "ldlc": "LDLC",
    }

    FORMAT_CHOICES = {
        "desktop": "Desktop",
        "laptop": "Laptop",
        "rack": "Rack",
        "mini": "Mini PC",
        "tablet": "Tablet"
    }

    site = models.CharField(max_length=100, choices=SITE_CHOICES)
    constructor = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=150, blank=True)
    model_number = models.CharField(max_length=150, blank=True)
    serial_number = models.CharField(max_length=150, blank=True)
    format = models.CharField(max_length=100, choices=FORMAT_CHOICES)

    processors = models.ManyToManyField(
        Processor,
        through=ComputerProcessor,
        blank=True
    )

    memory = models.ManyToManyField(
        Memory,
        through=ComputerMemory,
        blank=True
    )

    storage = models.ManyToManyField(
        Storage,
        through=ComputerStorage,
        blank=True
    )

    graphics_card = models.ManyToManyField(
        GraphicsCard,
        through=ComputerGraphicsCard,
        blank=True
    )

    network = models.ManyToManyField(
        Network,
        through=ComputerNetwork,
        blank=True
    )

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
            "constructor": self.constructor.pk if self.constructor is not None else None,
            "name": self.name,
            "model_number": self.model_number,
            "serial_number": self.serial_number,
            "format": self.format,
            "processors": [
                {
                    "id": processor.processor_id,
                    "quantity": processor.quantity,
                }
                for processor in ComputerProcessor.objects.filter(computer=self)
            ],
            "memory": [
                {
                    "id": memory.memory_id,
                    "quantity": memory.quantity,
                }
                for memory in ComputerMemory.objects.filter(computer=self)
            ],
            "storage": [
                {
                    "id": storage.storage_id,
                    "quantity": storage.quantity,
                }
                for storage in ComputerStorage.objects.filter(computer=self)
            ],
            "graphics_card": [
                {
                    "id": graphics_card.graphics_card_id,
                    "quantity": graphics_card.quantity
                }
                for graphics_card in ComputerGraphicsCard.objects.filter(computer=self)
            ],
            "network": [
                {
                    "id": network.graphics_card_id,
                    "quantity": network.quantity
                }
                for network in ComputerNetwork.objects.filter(computer=self)
            ],
        }
