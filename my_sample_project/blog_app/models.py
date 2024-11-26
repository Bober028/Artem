from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


class PublishedPostsManager(models.Manager):
    """Менеджер для вибору лише опублікованих постів."""
    def get_queryset(self):
        return super().get_queryset().filter(status=BlogPost.PublicationStatus.PUBLISHED)


class BlogPost(models.Model):
    """Модель для постів блогу."""
    class Meta:
        ordering = ['-published_at']

    class PublicationStatus(models.TextChoices):
        DRAFT = "D", _("Draft")
        PUBLISHED = "P", _("Published")

    status = models.CharField(
        max_length=1,
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
    )
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    text = models.TextField(verbose_name=_("Content"))
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Author"))
    slug = models.SlugField(unique_for_date='created_at', blank=False, verbose_name=_("Slug"))
    published_at = models.DateTimeField(default=timezone.now, verbose_name=_("Published At"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    tags = TaggableManager(verbose_name=_("Tags"))  # Поле для тегів

    # Менеджери
    objects = models.Manager()  # Стандартний менеджер
    published_objects = PublishedPostsManager()  # Менеджер для публікацій

    def __str__(self):
        return f"{self.title} | by {self.owner.username}"

    def get_absolute_url(self):
        """Повертає URL для конкретного поста."""
        return reverse(
            'blog_app:post',
            args=[
                self.created_at.year,
                self.created_at.month,
                self.created_at.day,
                self.slug
            ]
        )

    def save(self, *args, **kwargs):
        """Автоматичне оновлення часу публікації та генерація slug."""
        if self.pk:
            previous = BlogPost.objects.get(pk=self.pk)
            if previous.status == BlogPost.PublicationStatus.DRAFT and \
               self.status == BlogPost.PublicationStatus.PUBLISHED:
                self.published_at = timezone.now()
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Comment(models.Model):
    """Модель для коментарів до постів."""
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_("Post")
    )
    name = models.CharField(max_length=80, verbose_name=_("Name"))
    email = models.EmailField(verbose_name=_("Email"))
    body = models.TextField(verbose_name=_("Comment"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['created_at'])]
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
