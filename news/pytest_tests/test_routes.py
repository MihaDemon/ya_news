import pytest
from pytest_django.asserts import assertRedirects
from http import HTTPStatus

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('name', 'args'),
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_pk_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    ),
    ids=(
        'home',
        'detail',
        'login',
        'logout',
        'signup'
    )
)
def test_pages_availability(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    ('parametrized_client', 'expected_status'),
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND)
    ),
    ids=(
        'author',
        'admin'
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
    ids=('edit', 'delete')
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, comment_pk_for_args, name
):
    url = reverse(name, args=comment_pk_for_args)
    response = parametrized_client.get(url)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
    ids=('edit', 'delete')
)
def test_redirect_for_anonymous_client(client, name, comment_pk_for_args):
    login_url = reverse('users:login')
    url = reverse(name, args=comment_pk_for_args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)

    assertRedirects(response, expected_url)
