from django.urls import path

from .views import (RegisterView, add_comment, category_posts, create_post,
                    delete_comment, delete_post, edit_comment, edit_post,
                    edit_profile, index, post_detail, profile)

app_name = 'blog'

urlpatterns = [
    path('', index, name='index'),
    path('posts/create/', create_post, name='create_post'),
    path('posts/<int:id>/', post_detail, name='post_detail'),
    path('posts/<int:id>/edit/', edit_post, name='edit_post'),
    path('posts/<int:id>/delete/', delete_post, name='delete_post'),
    path('posts/<int:id>/comment/', add_comment, name='add_comment'),
    path(
        'posts/<int:id>/edit_comment/<int:comment_id>/',
        edit_comment,
        name='edit_comment'
    ),
    path(
        'posts/<int:id>/delete_comment/<int:comment_id>/',
        delete_comment,
        name='delete_comment'
    ),
    path(
        'category/<slug:category_slug>/',
        category_posts,
        name='category_posts'
    ),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/<str:username>/', profile, name='profile'),
    path('auth/registration/', RegisterView.as_view(), name='registration'),
]
