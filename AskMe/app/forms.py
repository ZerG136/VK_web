from django import forms
from django.contrib.auth.models import User

from app.models import Profile, Question, Tag, Answer

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, min_length=8,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Username', 'style': 'margin-bottom: 7px;margin-bottom: 15px;'}))
    password = forms.CharField(max_length=100, min_length=8,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password', 'style': 'margin-bottom: 7px;margin-bottom: 15px;'}))

    def clean(self):
        data = super().clean()
        username = data.get('username').strip()
        if not username:
            self.add_error('username', 'Username required.')
        else:
            data['username'] = username
        
        password = data.get('password').strip()
        if not password:
            self.add_error('password', 'Password required.')
        else:
            data['password'] = password

        return data


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=100, min_length=8,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Username', 'style': 'margin-bottom: 7px;margin-bottom: 15px;'}))
    email = forms.EmailField(max_length=100, min_length=8,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email', 'style': 'margin-bottom: 7px;margin-bottom: 15px;'}))
    password = forms.CharField(max_length=100, min_length=8,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password', 'style': 'margin-bottom: 7px;margin-bottom: 15px;'}))
    password_conf = forms.CharField(max_length=100, min_length=8,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirm Password', 'style': 'margin-bottom: 7px;margin-bottom: 15px;'}))
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User 
        fields = ['username', 'email', 'password'] 

    def clean(self):
        data = super().clean()
        username = data.get('username').strip()
        if not username:
            self.add_error('username', 'Username required.')
        else:
            data['username'] = username

        email = data.get('email').strip()
        if not email:
            self.add_error('email', 'Email required.')
        else:
            data['email'] = email

        password = data.get('password').strip()
        if not password:
            self.add_error('password', 'Password required.')

        password_conf = data.get('password_conf').strip()
        if not password_conf:
            self.add_error('password_conf', 'Password confirmation required.')

        if password_conf != password:
            self.add_error('password_conf', 'Passwords do not match.')
        
        if User.objects.filter(email=email).exists():
            self.add_error('email', 'Email already registered.')

        if User.objects.filter(username=username).exists():
            self.add_error('username', 'Username already used.')

        return data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()

        user_profile, created = Profile.objects.get_or_create(user=user) 
        user_profile.avatar = self.cleaned_data.get('avatar')
        if commit:
            user_profile.save()

        return user


class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(max_length=100,min_length=8, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'style': 'margin-bottom: 7px;margin-bottom: 15px;'}))
    email = forms.EmailField(max_length=100,min_length=8, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'style': 'margin-bottom: 7px;margin-bottom: 15px;'}))
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email'] 

    def clean(self):
        data = super().clean()
        user = self.instance
        username = data.get('username')
        if username:
            username = username.lower().strip()
        else:
            self.add_error('username', 'Username is required.')

        email = data.get('email')
        if email:
            email = email.lower().strip()
        else:
            self.add_error('email', 'Email is required.')

        if User.objects.filter(email=email).exclude(id=user.id).exists():
            self.add_error('email', 'A user with this email already exists.')

        if User.objects.filter(username=username).exclude(id=user.id).exists():
            self.add_error('username', 'A user with this username already exists.')

        return data

    def save(self, commit=True):
        user = super().save(commit=False)

        user_profile, created = Profile.objects.get_or_create(user=user)

        avatar = self.cleaned_data.get('avatar')

        old_avatar = user_profile.avatar
        if avatar:
            if old_avatar:
                old_avatar.delete(save=False)  
            user_profile.avatar = avatar

        if commit:
            user.save()
            user_profile.save()
        return user, user_profile


class QuestionForm(forms.ModelForm):
    title = forms.CharField(max_length=256, min_length=1,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Question title', 'style': 'margin-bottom: 7px;margin-bottom: 15px;'}))
    text = forms.CharField(min_length=1,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'Your question', 'rows': 8, 'style': 'height: 300px;'}))
    tags = forms.CharField(max_length=100, min_length=1,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Tags', 'style': 'margin-bottom: 7px;margin-bottom: 15px;'}))

    class Meta:
        model = Question
        fields = ['title', 'text', 'tags'] 

    def clean_tags(self):
        tags = super().clean().get('tags','')
        tag_names = set()  

        for tag in tags.split():
            tag = tag.strip()
            if tag:
                if len(tag) >= 25:
                    self.add_error('tags', 'Tag too long (>= 25)')
                tag_names.add(tag) 

        return tag_names 

    def save(self, profile, commit=True):
        question = super().save(commit=False)

        if commit:
            question.author = profile
            question.save() 

            for tag_name in self.cleaned_data['tags']:
                tag_obj, created = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag_obj)

            question.save() 

        return question


class AnswerForm(forms.ModelForm):
    text = forms.CharField(min_length=1,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'Your answer', 'rows': 8, 'style': 'height: 150px;'}))

    class Meta:
        model = Answer
        fields = ['text']
