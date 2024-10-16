from django import forms
from django.forms.widgets import DateTimeInput

from .models import User, Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'})
        }


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
