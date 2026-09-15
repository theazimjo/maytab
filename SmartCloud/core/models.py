import uuid
import random
import sys
from io import BytesIO
from PIL import Image
from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from .utils import generate_hikvision_id


class School(models.Model):
    name = models.CharField(max_length=255, verbose_name="Maktab nomi")
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name="Oxirgi aloqa")

    def __str__(self):
        return self.name

    @property
    def is_online(self):
        if not self.last_activity:
            return False
        diff = timezone.now() - self.last_activity
        return diff.total_seconds() < 600


class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="students")
    full_name = models.CharField(max_length=255)
    hikvision_id = models.CharField(
        max_length=20,
        editable=False,
        verbose_name="Terminal ID"
    )
    photo = models.ImageField(
        upload_to='students/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        verbose_name="Yuz rasmi"
    )
    is_synced = models.BooleanField(default=False)

    class Meta:
        unique_together = ['school', 'hikvision_id']

    def __str__(self):
        return f"{self.full_name} ({self.school.name})"

    def save(self, *args, **kwargs):
        if not self.hikvision_id:
            self.hikvision_id = generate_hikvision_id(self.school, Student, start_range=10000)

        if self.photo:
            try:
                img = Image.open(self.photo)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size)

                output_io = BytesIO()
                quality = 90
                img.save(output_io, format='JPEG', quality=quality)

                while output_io.tell() > 150 * 1024 and quality > 10:
                    output_io.seek(0)
                    output_io.truncate()
                    quality -= 10
                    img.save(output_io, format='JPEG', quality=quality)

                new_image = InMemoryUploadedFile(
                    output_io,
                    'ImageField',
                    f"{self.photo.name.split('.')[0]}.jpg",
                    'image/jpeg',
                    sys.getsizeof(output_io),
                    None
                )
                self.photo = new_image
            except Exception as e:
                print(f"Image Compression Error: {e}")

        super().save(*args, **kwargs)
