from django.conf.urls import url, include
from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^$', views.ArticleListView.as_view(), name='article_list'),
    url(r'^article/(?P<pk>[0-9]+)/$', views.ArticleDetail.as_view(), name='article_detail'),
    url(r'^article/new/$', views.ArticleCreate.as_view(), name='article_new'),
    url(r'^article/(?P<pk>[0-9]+)/edit/$', views.ArticleUpdate.as_view(), name='article_edit'),
    url(r'^drafts/$', views.DraftArticleListView.as_view(), name='article_draft_list'),
    url(r'^article/(?P<pk>\d+)/publish/$', views.article_publish, name='article_publish'),
    url(r'^article/(?P<pk>\d+)/delete/$', views.ArticleDelete.as_view(), name='article_delete'),
    url(r'^comment/(?P<pk>\d+)/approve/$', views.comment_approve, name='comment_approve'),
    url(r'^comment/(?P<pk>\d+)/remove/$', views.CommentDelete.as_view(), name='comment_remove'),
    url(r'^categories/(?P<categoryName>\w+)/$', views.ArticleListView.as_view(), name='article_categories_list'),
    url(r'^author/(?P<authorName>\w+)/$', views.ArticleListView.as_view(), name='article_author_list'),
    url(r'^search/$', views.SearchArticleListView.as_view(), name='search_list'),
    url(r'^article/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', views.ArticleListView.as_view(), name='article_date_list'),
    url(r'^accounts/register/$', views.RegisterFormView.as_view(), name='register'),
]
