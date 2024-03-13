from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from . import models

from collections import Counter
from django.db.models import Count
from django.shortcuts import render
from django.utils.html import mark_safe
from django.template import Template, Context

from . forms import SearchForm

# Create your views here.

def poxidb_home(request):
    form = SearchForm()
    results = []
    if request.method == 'POST':
        form = SearchForm(request.POST)
        
        if form.is_valid():
            
            if form.cleaned_data['query_organism'] != "":
                query = form.cleaned_data['query_organism']
                query += "_organism"
                
                if form.cleaned_data['search_type'] == 'antigen':
                    return redirect(reverse('poxidb:visualize_antigens' , kwargs={'query': query}))
                else:
                    return redirect(reverse('poxidb:visualize_epitopes' , kwargs={'query': query}))


            if form.cleaned_data['query_antigen'] != "":
                query = form.cleaned_data['query_antigen']
                query += "_antigen"
                if form.cleaned_data['search_type'] == 'antigen':
                    return redirect(reverse('poxidb:visualize_antigens' , kwargs={'query': query}))
                else:
                    return redirect(reverse('poxidb:visualize_epitopes' , kwargs={'query': query}))



    return render(request, "poxidb/poxidb_home.html", {'form':form})


def poxidb_all(request):
    unique_organisms = models.Proteome.objects.values('organism').annotate(protein_count=Count('organism'))


    organism_data = []


    for item in unique_organisms:
        organism = item['organism']

        query_antigens = models.Proteome.objects.filter(organism=organism, antigen_score__gt=0.5)
        antigen_count = len(query_antigens)

        query_epitopes = models.Epitope.objects.filter(organism=organism)
        epitope_count = query_epitopes.count()

        organism_data.append({
            'organism': organism,
            'protein_count': item['protein_count'],
            'antigen_count': antigen_count,
            'epitope_count':epitope_count
        })

    # Include organism_data in the dictionary
    return render(request, "poxidb/poxidb_all.html", {'organism_data': organism_data})

####proteome
def visualize_proteome(request, organism):
    proteome = models.Proteome.objects.filter(organism=organism)

    return render(request, "poxidb/visualize_proteome.html",
                  context={'organism':organism,
                   'proteome':proteome,
                   'n_proteins':len(proteome)})

def download_proteome(request, organism):
    proteome = models.Proteome.objects.filter(organism=organism)
    proteome_data = list(proteome.values())

    if proteome_data:
        response = HttpResponse(content_type='text/plain')
        filename = f"{organism}_proteome.fasta"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        for entry in proteome_data:
            description = entry['description']
            protein = entry['protein']

            # Write the description line starting with ">"
            response.write(f'>{description}\n')

            # Write the protein sequence
            response.write(f'{protein}\n')

        return response
    else:
        # Handle the case where there is no data
        return HttpResponse("No data available.")


####antigens
def visualize_antigens(request, query):
    antigens_data = []
    antigens = []
    query2 = ""

    
    if "_organism" in query:
        query2 = query.replace("_organism", "")

        antigens = models.Proteome.objects.filter(organism__contains = query2,
                                                antigen_score__gt=0.5)
        antigens_data = list(antigens.values())
        for item in antigens_data:
            epitopes = models.Epitope.objects.filter(description = item['description'])
            item['epitope_count'] = len(epitopes)
    
    if "_antigen" in query:
        query2 = query.replace("_antigen", "")
        antigens = models.Proteome.objects.filter(description__contains = query2,
                                                   antigen_score__gt=0.5)
        antigens_data = list(antigens.values())
        for item in antigens_data:
            epitopes = models.Epitope.objects.filter(description = item['description'])
            item['epitope_count'] = len(epitopes)


    return render(request, "poxidb/visualize_antigens.html",
                  context={'query':query2,
                           'download_query':query,
                           'antigens':antigens_data,
                           'n_antigens':len(antigens)})

def download_antigens(request, query):
    print(query)

    ###execute the query here based on what was searched
    if "_organism" in query:
        antigens = models.Proteome.objects.filter(organism__contains = query.replace("_organism", ""),
                                                antigen_score__gt=0.5)
    elif "_antigen" in query:
        antigens = models.Proteome.objects.filter(description__contains = query.replace("_antigen", ""),
                                                antigen_score__gt=0.5)
        
    antigens_data = list(antigens.values())

    if antigens_data:
        response = HttpResponse(content_type='text/plain')
        filename = f"{query}_antigens.fasta"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        for entry in antigens_data:
            description = entry['description']
            protein = entry['protein']

            # Write the description line starting with ">"
            response.write(f'>{description}\n')

            # Write the protein sequence
            response.write(f'{protein}\n')

        return response
    else:
        # Handle the case where there is no data
        return HttpResponse("No data available.")


####individual epitopes
def visualize_individual_epitopes(request, description):

    epitope_query = models.Epitope.objects.filter(description=description)
    epitopes_data = list(epitope_query.values())

    antigen_query = models.Proteome.objects.filter(description=description)
    antigen = list(antigen_query.values())

    for item in antigen:
        protein = item['protein']

    for item in epitopes_data:
        
        item['start'] = protein.find(item['sequence'])+1
        item['end'] = protein.find(item['sequence'])+1+len(item['sequence'])-1

    return render(request, "poxidb/visualize_individual_epitopes.html",
                  context={"epitopes":epitopes_data,
                           "antigen":antigen})

def download_individual_epitopes(request, description):
    epitopes = models.Epitope.objects.filter(description=description)
    epitopes_data = list(epitopes.values())

    if epitopes_data:
        response = HttpResponse(content_type='text/plain')
        filename = f"{description}_epitopes.fasta"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        description = ''
        for entry in epitopes_data:
            if entry['description'] != description:
                description = entry['description']
                response.write(f'\n>{description}\n')

            sequence = entry['sequence']
            response.write(f'{sequence}\t')

        return response
    else:
        return HttpResponse("No data available.")

####epitopes
def visualize_epitopes(request, query):
    epitopes_data = []
    epitopes = []
    query2 = ""

    if "_organism" in query:
        query2 = query.replace("_organism", "")
        epitopes_queryset = models.Epitope.objects.filter(organism__contains = query2)

    elif "_antigen" in query:
        query2 = query.replace("_antigen", "")
        epitopes_queryset = models.Epitope.objects.filter(description__contains = query2)
    else:
        epitopes_queryset = None

    if epitopes_queryset is not None:
        epitopes = list(epitopes_queryset.values())

    return render(request, "poxidb/visualize_epitopes.html",
                  context = {'epitopes':epitopes,
                             'query':query2,
                             'download_query':query,
                             'n_epitopes':len(epitopes)})

def download_epitopes(request, query):


    ###execute the query here based on what was searched
    if "_organism" in query:
        epitopes = models.Epitope.objects.filter(organism__contains = query.replace("_organism", ""))
    elif "_antigen" in query:
        epitopes = models.Epitope.objects.filter(description__contains = query.replace("_antigen", ""))
        
    epitopes_data = list(epitopes.values())

    if epitopes_data:
        response = HttpResponse(content_type='text/plain')
        filename = f"{query}_epitopes.fasta"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        description = ''
        for entry in epitopes_data:
            print(entry)
            if entry['description'] != description:
                description = entry['description']
                response.write(f'\n>{description}\n')

            sequence = entry['sequence']

            # Write the protein sequence
            response.write(f'{sequence}\t')

        return response
    else:
        # Handle the case where there is no data
        return HttpResponse("No data available.")
    
####funding
def fund(request):
    return render(request, "poxidb/funding.html")