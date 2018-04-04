from typing import Type

from django.db.models import *
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone

from mptt.models import MPTTModel, TreeForeignKey, TreeManager


class Category(MPTTModel):
    title = CharField(max_length=128)
    slug = SlugField()
    description = TextField(blank=True, null=True)

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class Meta:
        verbose_name_plural = 'Categories'

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self) -> str:
        return reverse('category_list', args=[self.slug])

    def get_descendant_categories(self, include_self: bool=True) -> Type[QuerySet]:
        """ Get this category and all it's decendents in a QuerySet """
        return self.get_descendants(include_self=include_self)

    def get_posts(self, published=False) -> Type[QuerySet]:
        """ Get all posts in this category and it's decendents """
        categories = self.get_descendant_categories()
        posts = Post.objects.filter(categories__in=categories)
        if published:
            posts = posts.filter(published__lte=timezone.now())
        return posts


class PostManager(Manager):
    def published_posts(self) -> Type[QuerySet]:
        """ Get all published posts order by most recent first """
        return Post.objects.filter(published__lt=timezone.now()).order_by('-published')

    def new_posts(self, number_posts=5) -> Type[QuerySet]:
        """ Get most recent x published posts """
        return self.published_posts()[:number_posts]

    def recent_posts(self, horizon: int=30) -> Type[QuerySet]:
        """ Get posts published in the last x days """
        delta = timezone.timedelta(horizon)
        start_date = timezone.now() - delta
        return self.published_posts().filter(published__gte=start_date)


class Post(Model):
    title = CharField(max_length=250)
    slug = SlugField()
    categories = ManyToManyField(Category, blank=True, related_name='posts')
    image = ImageField(upload_to='media/posts/', blank=True, null=True)
    excerpt = TextField(blank=True, null=True)
    content = TextField()

    author = ForeignKey(settings.AUTH_USER_MODEL)
    created = DateTimeField(auto_now_add=True)
    published = DateTimeField(blank=True, null=True)

    allow_comments = BooleanField(default=True)

    objects = PostManager()

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse('post_detail', args=[self.slug])

    def is_published(self) -> bool:
        """ Check if post is published """
        return self.published and self.published <= timezone.now()

    def published_after(self) -> Type[QuerySet]:
        """ Get posts published after this one """
        return Post.objects.filter(published__gt=self.published, published__lt=timezone.now()) if self.is_published() else Post.objects.none()

    def published_before(self) -> Type[QuerySet]:
        """ Get posts published before this one """
        return Post.objects.filter(published__lt=self.published) if self.is_published() else Post.objects.none()

    def has_next(self) -> bool:
        """ Check if there are posts after this one """
        return self.published_after().count() != 0

    def next_post(self) -> Type['Post']:
        """ Get next post """
        return self.published_after().order_by('-published')[0]

    def has_previous(self) -> bool:
        """ Check if there are posts before this one"""
        return self.published_before().count() != 0

    def previous_post(self) -> Type['Post']:
        """ Get previous post """
        return self.published_before().order_by('published')[0]

    def related_posts(self, number_items=5, include_ancestors=True) -> Type[QuerySet]:
        """ Get a random selection of posts that are related to this one by category (potentially ascendant categories) """
        if include_ancestors:
            categories = Category.objects.get_queryset_ancestors(self.categories.get_queryset())
        else:
            categories = self.categories.get_queryset()
        posts = Post.objects.published_posts().exclude(pk=self.pk).filter(categories__in=categories).order_by('?')[:number_items]
        return posts


class Comment(MPTTModel):
    content = TextField()
    author = ForeignKey(settings.AUTH_USER_MODEL, related_name='posts')
    created = DateTimeField(auto_now_add=True)
    score = IntegerField(default=0)
    voters = ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    post = ForeignKey(Post, related_name='comments')

    class MPTTMeta:
        order_insertion_by = ['created']

    class Meta:
        ordering = ['tree_id', 'lft']
