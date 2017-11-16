from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Article, Comment
from .forms import ArticleForm, CommentForm

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin, DeleteView, CreateView, UpdateView

from django.http import JsonResponse, HttpResponse, HttpResponseNotFound, Http404
from django.core import serializers

from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from html import unescape
from django.template.defaultfilters import linebreaksbr, truncatechars

from django.views.decorators.vary import vary_on_headers
from json import dumps
from django.db.models import Case, Sum, When, IntegerField

from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm

from django.db.models.functions import Length

def ger_articles_page(articles, page, paginate_by = 4):
    paginator = Paginator(articles, paginate_by)
    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        articles_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        articles_page = paginator.page(paginator.num_pages)
    return articles_page

class ArticleListView(ListView):
    allow_empty = True
    context_object_name = 'articles'
    model = Article
    paginate_by = 4
    template_name = "blog/article_list.html"

    @method_decorator(vary_on_headers('X-Requested-With'))
    def dispatch(self, *args, **kwargs):
        return super(ArticleListView, self).dispatch(*args, **kwargs)

    def field_json_queryset(self, articles):
        articles = articles.values('id', 'image', 'published_date', 'title', 'text', 'author__username', 'category__urlstext', 'category__title').annotate(approved_comments=Sum(Case(When(comments__approved_comment=True, then=1),default=0,output_field=IntegerField())))
        return articles

    def get_queryset(self):
        articles = Article.objects.filter(published_date__lte=timezone.now())
        articles = articles.order_by('-published_date', 'title')
        categoryName = self.kwargs.get('categoryName', "")
        authorName = self.kwargs.get('authorName', "")

        year = self.kwargs.get('year', "")
        month = self.kwargs.get('month', "")
        day = self.kwargs.get('day', "")

        if categoryName:
            articles = articles.filter(category__urlstext=categoryName)
        elif authorName:
            articles = articles.filter(author__username=authorName)
        elif year and month and day:
            articles = articles.filter(published_date__year=year).filter(published_date__month=month).filter(published_date__day=day)

        return articles

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        context['mode_list'] = 'simple'
        context['list_article_pag'] = ger_articles_page(self.get_queryset(), self.request.GET.get('page'), self.paginate_by)
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            mensajes = ger_articles_page(self.field_json_queryset(self.get_queryset()), self.request.GET.get('page'), self.paginate_by)
            json_object_records=[]

            for line in mensajes:
                json_object_dict = {}
                json_object_dict['id'] = line['id']
                json_object_dict['image'] = line['image']
                json_object_dict['published_date'] = line['published_date']
                json_object_dict['text'] = truncatechars(linebreaksbr(strip_tags(unescape(line['text']))),400)
                json_object_dict['title'] = line['title']
                json_object_dict['username'] = line['author__username']
                json_object_dict['category_urlstext'] = line['category__urlstext']
                json_object_dict['category_title'] = line['category__title']
                json_object_dict['approved_comments'] = line['approved_comments']
                json_object_records.append(json_object_dict)

            json_page_records=[]
            json_page_dict = {}
            json_page_dict['has_other_pages'] = mensajes.has_other_pages()
            json_page_dict['has_previous'] = mensajes.has_previous()
            json_page_dict['paginator_page_range'] = mensajes.paginator.page_range[-1]
            json_page_dict['has_next'] = mensajes.has_next()
            json_page_dict['end_index'] = mensajes.end_index()
            json_page_dict['start_index'] = mensajes.start_index()

            cur = 1;
            if (self.request.GET.get('page')):
                try:
                    cur = int(self.request.GET.get('page'))
                except ValueError:
                    cur = 1

            json_page_dict['current_page'] = cur
            json_page_records.append(json_page_dict)

            json_object = {}
            json_object["json_object"]=json_object_records
            json_object["json_page"]=json_page_records
            return JsonResponse(json_object)
        else:
            return super(ArticleListView,self).render_to_response(context, **response_kwargs)



