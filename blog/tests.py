import datetime
import os

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Category, Article, Comment
from .forms import ArticleForm, CommentForm

from django.contrib.auth.models import User

def create_article(title, days):
    time = timezone.now() + datetime.timedelta(days=days)
    category = Category.objects.get(title='test_category')
    author = User.objects.get(username='test_usr')
    return Article.objects.create(author=author, category=category, title=title, text='test_text', created_date=time, published_date=time)

def create_draft_article(title, days):
    time = timezone.now() + datetime.timedelta(days=days)
    category = Category.objects.get(title='test_category')
    author = User.objects.get(username='test_usr')
    return Article.objects.create(author=author, category=category, title=title, text='test_text', created_date=time)

def date_to_str(time):
    str_year = str(time.year)
    str_month = "01"
    if int(time.month) < 10:
        str_month = "0" + str(time.month)
    else:
        str_month = str(time.month)

    str_day = "01"
    if int(time.day) < 10:
        str_day = "0" + str(time.day)
    else:
        str_day = str(time.day)
    strdate = { 'str_year': str_year, 'str_month': str_month, 'str_day': str_day  }
    return strdate

"""
Testing model methods
"""
class Tests_Model_Method_Article(TestCase):
    def test_was_published_recently_with_future_article(self):
        """
        was_published_recently() should return False for article whose
        published_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days = 30)
        future_article = Article(1, 1, 'mytest_recently_with_future_article',
            published_date = time)
        self.assertEqual(future_article.was_published_recently(), False)

    def test_was_published_recently_with_old_article(self):
        """
        was_published_recently() should return False for article whose
        published_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days = 30)
        old_question = Article(1, 1, 'mytest_recently_with_old_article',
            published_date = time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_article(self):
        """
        was_published_recently() should return True for article whose
        published_date is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours = 1)
        recent_question = Article(1, 1, 'mytest_recently_with_recent_article',
            published_date = time)
        self.assertEqual(recent_question.was_published_recently(), True)


"""
Testing view methods - List
"""
class Test_View_Article_List(TestCase):
    def setUp(self):
        Category.objects.create(title = 'test_category',
            text = 'text_test_category',
            urlstext = 'url_test_category'
        )
        User.objects.create(username='test_usr', password ='secret')

    def test_article_list_view_with_no_article(self):
        """
        If no articles exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('blog:article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No blog are available.')
        self.assertQuerysetEqual(response.context['articles'], [])

    def test_article_list_view_with_no_article_published_date(self):
        """
        If no articles published_date exist, an appropriate message should
        be displayed.
        """
        time = timezone.now() + datetime.timedelta(days = -30)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        Article.objects.create(author = author,
            category = category,
            title = 'Past article.',
            text = 'Test text',
            created_date = time
        )
        response = self.client.get(reverse('blog:article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No blog are available.")
        self.assertQuerysetEqual(response.context['articles'], [])

    def test_article_list_view_with_a_past_article(self):
        """
        Articles with a published_date in the past should be displayed on the
        index page.
        """
        time = timezone.now() + datetime.timedelta(days = -30)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        Article.objects.create(author = author,
            category = category,
            title = 'Past article.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_list'))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Past article.>']
        )

    def test_article_list_view_with_a_future_article(self):
        """
        Articles with a published_date in the future should not be displayed on
        the index page.
        """
        time = timezone.now() + datetime.timedelta(days = 30)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        Article.objects.create(author = author,
            category = category,
            title = 'Future article.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_list'))
        self.assertContains(response, "No blog are available.", status_code=200)
        self.assertQuerysetEqual(response.context['articles'], [])

    def test_article_list_view_with_future_article_and_past_article(self):
        """
        Even if both past and future articles exist, only past articles
        should be displayed.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -30)
        Article.objects.create(author = author,
            category = category,
            title = 'Past article.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        time = timezone.now() + datetime.timedelta(days = 30)
        Article.objects.create(author = author,
            category = category,
            title = 'Future article.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_list'))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Past article.>']
        )

    def test_article_list_view_with_two_past_articles(self):
        """
        The articles index page may display multiple articles.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -30)
        Article.objects.create(author = author,
            category = category,
            title = 'Past article 1.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        time = timezone.now() + datetime.timedelta(days = -5)
        Article.objects.create(author = author,
            category = category,
            title = 'Past article 2.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_list'))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Past article 2.>', '<Article: Past article 1.>']
        )


