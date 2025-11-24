from django.db import models
from django.utils.text import slugify
from django.core.validators import URLValidator  # Валидатор для URL


class Phone(models.Model):
    # id поле будет создано автоматически как AutoField (основной ключ)
    name = models.CharField(max_length=255, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.URLField(validators=[URLValidator()], verbose_name="URL изображения")
    release_date = models.DateField(verbose_name="Дата выпуска")
    lte_exists = models.BooleanField(default=False, verbose_name="Есть поддержка LTE")
    slug = models.SlugField(unique=True, blank=True, max_length=255, verbose_name="Slug (URL)")  # max_length для slug

    def save(self, *args, **kwargs):
        # Автоматическая генерация slug на основе name, если slug не установлен
        if not self.slug and self.name:
            self.slug = slugify(self.name)


        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']  # По умолчанию сортируем по названию в алфавитном порядке
        verbose_name = "Телефон"
        verbose_name_plural = "Телефоны"