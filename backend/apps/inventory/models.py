from django.db import models
from apps.core.models import  CustomModel
from django.utils.text import slugify


# Category Model
class Category(CustomModel):
    name = models.CharField( "Categoria", max_length=50, blank=False, null=False, unique=True)
    description = models.CharField("Descripción", max_length=100, blank=True, null=False)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categorias'
        verbose_name = 'Categoria'
        ordering = ('name', )


# Product Model
class Product(CustomModel):
    name = models.CharField(verbose_name="Producto", max_length=100, blank=False, null=False, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    price = models.DecimalField('Precio', max_digits=5, decimal_places=2)
    image = models.ImageField('Imagen', upload_to='products', blank=True)
    description = models.TextField('Descripción', blank=True)
    has_stock = models.BooleanField('Tiene Inventario', default=False)
    category = models.ForeignKey(
        Category, verbose_name="Categoria", on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.name = self.name.title()
        super(Product, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


