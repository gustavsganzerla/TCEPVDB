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