class Test_View_Article_List_By_Category(TestCase):
    def setUp(self):
        Category.objects.create(title = 'test_category',
            text = 'text_test_category',
            urlstext = 'url_test_category'
        )
        User.objects.create(username='test_usr', password ='secret')

    def test_article_list_by_categories_view_with_no_articles(self):
        """
        If there are no articles for the selected category, a corresponding
        message should be displayed.
        """
        response = self.client.get(reverse('blog:article_categories_list',
            kwargs={'categoryName': 'url_test_category'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No blog are available.")
        self.assertQuerysetEqual(response.context['articles'], [])

    def test_article_list_by_categories_view_with_a_past_article(self):
        """
        Articles for the selected category with a published_date in the past
        should be displayed for the selected category page.
        """
        time = timezone.now() + datetime.timedelta(days = -30)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the past with the selected category.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_categories_list',
            kwargs={'categoryName' : 'url_test_category'}))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Articles in the past with the selected category.>']
        )

    def test_article_list_by_categories_view_with_a_future_article(self):
        """
        Articles for the selected category with a published_date in the future
        should not be displayed for the selected category page.
        """
        time = timezone.now() + datetime.timedelta(days = 30)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the future with the selected category.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_categories_list',
            kwargs={'categoryName' : 'url_test_category'}))
        self.assertContains(response, "No blog are available.", status_code=200)
        self.assertQuerysetEqual(response.context['articles'], [])

    def test_article_list_by_categories_view_with_future_and_past_article(self):
        """
        Even if both past and future articles for the selected category exist,
        only past articles for the selected category should be displayed.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -30)
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the past with the selected category.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        time = timezone.now() + datetime.timedelta(days = 30)
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the future with the selected category.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_categories_list',
            kwargs={'categoryName' : 'url_test_category'}))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Articles in the past with the selected category.>']
        )

    def test_article_list_by_categories_view_with_two_past_articles(self):
        """
        Several articles can be displayed on the page of the selected category
        for articles.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -30)
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the past with the selected category 1.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        time = timezone.now() + datetime.timedelta(days = -5)
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the past with the selected category 2.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_categories_list',
            kwargs={'categoryName' : 'url_test_category'}))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Articles in the past with the selected category 2.>',
            '<Article: Articles in the past with the selected category 1.>']
        )


class Test_View_Article_List_By_Author(TestCase):
    def setUp(self):
        Category.objects.create(title = 'test_category',
            text = 'text_test_category',
            urlstext = 'url_test_category'
        )
        User.objects.create(username='test_usr', password ='secret')

    def test_article_list_by_author_view_with_no_articles(self):
        """
        If there are no articles for the selected author, a corresponding
        message should be displayed.
        """
        response = self.client.get(reverse('blog:article_author_list',
            kwargs={'authorName': 'test_usr'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No blog are available.")
        self.assertQuerysetEqual(response.context['articles'], [])

    def test_article_list_by_author_view_with_a_past_article(self):
        """
        Articles for the selected author with a published_date in the past
        should be displayed for the selected author page.
        """
        time = timezone.now() + datetime.timedelta(days = -30)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the past with the selected author.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_author_list',
            kwargs={'authorName': 'test_usr'}))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Articles in the past with the selected author.>']
        )

    def test_article_list_by_author_view_with_a_future_article(self):
        """
        Articles for the selected author with a published_date in the future
        should not be displayed for the selected author page.
        """
        time = timezone.now() + datetime.timedelta(days = 30)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the future with the selected author.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_author_list',
            kwargs={'authorName': 'test_usr'}))
        self.assertContains(response, "No blog are available.", status_code=200)
        self.assertQuerysetEqual(response.context['articles'], [])

    def test_article_list_by_author_view_with_future_and_past_article(self):
        """
        Even if both past and future articles for the selected author exist,
        only past articles for the selected author should be displayed.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -30)
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the past with the selected author.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        time = timezone.now() + datetime.timedelta(days = 30)
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the future with the selected author.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_author_list',
            kwargs={'authorName': 'test_usr'}))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Articles in the past with the selected author.>']
        )

    def test_article_list_by_author_view_with_two_past_articles(self):
        """
        Several articles can be displayed on the page of the selected author
        for articles.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -30)
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the past with the selected author 1.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        time = timezone.now() + datetime.timedelta(days = -5)
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the past with the selected author 2.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_author_list',
            kwargs={'authorName': 'test_usr'}))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Articles in the past with the selected author 2.>',
            '<Article: Articles in the past with the selected author 1.>']
        )


