from django.db import models
from django.db.models import CASCADE

from apps.core.models import CustomModel

# Platform Model.
class Platform(CustomModel):
    name = models.CharField(verbose_name="Red Social", blank=False, null=False, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super(Platform, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Redes Sociales'
        verbose_name = 'Red Social'
        ordering = ('name',)

# Content Type model, post, reels
class ContentType(CustomModel):
    name = models.CharField(verbose_name="Contenido", blank=False, null=False, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super(ContentType, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Tipo de contenido'


class StatusChoices(models.TextChoices):
    DRAFT = "draft", "Borrador"
    IN_DESIGN = "in_design", "En diseño"
    SCHEDULED = "scheduled", "Programado"
    PUBLISHED = "published", "Publicado"
    CANCELED = "canceled", "Cancelado"


class SocialPost(CustomModel):
    title = models.CharField(verbose_name="Titulo", blank=False, null=False)
    platform = models.ManyToManyField(Platform, verbose_name="Redes Sociales")
    content_type = models.OneToOneField(ContentType, verbose_name="Tipo de contenido", on_delete=models.CASCADE)
    copy = models.TextField()
    cta_text = models.TextField()
    status = models.CharField("Estado", max_length=20, choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    scheduled_for = models.DateTimeField(verbose_name="Programado para", null=True, blank=True)

    class Meta:
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'