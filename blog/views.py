from typing import Dict, Type

from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.contrib.syndication.views import Feed
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import Post, Category, Comment
from .forms import CommentForm

POSTS_PER_PAGE = getattr(settings, 'POSTS_PER_PAGE', 10)
ARCHIVE_POSTS_PER_PAGE = getattr(settings, 'POSTS_PER_PAGE', 100)
BLOG_FEED_CONFIG = getattr(settings, 'BLOG_FEED', {
    'title': 'Latest Posts',
    'link': '/posts/',
    'description': 'The latest posts',
})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/list.html'
    paginate_by = POSTS_PER_PAGE
    queryset = Post.objects.published_posts()


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context


class PostArchiveListView(PostListView):
    paginate_by = ARCHIVE_POSTS_PER_PAGE
    template_name = 'blog/archive.html'

    def get_queryset(self) -> Type[QuerySet]:
        queryset = super().get_queryset()
        arg_count = len(self.args)
        if arg_count == 1:
            # filter by year
            year = int(self.args[0])
            return queryset.filter(published__year=year)
        elif arg_count == 2:
            # filter by month
            year = int(self.args[0])
            month = int(self.args[1])
            return queryset.filter(published__year=year, published__month=month)
        # default if anything else
        return queryset


class PostByCategoryListView(PostListView):
    def get_queryset(self)-> Type[QuerySet]:
        category = get_object_or_404(Category, slug=self.kwargs['category'])
        posts = category.get_posts(published=True)
        return posts


class PostByAuthorListView(PostListView):
    def get_queryset(self)-> Type[QuerySet]:
        user = get_object_or_404(get_user_model(), username=self.kwargs['username'])
        posts = Post.objects.published_posts().filter(author=user)
        return posts


class LatestPostsFeed(Feed):
    title = BLOG_FEED_CONFIG.get('title', 'Latest Posts')
    link = BLOG_FEED_CONFIG.get('link', '/posts/')
    description = BLOG_FEED_CONFIG.get('description', '')

    def items(self) -> Type[QuerySet]:
        return Post.objects.new_posts(number_posts=5)

    def item_title(self, item: Type[Post]) -> str:
        return item.title

    def item_description(self, item: Type[Post]) -> str:
        if item.excerpt:
            return item.excerpt
        return ''


@method_decorator(login_required, name='dispatch')
class CommentFormView(FormView):
    form_class = CommentForm

    def form_valid(self, form):
        slug = self.kwargs.get('slug')
        post = get_object_or_404(Post, slug=slug)
        content = form.cleaned_data['content']

        parent_id = self.kwargs.get('parent', None)
        if parent_id:
            parent = get_object_or_404(Comment, id=int(parent_id))
        else:
            parent = None

        comment = Comment.objects.create(
            content=content,
            author=self.request.user,
            parent=parent,
            post=post
        )
        return HttpResponseRedirect('{0}#{1}'.format(post.get_absolute_url(), comment.pk))