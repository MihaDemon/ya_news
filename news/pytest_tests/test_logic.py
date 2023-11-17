from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, news_detail_url
):
    client.post(news_detail_url, data=form_data)
    comments_count = Comment.objects.count()

    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(
    admin_client, admin_user, news, news_detail_url, form_data
):
    response = admin_client.post(news_detail_url, data=form_data)

    assertRedirects(response, f'{news_detail_url}#comments')

    comments_count = Comment.objects.count()

    assert comments_count == 1

    comment = Comment.objects.get()

    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == admin_user


@pytest.mark.django_db
def test_user_cant_use_bad_words(admin_client, news_detail_url):
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    }
    response = admin_client.post(news_detail_url, data=bad_words_data)

    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )

    comment_count = Comment.objects.count()

    assert comment_count == 0


def test_author_can_delete_comment(
        author_client, delete_comment_url, to_comments_url, comment
):
    response = author_client.delete(delete_comment_url)
    expected_url = to_comments_url

    assertRedirects(response, expected_url)

    comments_count = Comment.objects.count()

    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
    admin_client, delete_comment_url, comment
):
    response = admin_client.delete(delete_comment_url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comments_count = Comment.objects.count()

    assert comments_count == 1


def test_author_can_edit_comment(
    author_client, edit_comment_url, form_data, to_comments_url, comment
):
    response = author_client.post(edit_comment_url, data=form_data)

    assertRedirects(response, to_comments_url)

    comment.refresh_from_db()

    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
    admin_client, edit_comment_url, form_data, comment
):
    response = admin_client.post(edit_comment_url, data=form_data)
    comment_text = Comment.objects.get().text

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()

    assert comment.text == comment_text
