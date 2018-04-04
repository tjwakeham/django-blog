from typing import *
if TYPE_CHECKING:
    from django.db.models import QuerySet

from django.utils import timezone
from django.contrib.admin import *
from django.db.models import TextField

from mptt.admin import DraggableMPTTAdmin
from django_summernote.admin import SummernoteModelAdmin

from .models import Category, Post


class CategoryAdmin(DraggableMPTTAdmin):
    search_fields = ['title']
    list_display = ['tree_actions', 'indented_title', 'title', 'slug']
    prepopulated_fields = {'slug': ('title', )}
    mptt_indent_field = 'title'


site.register(Category, CategoryAdmin)


class PublishedListFilter(SimpleListFilter):
    title = 'Published'
    parameter_name = 'published'

    def lookups(self, request, model_admin) -> Tuple:
        return (
            ('No', 'Not Published'),
            ('Yes', 'Published'),
            ('Schedule', 'Scheduled')
        )

    def queryset(self, request, queryset) -> Type['QuerySet']:
        value = self.value()
        if not value:
            return queryset
        if value == 'No':
            return queryset.filter(published__isnull=True)
        elif value == 'Yes':
            return queryset.filter(published__lt=timezone.now())
        elif value == 'Schedule':
            return queryset.filter(published__gt=timezone.now())
        return queryset


class PostAdmin(SummernoteModelAdmin):
    search_fields = ['title']
    list_filter = ['author', 'categories', PublishedListFilter]
    list_display = ['title', 'slug', 'author', 'created', 'published']
    filter_horizontal = ['categories']
    prepopulated_fields = {'slug': ('title',)}
    summer_note_fields = '__all__'
    fieldsets = (
        ('Post Content', {'fields': ['title', 'content', 'excerpt', 'image', 'categories']}),
        ('Publication details', {'fields': ['author', 'published', 'slug', 'allow_comments']})
    )


site.register(Post, PostAdmin)
