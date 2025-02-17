import secrets
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from engine.models import Product, Order, Question, Address
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    username = forms.CharField(max_length=30)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    # terms = forms.BooleanField(required=True)

    def clean(self):
        clean_data = super().clean()
        password1 = clean_data.get("password1")
        password2 = clean_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Password do not match')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AddressForm(forms.ModelForm):
    location = forms.CharField(
        label='Search for your address', max_length=100, required=True, widget=forms.TextInput(
            attrs={'class': 'bg-light form-control', 'placeholder': 'Enter a location'}))
    first_name = forms.CharField(label='First Name *', max_length=100, widget=forms.TextInput(
        attrs={'class': 'bg-light form-control', 'placeholder': 'Steve'}))
    last_name = forms.CharField(label='Last Name *', max_length=100, widget=forms.TextInput(
        attrs={'class': 'bg-light form-control', 'placeholder': 'Smith'}))
    address_line_1 = forms.CharField(label='Address Line 1*', max_length=100, widget=forms.TextInput(
        attrs={'class': 'bg-light form-control', 'placeholder': 'Street'}))
    address_line_2 = forms.CharField(label='Address Line 2*', max_length=100, required=False, widget=forms.TextInput(
        attrs={'class': 'bg-light form-control', 'placeholder': 'Apt/Unit/Suite'}))

    country = CountryField().formfield(
        label='Country*',
        widget=CountrySelectWidget(attrs={'class': 'bg-light form-control'})
    )
    city = forms.CharField(
        label='City*', max_length=100,
        widget=forms.TextInput(attrs={'class': 'bg-light form-control', 'placeholder': 'City'}))
    state = forms.CharField(label='State / Province*', max_length=100, widget=forms.TextInput(
        attrs={'class': 'bg-light form-control', 'placeholder': 'Alabama'}))
    zipcode = forms.CharField(
        label='ZIP/ Postal Code*', max_length=20,
        widget=forms.TextInput(attrs={'class': 'bg-light form-control', 'placeholder': 'ZIP'}))
    phone_number = forms.CharField(
        label='Phone Number*', max_length=16,
        widget=forms.TextInput(
            attrs={'class': 'bg-light form-control', 'placeholder': 'Phone Number', 'pattern': r'^[+\-0-9]*$'}),
        required=True)
    description = forms.CharField(
        label='Additional Delivery Instructions', required=False,
        widget=forms.Textarea(attrs={'class': 'bg-light form-control',
                                     'placeholder': 'Additional Delivery Instructions', 'rows': 4}))

    class Meta:
        model = Address
        fields = ['location', 'first_name', 'last_name', 'address_line_1', 'address_line_2',
                  'country', 'city', 'state', 'zipcode', 'phone_number', 'description']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'count', 'price', 'photo1', 'photo2', 'photo3', 'photo4', 'photo5', 'photo6']

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        product = super().save(commit=False)
        photo_fields = ['photo1', 'photo2', 'photo3', 'photo4', 'photo5', 'photo6']

        for field in photo_fields:
            photo = self.cleaned_data.get(field)

            if photo:
                if photo.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    image = Image.open(photo)
                    image = image.convert('RGB')

                    output = BytesIO()
                    image.save(output, format='WebP')
                    output.seek(0)

                    webp_image = ContentFile(output.read())
                    token = secrets.token_hex(2)
                    webp_image.name = f"{self.user_id}_{photo.name.split('.')[0]}_{token}.webp"
                    setattr(product, field, webp_image)

        if commit:
            product.save()

        return product


class OrderAddressForm(forms.ModelForm):
    location = forms.CharField(
        label='Search for your address', max_length=100, required=True, widget=forms.TextInput(
            attrs={'class': 'bg-light form-control', 'placeholder': 'Enter a location'}))
    first_name = forms.CharField(label='First Name *', max_length=100, widget=forms.TextInput(
        attrs={'class': 'bg-light form-control', 'placeholder': 'Steve'}))
    last_name = forms.CharField(label='Last Name *', max_length=100, widget=forms.TextInput(
        attrs={'class': 'bg-light form-control', 'placeholder': 'Smith'}))
    address_line_1 = forms.CharField(label='Address Line 1*', max_length=100, widget=forms.TextInput(
        attrs={'class': 'bg-light form-control', 'placeholder': 'Street'}))
    address_line_2 = forms.CharField(label='Address Line 2*', max_length=100, required=False, widget=forms.TextInput(
        attrs={'class': 'bg-light form-control', 'placeholder': 'Apt/Unit/Suite'}))
    country = CountryField().formfield(
        label='Country*',
        widget=CountrySelectWidget(attrs={'class': 'bg-light form-control'})
    )
    city = forms.CharField(
        label='City*', max_length=100,
        widget=forms.TextInput(attrs={'class': 'bg-light form-control', 'placeholder': 'City'}))
    state = forms.CharField(label='State / Province*', max_length=100, widget=forms.TextInput(
        attrs={'class': 'bg-light form-control', 'placeholder': 'Alabama'}))
    zipcode = forms.CharField(
        label='ZIP/ Postal Code*', max_length=20,
        widget=forms.TextInput(attrs={'class': 'bg-light form-control', 'placeholder': 'ZIP'}))
    phone_number = forms.CharField(
        label='Phone Number*', max_length=16,
        widget=forms.TextInput(
            attrs={'class': 'bg-light form-control', 'placeholder': 'Phone Number', 'pattern': r'^[+\-0-9]*$'}),
        required=True)
    description = forms.CharField(
        label='Additional Delivery Instructions', required=False,
        widget=forms.Textarea(attrs={'class': 'bg-light form-control',
                                     'placeholder': 'Additional Delivery Instructions', 'rows': 4}))

    class Meta:
        model = Order
        fields = ['location', 'first_name', 'last_name', 'address_line_1', 'address_line_2',
                  'country', 'city', 'state', 'zipcode', 'phone_number', 'description']


class QuestionForm(forms.ModelForm):
    name = forms.CharField(label='Question Name', max_length=64, required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Full Name', 'type': 'text', 'name': 'name'}
    ))
    email = forms.EmailField(label='Email', required=True, widget=forms.EmailInput(
        attrs={'placeholder': 'Email address'}
    ))
    message = forms.CharField(label='Message', max_length=363, required=True, widget=forms.Textarea(
        attrs={'placeholder': 'Tell us your details...', 'name': 'message'}
    ))

    class Meta:
        model = Question
        fields = ['name', 'email', 'message']
