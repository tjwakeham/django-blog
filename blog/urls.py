from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r'^$', PostListView.as_view(), name='post_list'),
    url(r'^rss/$', LatestPostsFeed(), name='post_feed'),

    url(r'^post/(?P<slug>[a-zA-Z0-9\-]+)$', PostDetailView.as_view(), name='post_detail'),

    url(r'^archive/$', PostArchiveListView.as_view(), name='post_archive'),
    url(r'^archive/([0-9]{4})$', PostArchiveListView.as_view(), name='post_archive_year'),
    url(r'^archive/([0-9]{4})/(10|11|12|[1-9])/$', PostArchiveListView.as_view(), name='post_archive_month'),

    url(r'^category/(?P<category>[a-zA-Z0-9\-]+)$', PostByCategoryListView.as_view(), name='post_by_category_list'),

    url(r'^author/(?P<username>[a-zA-Z0-9\-]+)$', PostByAuthorListView.as_view(), name='post_by_author_list'),

    url(r'^comment/add/(?P<slug>[a-zA-Z0-9\-]+)$', CommentFormView.as_view(), name='post_add_comment'),
    url(r'^comment/add/(?P<slug>[a-zA-Z0-9\-]+)/(?P<parent>[0-9]+)$', CommentFormView.as_view(), name='post_add_comment_to_parent')
]

