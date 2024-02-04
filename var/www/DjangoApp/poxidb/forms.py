from django import forms

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