class Test_View_Article_List_By_Calendar(TestCase):
    def setUp(self):
        Category.objects.create(title = 'test_category',
            text = 'text_test_category',
            urlstext = 'url_test_category'
        )
        User.objects.create(username='test_usr', password ='secret')

    def test_article_list_by_calendar_view_with_no_articles(self):
        """
        If there are no articles for the selected date, a corresponding
        message should be displayed.
        """
        response = self.client.get(reverse('blog:article_date_list',
            kwargs={'year': '2017', 'month': '10', 'day': '30'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No blog are available.")
        self.assertQuerysetEqual(response.context['articles'], [])

    def tes_article_list_byt_calendar_view_with_a_past_article(self):
        """
        Articles for the selected date with a published_date in the past
        should be displayed for the selected date page.
        """
        time = timezone.now() + datetime.timedelta(days = -30)
        strdate = date_to_str(time)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the past with the selected date.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_date_list',
            kwargs={'year': strdate['str_year'],
                'month': strdate['str_month'],
                'day': strdate['str_day']
            }
        ))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Articles in the past with the selected date.>']
        )

    def test_article_list_by_calendar_view_with_a_future_article(self):
        """
        Articles for the selected date with a published_date in the future
        should not be displayed for the selected date page.
        """
        time = timezone.now() + datetime.timedelta(days = 30)
        strdate = date_to_str(time)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        Article.objects.create(author = author,
            category = category,
            title = 'Articles in the future with the selected date.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        time = timezone.now() + datetime.timedelta(30)
        strdate = date_to_str(time)
        response = self.client.get(reverse('blog:article_date_list',
            kwargs={'year': strdate['str_year'],
                'month': strdate['str_month'],
                'day': strdate['str_day']
            }
        ))
        self.assertContains(response, "No blog are available.", status_code=200)
        self.assertQuerysetEqual(response.context['articles'], [])

    def test_article_list_by_calendar_view_with_two_past_articles(self):
        """
        Several articles can be displayed on the page of the selected date
        for articles.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -30)
        strdate = date_to_str(time)
        Article.objects.create(author = author,
            category = category,
            title = 'Articles bb.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        Article.objects.create(author = author,
            category = category,
            title = 'Articles a.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_date_list',
            kwargs={'year': strdate['str_year'],
                'month': strdate['str_month'],
                'day': strdate['str_day']
            }
        ))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Articles a.>', '<Article: Articles bb.>']
        )


class Test_View_Draft_Article_List(TestCase):
    def setUp(self):
        self.usercreate = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.usercreate)
        Category.objects.create(title='test_category',
            text='text_test_category',urlstext='url_test_category')
        User.objects.create_user(username='test_usr', password='secret')

    def test_draft_article_list_of_not_registered_user(self):
        '''
        Access to draft article list of not registered user
        '''
        response = self.client.get(reverse('blog:article_draft_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
            expected_url='/accounts/login/?next=/drafts/',
            status_code=302,
            target_status_code=200
        )

    def test_draft_article_list_registered_user(self):
        '''
        Access to draft article list registered user
        '''
        self.client.login(username = self.usercreate['username'],
            password = self.usercreate['password'])
        response = self.client.get(reverse('blog:article_draft_list'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_draft_article_list_view_with_no_article(self):
        """
        If no draft articles exist, an appropriate message should be displayed.
        """
        self.client.login(username = self.usercreate['username'],
            password = self.usercreate['password'])
        response = self.client.get(reverse('blog:article_draft_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No blog are available.")
        self.assertQuerysetEqual(response.context['articles'], [])
        self.client.logout()

    def test_draft_article_list_view_with_article_published_date(self):
        """
        If articles published_date exist, an appropriate message
        should be displayed.
        """
        time = timezone.now() + datetime.timedelta(days = -10)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        Article.objects.create(author = author,
            category = category,
            title = 'Articles with published date.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        self.client.login(username = 'test_usr', password = 'secret')
        response = self.client.get(reverse('blog:article_draft_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No blog are available.")
        self.assertQuerysetEqual(response.context['articles'], [])
        self.client.logout()

    def test_draft_article_list_view_with_a_past_article_owned_user(self):
        """
        Draft articles with a created_date in the past should be displayed on
        the page owned by the user.
        """
        time = timezone.now() + datetime.timedelta(days = -10)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        Article.objects.create(author = author,
            category = category,
            title = 'Articles owned user.',
            text = 'Test text',
            created_date = time,
        )
        author = User.objects.get(username = self.usercreate['username'])
        Article.objects.create(author = author,
            category = category,
            title = 'Articles not owned user.',
            text = 'Test text',
            created_date = time,
        )
        self.client.login(username = 'test_usr', password = 'secret')
        response = self.client.get(reverse('blog:article_draft_list'))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Articles owned user.>']
        )
        self.client.logout()

    def test_draft_article_list_view_with_a_past_article_no_owned_user(self):
        """
        Draft articles with a created_date in the past should be displayed on
        the page no owned by the user.
        """
        time = timezone.now() + datetime.timedelta(days = -10)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = self.usercreate['username'])
        Article.objects.create(author = author,
            category = category,
            title = 'Articles not owned user.',
            text = 'Test text',
            created_date = time,
        )
        self.client.login(username = 'test_usr', password = 'secret')
        response = self.client.get(reverse('blog:article_draft_list'))
        self.assertContains(response, "No blog are available.")
        self.assertQuerysetEqual(response.context['articles'], [])
        self.client.logout()


    def test_draft_article_list_view_with_a_future_article(self):
        """
        Draft articles with a created_date in the future should be displayed on
        the page.
        """
        time = timezone.now() + datetime.timedelta(days = 30)
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        Article.objects.create(author = author,
            category = category,
            title = 'Future article.',
            text = 'Test text',
            created_date = time,
        )
        self.client.login(username = 'test_usr', password = 'secret')
        response = self.client.get(reverse('blog:article_draft_list'))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Future article.>']
        )
        self.client.logout()

    def test_draft_article_list_view_with_future_and_past_article(self):
        """
        Even if both past and future draft articles existmshould be displayed.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -30)
        Article.objects.create(author = author,
            category = category,
            title = 'Past article.',
            text = 'Test text',
            created_date = time,
        )
        time = timezone.now() + datetime.timedelta(days = 30)
        Article.objects.create(author = author,
            category = category,
            title = 'Future article.',
            text = 'Test text',
            created_date = time,
        )
        self.client.login(username = 'test_usr', password = 'secret')
        response = self.client.get(reverse('blog:article_draft_list'))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Future article.>', '<Article: Past article.>']
        )
        self.client.logout()

    def test_draft_article_list_view_with_two_past_articles(self):
        """
        The draft articles page may display multiple articles.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -30)
        Article.objects.create(author = author,
            category = category,
            title = 'Past article 1.',
            text = 'Test text',
            created_date = time,
        )
        time = timezone.now() + datetime.timedelta(days = -5)
        Article.objects.create(author = author,
            category = category,
            title = 'Past article 2.',
            text = 'Test text',
            created_date = time,
        )
        self.client.login(username = 'test_usr', password = 'secret')
        response = self.client.get(reverse('blog:article_draft_list'))
        self.assertQuerysetEqual(
            response.context['articles'],
            ['<Article: Past article 2.>', '<Article: Past article 1.>']
        )
        self.client.logout()


"""
Testing view methods - Element
"""
class Test_View_User(TestCase):
    def setUp(self):
        self.usercreate = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.usercreate)
        Category.objects.create(title='test_category',
            text='text_test_category',urlstext='url_test_category')
        User.objects.create_user(username='test_usr', password='secret')

    def test_user_verify_login(self):
        """
        Verify user login
        """
        login = self.client.login(username = self.usercreate['username'],
            password = self.usercreate['password'])
        self.assertTrue(login)
        self.client.logout()

    def test_user_in_login(self):
        """
        Verify user login in, should be logged in now
        """
        response = self.client.post('/accounts/login/', self.usercreate, follow=True)
        self.assertTrue(response.context['user'].is_active)


class Test_View_Article_Detail(TestCase):
    def setUp(self):
        self.usercreate = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.usercreate)
        Category.objects.create(title='test_category',
            text='text_test_category',urlstext='url_test_category')
        User.objects.create_user(username='test_usr', password='secret')

    def test_detail_article_view_with_a_published_date_future_article(self):
        """
        The detail view of a article with a published_date in the future should
        return a 404 not found if published.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = 5)
        future_article = Article.objects.create(author = author,
            category = category,
            title = 'Future article.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_detail',
            args=(future_article.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_article_view_with_a_published_date_past_article(self):
        """
        The detail view of a article with a published_date in the past should
        display the article's text if published.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -5)
        past_article = Article.objects.create(author = author,
            category = category,
            title = 'Past article.',
            text = 'Test text',
            created_date = time,
            published_date = time,
        )
        response = self.client.get(reverse('blog:article_detail',
            args=(past_article.id,)))
        self.assertContains(response, past_article.title, status_code=200)


    def test_detail_article_view_with_a_created_date_future_not_user(self):
        """
        The detail view of a draft article with a created_date in the future
        should return a 404 not found, for not registered or not logged in
        system, if not published.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = 5)
        future_article = Article.objects.create(author = author,
            category = category,
            title = 'Future article.',
            text = 'Test text',
            created_date = time,
        )
        response = self.client.get(reverse('blog:article_detail',
            args=(future_article.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_article_view_with_a_created_date_future_loggin_user(self):
        """
        The detail view of a draft article with a created_date in the future
        should display the article detail, for user logged in
        system, if not published. A user can only access his article.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = 5)
        future_article_owned = Article.objects.create(author = author,
            category = category,
            title = 'Future detail article owned user.',
            text = 'Test text',
            created_date = time,
        )
        author = User.objects.get(username = self.usercreate['username'])
        future_article_not_owned = Article.objects.create(author = author,
            category = category,
            title = 'Future detail article not owned user.',
            text = 'Test text',
            created_date = time,
        )
        self.client.login(username = 'test_usr', password = 'secret')

        response = self.client.get(reverse('blog:article_detail',
            args=(future_article_owned.id,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('blog:article_detail',
            args=(future_article_not_owned.id,)))
        self.assertEqual(response.status_code, 404)

        self.client.logout()

    def test_detail_article_view_with_a_created_date_past_loggin_user(self):
        """
        The detail view of a draft article with a created_date in the past
        should display the article detail, for user logged in
        system, if not published. A user can only access his article.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -5)
        past_article_owned = Article.objects.create(author = author,
            category = category,
            title = 'Past detail article owned user.',
            text = 'Test text',
            created_date = time,
        )
        author = User.objects.get(username = self.usercreate['username'])
        past_article_not_owned = Article.objects.create(author = author,
            category = category,
            title = 'Past detail article not owned user.',
            text = 'Test text',
            created_date = time,
        )
        self.client.login(username = 'test_usr', password = 'secret')

        response = self.client.get(reverse('blog:article_detail',
            args=(past_article_owned.id,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('blog:article_detail',
            args=(past_article_not_owned.id,)))
        self.assertEqual(response.status_code, 404)

        self.client.logout()

    def test_detail_article_delete_not_logged_user(self):
        """
        If the user has not logged in, he can not delete the article
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -5)
        past_article = Article.objects.create(author = author,
            category = category,
            title = 'Past detail article.',
            text = 'Test text',
            created_date = time,
        )
        response = self.client.get(reverse('blog:article_delete',
            args=(past_article.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
            expected_url='/accounts/login/?next=/article/'+
                str(past_article.id)+'/delete/',
            status_code=302,
            target_status_code=200
        )

    def test_detail_article_delete_loggin_user(self):
        """
        The user can delete only his article if it is not published
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -5)
        past_article_owned = Article.objects.create(author = author,
            category = category,
            title = 'Past detail article owned user.',
            text = 'Test text',
            created_date = time,
        )
        author = User.objects.get(username = self.usercreate['username'])
        past_article_not_owned = Article.objects.create(author = author,
            category = category,
            title = 'Past detail article not owned user.',
            text = 'Test text',
            created_date = time,
        )

        self.client.login(username = 'test_usr', password = 'secret')

        response = self.client.post(reverse('blog:article_delete',
            args=(past_article_owned.id,)),
            {'pk': past_article_owned.id,
                'author': 'test_usr'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
            expected_url='/drafts/',
            status_code=302,
            target_status_code=200
        )

        response = self.client.post(reverse('blog:article_delete',
            args=(past_article_not_owned.id,)),
            {'pk': past_article_not_owned.id,
                'author': str(self.usercreate['username']) })
        self.assertEqual(response.status_code, 404)

        self.client.logout()

    def test_detail_article_publish_not_logged_user(self):
        """
        If the user has not logged in, he can not publish the article
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -5)
        past_article = Article.objects.create(author = author,
            category = category,
            title = 'Past detail article.',
            text = 'Test text',
            created_date = time,
        )
        response = self.client.get(reverse('blog:article_publish',
            args=(past_article.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
            expected_url='/accounts/login/?next=/article/'+
                str(past_article.id)+'/publish/',
            status_code=302,
            target_status_code=200
        )

    def test_detail_article_publish_loggin_user(self):
        """
        The user can publish only his article if it is not published
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -5)
        past_article_owned = Article.objects.create(author = author,
            category = category,
            title = 'Past detail article owned user.',
            text = 'Test text',
            created_date = time,
        )
        author = User.objects.get(username = self.usercreate['username'])
        past_article_not_owned = Article.objects.create(author = author,
            category = category,
            title = 'Past detail article not owned user.',
            text = 'Test text',
            created_date = time,
        )

        self.client.login(username = 'test_usr', password = 'secret')

        response = self.client.get(reverse('blog:article_publish',
            args=(past_article_owned.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
            expected_url='/article/'+str(past_article_owned.id)+'/',
            status_code=302,
            target_status_code=200
        )
        response = self.client.get(reverse('blog:article_detail',
            args=(past_article_owned.id,)))
        self.assertNotEqual(response.context['article'].published_date, None)

        response = self.client.get(reverse('blog:article_publish',
            args=(past_article_not_owned.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
            expected_url='/article/'+str(past_article_not_owned.id)+'/',
            status_code=302,
            target_status_code=404
        )
        response = self.client.get(reverse('blog:article_detail',
            args=(past_article_not_owned.id,)))
        self.assertEqual(response.status_code, 404)

        self.client.logout()


class Test_View_Article_Form(TestCase):
    def setUp(self):
        self.usercreate = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.usercreate)
        Category.objects.create(title='test_category',
            text='text_test_category',urlstext='url_test_category')
        User.objects.create_user(username='test_usr', password='secret')

    def test_form_article_valid(self):
        """
        Form validation for validity. Valid form data
        """
        category = Category.objects.get(title = 'test_category')
        data = {
            'title': "Title article",
            'category': category.id,
            'text': "Text article",
        }
        form = ArticleForm(data)
        self.assertTrue(form.is_valid())

    def test_form_article_invalid(self):
        """
        Form validation for validity. Invalid Form Data
        """
        category = Category.objects.get(title = 'test_category')
        data = {
            'title': "",
            'category': category.id,
            'text': "",
        }
        form = ArticleForm(data)
        self.assertFalse(form.is_valid())

    def test_form_article_not_logged_user_edit(self):
        """
        The user can not edit article the entry if he is not logged in.
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -5)
        past_article = Article.objects.create(author = author,
            category = category,
            title = 'Past detail article.',
            text = 'Test text',
            created_date = time,
        )
        response = self.client.get(reverse('blog:article_edit',
            args=(past_article.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
            expected_url='/accounts/login/?next=/article/'+
                str(past_article.id)+'/edit/',
            status_code=302,
            target_status_code=200
        )

    def test_form_article_not_logged_user_create(self):
        """
        The user can not add article the entry if he is not logged in.
        """
        response = self.client.get(reverse('blog:article_new'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
            expected_url='/accounts/login/?next=/article/new/',
            status_code=302,
            target_status_code=200
        )

    def test_form_article_loggin_user_saving_to_list(self):
        """
        Test form save saving to a list
        """
        category = Category.objects.get(title = 'test_category')
        user_test = User.objects.get(username = 'test_usr')
        self.client.login(username = 'test_usr', password = 'secret')

        data = {
            'title': "Title article",
            'category': category.id,
            'text': "Text article",
        }
        form = ArticleForm(data)
        article = form.save(commit=False)
        article.author = user_test
        article.save()
        self.assertEqual(article, Article.objects.first())
        self.assertEqual(article.title, 'Title article')
        self.assertEqual(article.text, 'Text article')
        self.client.logout()

    def test_form_article_loggin_user_create(self):
        """
        Only the logged-in user can create an article
        """
        category = Category.objects.get(title = 'test_category')
        data = {
            'title': "Title article new",
            'category': category.id,
            'text': "Text article",
        }
        self.client.login(username = 'test_usr', password = 'secret')
        response = self.client.post(reverse('blog:article_new'), data,
            secure=False)
        self.assertEqual(response.status_code, 302)
        past_article = Article.objects.filter(title='Title article new').values('id')
        past_article = past_article[0]
        self.assertRedirects(response,
            expected_url='/article/'+str(past_article['id'])+'/',
            status_code=302,
            target_status_code=200
        )
        self.client.logout()

    def test_form_article_loggin_user_edit_author(self):
        """
        The author of his article can edit it if he logged in
        """
        category = Category.objects.get(title = 'test_category')
        author = User.objects.get(username = 'test_usr')
        time = timezone.now() + datetime.timedelta(days = -5)
        Article.objects.create(author = author,
            category = category,
            title = 'Past detail article owned user.',
            text = 'Test text',
            created_date = time,
        )
        author = User.objects.get(username = self.usercreate['username'])
        Article.objects.create(author = author,
            category = category,
            title = 'Past detail article not owned user.',
            text = 'Test text',
            created_date = time,
        )

        past_article_owned = Article.objects.filter(
            title='Past detail article owned user.').values('id',
            'author', 'category', 'title', 'text', 'created_date',
            'published_date', 'image')
        past_article_not_owned = Article.objects.filter(
            title='Past detail article not owned user.').values('id',
            'author', 'category', 'title', 'text', 'created_date',
            'published_date', 'image')

        self.client.login(username = 'test_usr', password = 'secret')

        past_article_owned = past_article_owned[0]
        past_article_owned['title'] = 'Past detail article owned user edit.'
        response = self.client.post(reverse('blog:article_edit',
            args=(past_article_owned['id'],)), past_article_owned)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
            expected_url='/article/'+ str(past_article_owned['id'])+'/',
            status_code=302,
            target_status_code=200
        )
        response = self.client.get(reverse('blog:article_detail',
            args=(past_article_owned['id'],)))
        self.assertEqual(response.context['article'].title,
            'Past detail article owned user edit.')

        past_article_not_owned = past_article_not_owned[0]
        past_article_not_owned['title'] = 'Past detail art. not owned usr edit.'
        response = self.client.post(reverse('blog:article_edit',
            args=(past_article_not_owned['id'],)), past_article_not_owned)
        self.assertEqual(response.status_code, 404)

        self.client.logout()

#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------

class UserComent(TestCase):
    def setUp(self):
        self.usercreate = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.usercreate)
        Category.objects.create(title='test_category',
            text='text_test_category',urlstext='url_test_category')
        User.objects.create_user(username='test_usr', password='secret')

    def test_CommentForm_valid(self):
        """
        Form validation for validity
        Valid form data
        """
        form = CommentForm(data={'author': "me", 'text': "text comment"})
        self.assertTrue(form.is_valid())

    def test_CommentForm_invalid(self):
        """
        Form validation for validity
        Invalid Form Data
        """
        form = CommentForm(data={'author': "", 'text': ""})
        self.assertFalse(form.is_valid())

    def test_add_comment_invalidform_view(self):
        """
        Invalid Data
        """
        past_article = create_article(title='Past article.', days=-5)
        response = self.client.post(reverse('blog:article_detail', args=(past_article.id,)), {'author': "me", 'text': ""})
        self.assertEqual(response.status_code, 200)

    def test_add_comment_validform_view(self):
        """
        Valid Data
        """
        past_article = create_article(title='Past article.', days=-5)
        response = self.client.post(reverse('blog:article_detail', args=(past_article.id,)), {'author': "me", 'text': "text detail"}, secure=False)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url=reverse('blog:article_detail', args=(past_article.id,)), status_code=302, target_status_code=200)

    def test_form_save_saving_to_a_list(self):
        '''
        Test form save saving to a list
        '''
        past_article = create_article(title='Past article.', days=-5)
        form = CommentForm(data={'author': "me", 'text': "text detail"})
        comment = form.save(commit=False)
        comment.article = past_article
        comment.save()
        self.assertEqual(comment, Comment.objects.first())
        self.assertEqual(comment.author, 'me')
        self.assertEqual(comment.text, 'text detail')



    #url(r'^comment/(?P<pk>\d+)/approve/$', views.comment_approve, name='comment_approve'),
    #url(r'^comment/(?P<pk>\d+)/remove/$', views.CommentDelete.as_view(), name='comment_remove'),
    #url(r'^search/$', views.SearchArticleListView.as_view(), name='search_list'),
    #url(r'^accounts/register/$', views.RegisterFormView.as_view(), name='register'),
