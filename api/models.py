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

    def to_dict(self):
        return {
            "id": self.pk,
            "constructor": self.constructor.pk if self.constructor is not None else None,
            "name": self.name,
            "architecture": self.architecture,
            "frequency": self.frequency,
            "core_count": self.core_count,
        }

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
    TYPE_CHOICES = {
        "sdr": "SDR",
        "ddr1": "DDR1",
        "ddr2": "DDR2",
        "ddr3": "DDR3",
        "ddr4": "DDR4",
        "ddr5": "DDR5",
    }

    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    size = models.PositiveBigIntegerField()
    frequency = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = "Memory Stick"
        verbose_name_plural = "Memory Sticks"
        ordering = ["constructor", "name"]

    def to_dict(self):
        return {
            "id": self.pk,
            "constructor": self.constructor.pk if self.constructor is not None else None,
            "name": self.name,
            "type": self.type,
            "size": self.size,
            "frequency": self.frequency,
        }

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
    TYPE_CHOICES = {
        "hdd": "HDD",
        "ssd": "SSD",
        "nvme": "NVMe",
        "emmc": "eMMC",
    }

    storage_type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    size = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = "Storage Device"
        verbose_name_plural = "Storage Devices"
        ordering = ["constructor", "name"]

    def to_dict(self):
        return {
            "id": self.pk,
            "constructor": self.constructor.pk if self.constructor is not None else None,
            "name": self.name,
            "type": self.storage_type,
            "size": self.size,
        }

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
    vram_size = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = "Graphics Card"
        verbose_name_plural = "Graphics Cards"
        ordering = ["constructor", "name"]

    def to_dict(self):
        return {
            "id": self.pk,
            "constructor": self.constructor.pk if self.constructor is not None else None,
            "name": self.name,
            "vram_size": self.vram_size,
        }

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
    TYPE_CHOICES = {
        "eth": "Ethernet",
        "wifi": "Wi-Fi",
    }

    network_type = models.CharField(min_length=100, choices=TYPE_CHOICES)
    speed = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = "Network Connection"
        verbose_name_plural = "Network Connections"
        ordering = ["constructor", "name"]

    def to_dict(self):
        return {
            "id": self.pk,
            "constructor": self.constructor.pk if self.constructor is not None else None,
            "name": self.name,
            "type": self.network_type,
            "speed": self.speed,
        }

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
