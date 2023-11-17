import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from news.models import Comment, News


TEST_COMMENTS_AMOUNT = 2


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )

    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст'
    )

    return comment


@pytest.fixture
def news_pk_for_args(news):
    return (news.pk, )


@pytest.fixture
def comment_pk_for_args(comment):
    return (comment.pk, )


@pytest.fixture
def create_news():
    today = datetime.today()

    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def create_comments(news, author):
    now = timezone.now()

    for index in range(TEST_COMMENTS_AMOUNT):

        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )

        comment.created = now + timedelta(days=index)

        comment.save()


@pytest.fixture
def news_detail_url(news_pk_for_args):
    url = reverse('news:detail', args=news_pk_for_args)

    return url


@pytest.fixture
def delete_comment_url(comment_pk_for_args):
    url = reverse('news:delete', args=comment_pk_for_args)

    return url


@pytest.fixture
def to_comments_url(news_pk_for_args):
    url = reverse('news:detail', args=news_pk_for_args) + '#comments'

    return url


@pytest.fixture
def edit_comment_url(comment_pk_for_args):
    edit_url = reverse('news:edit', args=comment_pk_for_args)

    return edit_url


@pytest.fixture
def form_data():
    return {
        'text': 'Текст комментария'
    }
