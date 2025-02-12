from datetime import datetime
from django.db import models
from django.utils.timezone import now
from datetime import timedelta


class Website(models.Model):
    company = models.TextField()
    domain = models.CharField(max_length=200, null=True)
    url = models.CharField(max_length=200, null=True)
    token_page = models.CharField(max_length=250, null=True)
    source = models.CharField(max_length=250, null=True)
    emails_checked = models.BooleanField(default=False)
    updated_at = models.DateField(default=datetime.now)

    def __str__(self):
        return self.company


class EmailAddress(models.Model):
    website = models.ForeignKey(Website, related_name='email_addresses', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=250, null=True)
    email = models.EmailField(null=True)
    position = models.CharField(max_length=250, null=True)

    def __str__(self):
        return f'{self.email} - {self.website.company}'


class ParserStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Название парсера
    total_items = models.IntegerField(default=0)  # Общее количество элементов
    processed_items = models.IntegerField(default=0)  # Обработанные элементы
    status = models.CharField(
        max_length=50,
        choices=[
            ('idle', 'Idle'),
            ('running', 'Running')
        ],
        default='idle'
    )
    last_scraped_page = models.CharField(max_length=250, null=True)
    enabled = models.BooleanField(default=False)
    last_run = models.DateTimeField(default=datetime.now)

    def progress(self):
        """Вычисляет процент завершения"""
        if self.total_items == 0:
            return 0
        return int((self.processed_items / self.total_items) * 100)

    def __str__(self):
        return f"{self.name} - {self.get_status_display()} ({self.progress()}%)"


class MyModelManager(models.Manager):
    edit_access = True
    def get_queryset(self):
        if self.edit_access:
            self.edit_access = False
            threshold = now() - timedelta(hours=1)
            self.model.objects.filter(created_at__lt=threshold).delete()
            self.edit_access = True

        return super().get_queryset()


class ParsedWebsite(models.Model):
    parser = models.ForeignKey(ParserStatus, related_name='last_parsed', on_delete=models.CASCADE, null=True)
    url = models.CharField(max_length=250, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MyModelManager()

    def __str__(self):
        return f'{self.email} - {self.website.company}'
