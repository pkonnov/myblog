from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Article, Comment
from .forms import ArticleForm, CommentForm

from django.views.generic.list import ListView

def ger_articles_page(articles, request):
    paginator = Paginator(articles, 4)
    page = request.GET.get('page')
    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        articles_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        articles_page = paginator.page(paginator.num_pages)
    return articles_page


def article_list(request, categoryName='', authorName=''):
    mode_list = 'simple'

    articles = Article.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    if categoryName:
        articles = articles.filter(category__urlstext=categoryName)
    if authorName:
        articles = articles.filter(author__username=authorName)

    return render(request, 'blog/article_list.html', {'articles': ger_articles_page(articles, request), 'mode_list':mode_list})


def search_list(request):
    mode_list = 'search'

    if 'srchtxt' in request.GET:
        message = 'You searched for: %r' % request.GET['srchtxt']
        srchtxt = request.GET['srchtxt']
    else:
        message = 'You submitted an empty form.'
        srchtxt = ''

    articles = ''
    if srchtxt:
        articles = Article.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
        articles = articles.filter(text__icontains=srchtxt)

    return render(request, 'blog/article_list.html', {'articles': ger_articles_page(articles, request), 'mode_list':mode_list, 'message': message, 'srchtxt':srchtxt })


def article_date_list(request, year=2017, month=9, day=22):
    articles = Article.objects.filter(published_date__lte=timezone.now()).filter(published_date__year=year).filter(published_date__month=month).filter(published_date__day=day).order_by('published_date')

    return render(request, 'blog/article_list.html', {'articles': ger_articles_page(articles, request)})


@login_required
def article_draft_list(request):
    mode_list = 'draft'
    articles = Article.objects.filter(published_date__isnull=True).order_by('created_date')

    return render(request, 'blog/article_list.html', {'articles': ger_articles_page(articles, request), 'mode_list': mode_list})


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.save()
            return redirect('blog:article_detail', pk=article.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/article_detail.html', {'article': article, 'form': form})


@login_required
def article_new(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('blog:article_detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'blog/article_edit.html', {'form': form})


@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('blog:article_detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'blog/article_edit.html', {'form': form})


@login_required
def article_publish(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.publish()
    return redirect('blog:article_detail', pk=pk)


@login_required
def article_remove(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.delete()
    return redirect('blog:article_list')


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('blog:article_detail', pk=comment.article.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('blog:article_detail', pk=comment.article.pk)



...
$("#update-list").prepend('<input type="text" size="40" value='+val.pk+' name='+val.pk+'>\
<div class="card mb-4">\
{% if '+val.fields["image"]+' %}\
<div class="span2">\
<img  src="{{ MEDIA_URL }}'+val.fields["image"]+'">\
</div>\
{% endif %}\
<div class="card-body">\
<h2 class="card-title">'+val.fields["title"]+'</h2>\
</div>\
<div class="card-footer text-muted">\
</div>\
</div>'

);
...
