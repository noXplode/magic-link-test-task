from django.db import models
import uuid


# Create your models here.
class EmailToken(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField("Email", max_length=100)
    created = models.DateTimeField("Token created", auto_now_add=True)
    entered = models.IntegerField("URL use count", default=0, editable=False)
    last_visited = models.DateTimeField("Last visit", auto_now=True)
    active = models.BooleanField("Access allowed", default=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.token}, {self.email}'

    def increase_visit(self):
        self.entered += 1
        self.save()
