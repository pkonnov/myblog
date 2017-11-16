from django import forms
from .models import Article, Comment

class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ('title', 'category', 'text', 'image')

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class' : 'form-control'})
        self.fields['category'].widget.attrs.update({'class' : 'form-control'})
        self.fields['text'].widget.attrs.update({'class' : 'form-control'})
        self.fields['image'].widget.attrs.update({'class' : 'form-control'})


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('author', 'text',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['author'].widget.attrs.update({'class' : 'form-control'})
        self.fields['text'].widget.attrs.update({'class' : 'form-control', 'rows' : '10'})
