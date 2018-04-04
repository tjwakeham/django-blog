## Django blog app 

A reference implementation of a Django blog app with threaded comments and fully categorised and archived posts.

### Requirements

* `django_summernote`
* `easy_thumbnail`
* `django-mptt`

### Installation

Add `blog`, `easy_thumbnail', `mptt`, `django_summernote` to `installed_apps`

Add the required context processors

```python
TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'blog.context_processors.category.categories',
                'blog.context_processors.post.posts'
            ],
        },
    },
]
```

Run `python manage.py migrate`

Run `python manage.py collectstatic`