from django.db import models

# Create your models for inventory.
class Category(models.Model):
    name = models.CharField(_("Categoria"), max_length=100, blank=False, null=False)

    def __str__(self):
        return self.name

