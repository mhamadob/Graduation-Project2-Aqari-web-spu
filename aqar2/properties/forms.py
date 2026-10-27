from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Property, PropertyImage, Comment, SavedSearch, UserProfile

# REQ-2  +  REQ-19,20
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'example@mail.com'}))
    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('هذا البريد مستخدم بالفعل')
        return email

# REQ-3
class EditProfileForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['username', 'email', 'first_name', 'last_name']

# REQ-60
class UserProfileForm(forms.ModelForm):
    class Meta:
        model  = UserProfile
        fields = ['phone', 'bio', 'avatar', 'city']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'نبذة عنك...'}),
        }

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'multiple': True}))
        super().__init__(*args, **kwargs)
    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(d, initial) for d in data]
        return single_clean(data, initial)

# REQ-6,7
class PropertyForm(forms.ModelForm):
    additional_images = MultipleFileField(required=False, label='صور إضافية')

    class Meta:
        model  = Property
        fields = ['title', 'description', 'price', 'city', 'address',
                  'area', 'rooms', 'property_type', 'status', 'image',
                  'is_active', 'ad_state']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

# REQ-22
class PropertyImageForm(forms.ModelForm):
    class Meta:
        model  = PropertyImage
        fields = ['image', 'caption']

# REQ-44
class CommentForm(forms.ModelForm):
    class Meta:
        model  = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'اكتب تعليقك...'}),
        }

# REQ-47
class SavedSearchForm(forms.ModelForm):
    class Meta:
        model  = SavedSearch
        fields = ['name', 'query', 'city', 'property_type', 'status', 'min_price', 'max_price']
