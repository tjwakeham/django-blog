from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from blog.models import Post, Category

one_day = timezone.timedelta(1)
one_year = timezone.timedelta(365)
yesterday = timezone.now() - one_day
one_year_ago = timezone.now() - one_year
tomorrow = timezone.now() + one_day


class BlogTestCases(TestCase):
    def setUp(self):
        user = get_user_model().objects.create(username='testuser', email='test@test.com', is_superuser=True)
        self.category_a = Category.objects.create(title='Cat A', slug='cat-a')
        self.category_b = Category.objects.create(title='Cat B', slug='cat-b', parent=self.category_a)

        self.published_1 = Post.objects.create(title='Test Post 1',
                                               slug='test-post-1',
                                               published=one_year_ago,
                                               author=user)
        self.published_1.categories.add(self.category_a)

        self.published_2 = Post.objects.create(title='Test Post 2',
                                               slug='test-post-2',
                                               published=yesterday,
                                               author=user)
        self.published_2.categories.add(self.category_b)

        self.future_publish_date = Post.objects.create(title='Test Post 3',
                                                       slug='test-post-3',
                                                       published=tomorrow,
                                                       author=user)
        self.future_publish_date.categories.add(self.category_a)

        self.not_published = Post.objects.create(title='Test Post 4',
                                                 slug='test-post-4',
                                                 author=user)

    def test_post_is_published(self):
        self.assertTrue(self.published_1.is_published())
        self.assertFalse(self.future_publish_date.is_published())
        self.assertFalse(self.not_published.is_published())

    def test_post_published_posts(self):
        posts = Post.objects.published_posts()
        self.assertQuerysetEqual(posts, ['<Post: Test Post 1>', '<Post: Test Post 2>'], ordered=False)

    def test_post_new_posts(self):
        posts = Post.objects.new_posts()
        self.assertQuerysetEqual(posts, ['<Post: Test Post 1>', '<Post: Test Post 2>'], ordered=False)

    def test_post_recent_posts(self):
        posts = Post.objects.recent_posts()
        self.assertQuerysetEqual(posts, ['<Post: Test Post 2>'], ordered=False)

    def test_post_has_next(self):
        self.assertTrue(self.published_1.has_next())
        self.assertFalse(self.published_2.has_next())
        self.assertFalse(self.future_publish_date.has_next())
        self.assertFalse(self.not_published.has_next())

    def test_post_next_post(self):
        self.assertEqual(self.published_2, self.published_1.next_post())
        with self.assertRaises(IndexError):
            self.published_2.next_post()

    def test_post_has_previous(self):
        self.assertFalse(self.published_1.has_previous())
        self.assertTrue(self.published_2.has_previous())
        self.assertFalse(self.future_publish_date.has_previous())
        self.assertFalse(self.not_published.has_previous())

    def test_post_related_posts(self):
        posts = self.published_2.related_posts(number_items=5, include_ancestors=True)
        self.assertQuerysetEqual(posts, ['<Post: Test Post 1>'])
        posts = self.published_2.related_posts(number_items=5, include_ancestors=False)
        self.assertQuerysetEqual(posts, [])

    def test_get_descendant_categories(self):
        categories = self.category_a.get_descendant_categories(include_self=True)
        self.assertQuerysetEqual(categories, ['<Category: Cat A>', '<Category: Cat B>'])
        categories = self.category_a.get_descendant_categories(include_self=False)
        self.assertQuerysetEqual(categories, ['<Category: Cat B>'])

    def test_category_get_posts(self):
        posts = self.category_a.get_posts(published=True)
        self.assertQuerysetEqual(posts, ['<Post: Test Post 1>', '<Post: Test Post 2>'], ordered=False)
        posts = self.category_a.get_posts()
        self.assertQuerysetEqual(posts, ['<Post: Test Post 1>', '<Post: Test Post 2>', '<Post: Test Post 3>'],
                                 ordered=False)
        posts = self.category_b.get_posts()
        self.assertQuerysetEqual(posts, ['<Post: Test Post 2>'], ordered=False)