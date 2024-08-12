from django import forms
from django_recaptcha.fields import ReCaptchaField


class SearchForm(forms.Form):
    query_organism = forms.CharField(label = 'Search Organism', required=False)
    query_antigen = forms.CharField(label = 'Search Antigen', required=False)
    search_type = forms.ChoiceField(
        label = "Search in",
        choices=[
            ("antigen", "Antigens Database"),
            ("epitope", "Epitopes Database")
        ],
        widget=forms.RadioSelect,
        required=True
    )


class ContactForm(forms.Form):
    subject = forms.CharField(label = "Subject of your message", required=True)
    email = forms.EmailField(label="Your email address", required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={"rows":10, 
                                                                "cols":40,
                                                                "placeholder":"Type your message here"}),
                                                                required=True)
    captcha = ReCaptchaField()