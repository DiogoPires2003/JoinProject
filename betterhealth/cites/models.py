from django.db import models
from django.contrib.auth.models import User

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendent'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancel·lada'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.date.strftime('%d/%m/%Y %H:%M')}"
