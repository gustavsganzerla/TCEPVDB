from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from . import models

from collections import Counter
from django.db.models import Count
from django.shortcuts import render
from django.utils.html import mark_safe
from django.template import Template, Context

# Create your views here.
def poxidb(request):
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
    return render(request, "poxidb/poxidb.html", {'organism_data': organism_data})


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

            response.write(f'>{description}\n')

            response.write(f'{protein}\n')

        return response
    else:
        return HttpResponse("No data available.")

def visualize_antigens(request, organism):
    antigens = models.Proteome.objects.filter(organism = organism,
                                               antigen_score__gt=0.5)
    antigens_data = list(antigens.values())
    for item in antigens_data:
        epitopes = models.Epitope.objects.filter(description = item['description'])
        item['epitope_count'] = len(epitopes)

   
    return render(request, "poxidb/visualize_antigens.html",
                  context={'organism':organism,
                           'antigens':antigens_data,
                           'n_antigens':len(antigens)})

def download_antigens(request, organism):
    antigens = models.Proteome.objects.filter(organism=organism,
                                               antigen_score__gt=0.5)
    antigens_data = list(antigens.values())

    if antigens_data:
        response = HttpResponse(content_type='text/plain')
        filename = f"{organism}_antigens.fasta"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        for entry in antigens_data:
            description = entry['description']
            protein = entry['protein']

            response.write(f'>{description}\n')
            response.write(f'{protein}\n')

        return response
    else:
        return HttpResponse("No data available.")

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

def visualize_epitopes(request, organism):
    epitopes = models.Epitope.objects.filter(organism = organism)

    return render(request, "poxidb/visualize_epitopes.html",
                  context = {'epitopes':epitopes,
                             'organism':organism,
                             'n_epitopes':len(epitopes)})

def download_epitopes(request, organism):
    epitopes = models.Epitope.objects.filter(organism=organism)
    epitopes_data = list(epitopes.values())

    if epitopes_data:
        response = HttpResponse(content_type='text/plain')
        filename = f"{organism}_epitopes.fasta"
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