class SearchArticleListView(ListView):
    allow_empty = True
    context_object_name = 'articles'
    model = Article
    paginate_by = 4
    template_name = "blog/article_list.html"

    def __init__(self, **kwargs):
        self.message = ''
        self.srchtxt = ''

    def get_queryset(self):
        if 'srchtxt' in self.request.GET:
            self.message = 'You searched for: %r' % self.request.GET.get('srchtxt', "")
            self.srchtxt = self.request.GET.get('srchtxt', "")
        else:
            self.message = 'You submitted an empty form.'
            self.srchtxt = ''

        articles = ''
        if self.srchtxt:
            articles = Article.objects.filter(published_date__lte=timezone.now())
            articles = articles.order_by('-published_date', 'title')
            articles = articles.filter(text__icontains=self.srchtxt)
        return articles

    def get_context_data(self, **kwargs):
        context = super(SearchArticleListView, self).get_context_data(**kwargs)
        context['mode_list'] = 'search'
        context['list_article_pag'] = ger_articles_page(self.get_queryset(), self.request.GET.get('page'), self.paginate_by)
        context['message'] = self.message
        context['srchtxt'] = self.srchtxt
        return context


@method_decorator(login_required, name='dispatch')
class DraftArticleListView(ListView):
    allow_empty = True
    context_object_name = 'articles'
    model = Article
    paginate_by = 4
    template_name = "blog/article_list.html"

    def get_queryset(self):
        articles = Article.objects.filter(published_date__isnull=True, author__username = self.request.user)
        articles = articles.order_by('-created_date', 'title')
        return articles

    def get_context_data(self, **kwargs):
        context = super(DraftArticleListView, self).get_context_data(**kwargs)
        context['mode_list'] = 'draft'
        context['list_article_pag'] = ger_articles_page(self.get_queryset(), self.request.GET.get('page'), self.paginate_by)
        return context


class ArticleDetail(FormMixin, DetailView):
    context_object_name = 'article'
    model = Article
    template_name = "blog/article_detail.html"
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super(ArticleDetail, self).get_context_data(**kwargs)
        context['form'] = CommentForm(initial={'post': self.object})
        context['comments'] = Comment.objects.filter(article__id=self.object.id).filter(created_date__lte=timezone.now()).order_by('created_date')
        return context

    def get_queryset(self):
        if self.request.user.is_authenticated():
            articles = Article.objects.filter(author__username = self.request.user) | Article.objects.filter(published_date__lte=timezone.now())
        else:
            articles = Article.objects.filter(published_date__lte=timezone.now())
        return articles

    def get_success_url(self):
        return reverse('blog:article_detail', kwargs={'pk': self.object.id})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.article = self.object
        comment.save()
        return super(ArticleDetail, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class ArticleDelete(DeleteView):
    model = Article
    template_name = "blog/article_confirm_delete.html"
    success_url = reverse_lazy('blog:article_draft_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if str(self.object.author.username) == str(request.user):
            return super(ArticleDelete, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404


@method_decorator(login_required, name='dispatch')
class ArticleCreate(CreateView):
    model = Article
    template_name = "blog/article_edit.html"
    form_class = ArticleForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        return super(ArticleCreate, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class ArticleUpdate(UpdateView):
    model = Article
    template_name = "blog/article_edit.html"
    form_class = ArticleForm

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if str(self.object.author.username) == str(request.user):
            return super(ArticleUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        return super(ArticleUpdate, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class CommentDelete(DeleteView):
    model = Comment
    template_name = "blog/comment_confirm_delete.html"

    def get_success_url(self):
        return reverse('blog:article_detail', kwargs={'pk': self.object.article.pk})


class RegisterFormView(FormView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = "registration/register.html"

    def form_valid(self, form):
        form.save()
        return super(RegisterFormView, self).form_valid(form)

@login_required
def article_publish(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if str(article.author.username) == str(request.user):
        article.publish()

    return redirect(reverse('blog:article_detail', kwargs={'pk': pk}))


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect(reverse('blog:article_detail', kwargs={'pk': comment.article.pk}))
