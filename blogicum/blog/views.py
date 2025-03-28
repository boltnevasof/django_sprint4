from blog.models import Post
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import now
from django.views.generic import CreateView

from .forms import (CommentForm, CustomUserCreationForm, PostForm,
                    ProfileEditForm)
from .models import Category, Comment, Post

POSTS_PER_PAGE = 10  # Константа для количества постов на главной


# def index(request):
#     """Главная страница - 5 последних публикаций."""
#     page_obj = Post.objects.published().with_relations()[:POSTS_PER_PAGE]

#     return render(request, 'blog/index.html', {'page_obj': page_obj})

def index(request):
    post_list = (Post.objects.published().with_relations()
                 .annotate(comment_count=Count('comments'))
                 .order_by('-pub_date'))
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


# def category_posts(request, category_slug):
#     """Страница категории: публикации выбранной категории."""
#     category = get_object_or_404(
#         Category,
#         slug=category_slug,
#         is_published=True
#     )

#     post_list = Post.objects.published().with_relations().filter(
#         category=category
#     )

#     return render(
#         request, 'blog/category.html',
#         {'category': category,
#          'post_list': post_list,
#          'category_slug': category.slug}
#     )
def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = (Post.objects.published().with_relations().
                 filter(category=category)
                 .annotate(comment_count=Count('comments'))
                 .order_by('-pub_date'))
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj,
        'category_slug': category.slug
    })


def post_detail(request, id):
    post = get_object_or_404(Post.objects.with_relations(), id=id)

    # Если пост не опубликован, запланирован на будущее
    # или категория снята с публикации — и юзер не автор 404
    if (
        not post.is_published
        or post.pub_date > timezone.now()
        or (post.category and not post.category.is_published)
    ):
        if request.user != post.author:
            raise Http404("Пост недоступен")

    form = CommentForm()
    comments = post.comments.all()

    return render(request, 'blog/detail.html', {
        'post': post,
        'form': form,
        'comments': comments,
    })


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


def profile(request, username):
    profile = get_object_or_404(User, username=username)

    if request.user == profile:
        post_list = (
            Post.objects.filter(author=profile)
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')  # сортировка от новых к старым
        )
    else:
        post_list = (
            Post.objects.filter(
                author=profile,
                is_published=True,
                pub_date__lte=now()
            )
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')  # сортировка от новых к старым
        )

    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/profile.html', {
        'profile': profile,
        'page_obj': page_obj,
    })


@login_required
def edit_profile(request):
    user = request.user
    form = ProfileEditForm(request.POST or None, instance=user)

    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=user.username)

    return render(
        request,
        'registration/registration_form.html',
        {'form': form}
    )


def edit_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user != post.author:
        return redirect('blog:post_detail', id=post.id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=post.id)

    return render(request, 'blog/create.html', {'form': form, 'is_edit': True})


# Добавление комментария
@login_required
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id=id)


# Редактирование комментария
@login_required
def edit_comment(request, id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=id)
    if comment.author != request.user:
        return redirect('blog:post_detail', id=id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=id)
    return render(
        request,
        'blog/comment.html',
        {'form': form, 'comment': comment}
    )


# Удаление комментария
@login_required
def delete_comment(request, id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=id)
    if comment.author != request.user:
        return redirect('blog:post_detail', id=id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=id)
    return render(request, 'blog/comment.html', {'comment': comment})


@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user != post.author:
        return redirect('blog:post_detail', id=post.id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/create.html', {
        'post': post,
        'form': None,
        'is_delete': True
    })


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')
