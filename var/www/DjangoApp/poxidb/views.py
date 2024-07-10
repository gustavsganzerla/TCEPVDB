from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from . import models

from collections import Counter
from django.db.models import Count
from django.shortcuts import render
from django.utils.html import mark_safe
from django.template import Template, Context

from . forms import SearchForm, ContactForm
import csv
import requests
import json
import certifi
import urllib.request
from django.views.decorators.csrf import csrf_exempt
from Bio.SeqUtils.ProtParam import ProteinAnalysis

from django.core.mail import EmailMessage, get_connection
from django.conf import settings


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

def characterize_proteome(request, organism):
    csv_content = []
    output = []
    allowed_amino_acids = set("ARNDCQEGHIJKLMFPSTWYV")
    proteome = models.Proteome.objects.filter(organism=organism)

    proteome_data = list(proteome.values())
    
    for item in proteome_data:
        protein_seq = item['protein'].replace("\n", "")
        if all(aa in allowed_amino_acids for aa in protein_seq):

            if (instability_index(protein_seq)) < 40:
                stability = "Stable"
            else:
                stability = "Unstable"
            output.append({
                'sequence':protein_seq,
                'length':len(protein_seq),
                'gravy':gravy(protein_seq),
                'aliphatic_index':aliphatic_index(protein_seq),
                'instability_index':instability_index(protein_seq),
                'stability':stability,
                'molecular_weight':molecular_weight(protein_seq),
                'aromaticity':aromaticity(protein_seq),
                'isoelectric_point':isoelectric_point(protein_seq),
                'atomic_composition':atomic_composition(protein_seq),
                'secondary_structure_fraction':secondary_structure_fraction(protein_seq),
                'molar_extinction_coefficient':molar_extinction_coefficient(protein_seq),
                'charge_at_pH':charge_at_pH(protein_seq, 7),
                'count_amino_acids':count_amino_acids(protein_seq),
                'get_amino_acids_percent':get_amino_acids_percent(protein_seq)
            })
    if output:
        csv_content = []
        csv_content.append(['Sequence',
                           'Length',
                           'Gravy',
                           'Aliphatic Index',
                           'Instability Index',
                           'Stability',
                           'Molecular Weight',
                           'Aromaticity',
                           'Isoelectric Point',
                           'Charge at pH 7'])
        for item in output:
            csv_content.append([item['sequence'],
                               item['length'],
                               item['gravy'],
                               item['aliphatic_index'],
                               item['instability_index'],
                               item['stability'],
                               item['molecular_weight'],
                               item['aromaticity'],
                               item['isoelectric_point'],
                               item['charge_at_pH']
                               ])
        request.session['csv_content'] = csv_content
    return render(request, 'poxidb/view_characterization.html', context={'output':output,
                                                                         'csv_content':csv_content})

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

def characterize_antigens(request, query):
    csv_content = []
    allowed_amino_acids = set("ARNDCQEGHIJKLMFPSTWYV")
    antigens_data = []
    antigens = []
    query2 = ""
    output = []


    if "_organism" in query:
        query2 = query.replace("_organism", "")

        antigens_queryset = models.Proteome.objects.filter(organism__contains = query2,
                                                antigen_score__gt=0.5)

    elif "_antigen" in query:
        query2 = query.replace("_antigen", "")
        antigens_queryset = models.Proteome.objects.filter(description__contains = query2,
                                                   antigen_score__gt=0.5)
    else:
        antigens_queryset = None

    if antigens_queryset is not None:
        antigens = list(antigens_queryset.values())

    for antigen in antigens:
        antigen_sequence = antigen['protein'].replace("\n", "")
        if all(aa in allowed_amino_acids for aa in antigen_sequence):
            if (instability_index(antigen_sequence)) < 40:
                stability = "Stable"
            else:
                stability = "Unstable"
            output.append({
                'sequence':antigen_sequence,
                'length':len(antigen_sequence),
                'gravy':gravy(antigen_sequence),
                'aliphatic_index':aliphatic_index(antigen_sequence),
                'instability_index':instability_index(antigen_sequence),
                'stability':stability,
                'molecular_weight':molecular_weight(antigen_sequence),
                'aromaticity':aromaticity(antigen_sequence),
                'isoelectric_point':isoelectric_point(antigen_sequence),
                'atomic_composition':atomic_composition(antigen_sequence),
                'secondary_structure_fraction':secondary_structure_fraction(antigen_sequence),
                'molar_extinction_coefficient':molar_extinction_coefficient(antigen_sequence),
                'charge_at_pH':charge_at_pH(antigen_sequence, 7),
                'count_amino_acids':count_amino_acids(antigen_sequence),
                'get_amino_acids_percent':get_amino_acids_percent(antigen_sequence)
            })
    if output:
        csv_content = []
        csv_content.append(['Sequence',
                           'Length',
                           'Gravy',
                           'Aliphatic Index',
                           'Instability Index',
                           'Stability',
                           'Molecular Weight',
                           'Aromaticity',
                           'Isoelectric Point',
                           'Charge at pH 7'])
        for item in output:
            csv_content.append([item['sequence'],
                               item['length'],
                               item['gravy'],
                               item['aliphatic_index'],
                               item['instability_index'],
                               item['stability'],
                               item['molecular_weight'],
                               item['aromaticity'],
                               item['isoelectric_point'],
                               item['charge_at_pH']
                               ])
        request.session['csv_content'] = csv_content
    return render(request, 'poxidb/view_characterization.html', context={'output':output,
                                                                         'csv_content':csv_content})

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

def characterize_individual_epitopes(request, description):
    csv_content = []
    output = []
    epitope_query = models.Epitope.objects.filter(description=description)
    epitopes_data = list(epitope_query.values())


    for epitope in epitopes_data:
        if (instability_index(epitope['sequence'])) < 40:
            stability = "Stable"
        else:
            stability = "Unstable"
        output.append({
            'sequence':epitope['sequence'],
            'length':len(epitope['sequence']),
            'gravy':gravy(epitope['sequence']),
            'aliphatic_index':aliphatic_index(epitope['sequence']),
            'instability_index':instability_index(epitope['sequence']),
            'stability':stability,
            'molecular_weight':molecular_weight(epitope['sequence']),
            'aromaticity':aromaticity(epitope['sequence']),
            'isoelectric_point':isoelectric_point(epitope['sequence']),
            'atomic_composition':atomic_composition(epitope['sequence']),
            'secondary_structure_fraction':secondary_structure_fraction(epitope['sequence']),
            'molar_extinction_coefficient':molar_extinction_coefficient(epitope['sequence']),
            'charge_at_pH':charge_at_pH(epitope['sequence'], 7),
            'count_amino_acids':count_amino_acids(epitope['sequence']),
            'get_amino_acids_percent':get_amino_acids_percent(epitope['sequence'])
        })
    if output:
        csv_content = []
        csv_content.append(['Sequence',
                           'Length',
                           'Gravy',
                           'Aliphatic Index',
                           'Instability Index',
                           'Stability',
                           'Molecular Weight',
                           'Aromaticity',
                           'Isoelectric Point',
                           'Charge at pH 7'])
        for item in output:
            csv_content.append([item['sequence'],
                               item['length'],
                               item['gravy'],
                               item['aliphatic_index'],
                               item['instability_index'],
                               item['stability'],
                               item['molecular_weight'],
                               item['aromaticity'],
                               item['isoelectric_point'],
                               item['charge_at_pH']
                               ])
        request.session['csv_content'] = csv_content
    return render(request, 'poxidb/view_characterization.html', context={'output':output,
                                                                         'csv_content':csv_content})
   

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
                             'n_epitopes':len(epitopes)
                             })

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

def characterize_epitopes(request, query):
    allowed_amino_acids = set("ARNDCQEGHIJKLMFPSTWYV")
    epitopes = []
    query2 = ""
    output = []
    stability = ""
    csv_content = []

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
    
    for epitope in epitopes:
        if all(aa in allowed_amino_acids for aa in epitope['sequence']):
            if (instability_index(epitope['sequence'])) < 40:
                stability = "Stable"
            else:
                stability = "Unstable"
            output.append({
                'sequence':epitope['sequence'],
                'length':len(epitope['sequence']),
                'gravy':gravy(epitope['sequence']),
                'aliphatic_index':aliphatic_index(epitope['sequence']),
                'instability_index':instability_index(epitope['sequence']),
                'stability':stability,
                'molecular_weight':molecular_weight(epitope['sequence']),
                'aromaticity':aromaticity(epitope['sequence']),
                'isoelectric_point':isoelectric_point(epitope['sequence']),
                'atomic_composition':atomic_composition(epitope['sequence']),
                'secondary_structure_fraction':secondary_structure_fraction(epitope['sequence']),
                'molar_extinction_coefficient':molar_extinction_coefficient(epitope['sequence']),
                'charge_at_pH':charge_at_pH(epitope['sequence'], 7),
                'count_amino_acids':count_amino_acids(epitope['sequence']),
                'get_amino_acids_percent':get_amino_acids_percent(epitope['sequence'])
            })

    if output:
        csv_content = []
        csv_content.append(['Sequence',
                           'Length',
                           'Gravy',
                           'Aliphatic Index',
                           'Instability Index',
                           'Stability',
                           'Molecular Weight',
                           'Aromaticity',
                           'Isoelectric Point',
                           'Charge at pH 7'])
        for item in output:
            csv_content.append([item['sequence'],
                               item['length'],
                               item['gravy'],
                               item['aliphatic_index'],
                               item['instability_index'],
                               item['stability'],
                               item['molecular_weight'],
                               item['aromaticity'],
                               item['isoelectric_point'],
                               item['charge_at_pH']
                               ])
        request.session['csv_content'] = csv_content

    return render(request, 'poxidb/view_characterization.html', context={'output':output,
                                                                         'csv_content': csv_content})
           

####funding
def fund(request):
    return render(request, "poxidb/funding.html")

####download characterization
def download_characterization(request):
    csv_content = request.session.get('csv_content', None)
    if csv_content:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="output.csv"'

        csv_writer = csv.writer(response)
        for row in csv_content:
            csv_writer.writerow(row)

        return response
    else:
        # Handle the case where there is no CSV content
        return HttpResponse("No CSV content available.")


####contact
def contact(request):
    if request.method=='POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            collected_data = form.cleaned_data
            subject = collected_data.get('subject')
            email = collected_data.get('email')
            message = collected_data.get('message')

            with get_connection(
                host = settings.EMAIL_HOST,
                port = settings.EMAIL_PORT,
                username = settings.EMAIL_HOST_USER,
                password = settings.EMAIL_HOST_PASSWORD,
                use_ssl = settings.EMAIL_USE_SSL
            ) as connection:
                subject = subject
                email_from = settings.EMAIL_HOST_USER
                recipient_list = ['sganzerlagustavo@gmail.com']
                message = message+"\n"+email

                email = EmailMessage(
                    subject,
                    message,
                    email_from,
                    recipient_list
                )
                email.send()

                return render(request, "poxidb/contact_success.html")
            


    else:
        form = ContactForm()
    
    return render(request, 'poxidb/contact.html', {'form':form})

###protein characterization functions
def gravy(protein):
    gravy_values = {
        'A':  1.8 , 
        'R': -4.5,  
        'N': -3.5,  
        'D': -3.5,  
        'C':  2.5,  
        'Q': -3.5,  
        'E': -3.5,  
        'G': -0.4,  
        'H': -3.2,  
        'I':  4.5,  
        'L':  3.8,  
        'K': -3.9,  
        'M':  1.9,  
        'F':  2.8,  
        'P': -1.6,  
        'S': -0.8,  
        'T': -0.7,  
        'W': -0.9,  
        'Y': -1.3,  
        'V':  4.2  
        }

    sequence_gravy = []
    for aminoacid in protein:
        gravy_value = gravy_values.get(aminoacid)
        sequence_gravy.append(gravy_value)
    return round(sum(sequence_gravy)/len(protein),2)
    
def aliphatic_index(protein):

    a = 2.9
    b = 3.9

    counts = {
        'A': 0, 
        'V': 0,
        'I': 0, 
        'L': 0, 
    }

    total_amino_acids = len(protein)

    for amino_acid in protein:
        if amino_acid in counts:
            counts[amino_acid] += 1

    mole_percent = {aa: (count / total_amino_acids) * 100 for aa, count in counts.items()}

    aliphatic_index = mole_percent['A'] + a * mole_percent['V'] + b * (mole_percent['I'] + mole_percent['L'])

    return round(aliphatic_index,2)       

def instability_index(protein):
    x = ProteinAnalysis(protein)
    return(round(x.instability_index(),2))

def molecular_weight(protein):
    x = ProteinAnalysis(protein)
    return(round(x.molecular_weight(),2))

def aromaticity(protein):
    x = ProteinAnalysis(protein)
    return(round(x.aromaticity(),2))

def isoelectric_point(protein):
    x = ProteinAnalysis(protein)
    return(round(x.isoelectric_point(),2))

def atomic_composition(protein):
    c = 0
    h = 0
    o = 0
    n = 0
    s = 0

    for aa in protein:
        if aa == 'A': #Alanine (Ala)
            c+=3
            h+=7
            o+=2
            n+=1
            s+=0
        if aa == 'R': #Arginine (Arg)
            c+=6
            h+=14
            o+=2
            n+=4
            s+=0
        if aa == 'N':#Asparagine (Asn)
            c+=4
            h+=8
            o+=3
            n+=2
            s+=0
        if aa == 'D':#Aspartic Acid (Asp)
            c+=4
            h+=7
            o+=4
            n+=1
            s+=0
        if aa == 'C':#Cysteine (Cys)
            c+=3
            h+=7
            o+=2
            n+=1
            s+=1
        if aa == 'Q':#Glutamine (Gln)
            c+=5
            h+=10
            o+=3
            n+=2
            s+=0
        if aa == 'E':#Glutamic Acid (Glu)
            c+=5
            h+=9
            o+=4
            n+=1
            s+=0
        if aa == 'G':#Glycine (Gly)
            c+=2
            h+=5
            o+=2
            n+=1
            s+=0
        if aa == 'H':#Histidine (His)
            c+=6
            h+=9
            o+=2
            n+=3
            s+=0
        if aa == 'I':#Isoleucine (Ile)
            c+=6
            h+=13
            o+=2
            n+=1
            s+=0
        if aa == 'L':#Leucine (Leu)
            c+=6
            h+=13
            o+=2
            n+=1
            s+=0
        if aa == 'K':#Lysine (Lys)
            c+=6
            h+=14
            o+=2
            n+=2
            s+=0
        if aa == 'M':#Methionine (Met)
            c+=5
            h+=11
            o+=2
            n+=1
            s+=1
        if aa == 'F':#Phenylalanine (Phe)
            c+=9
            h+=11
            o+=2
            n+=1
            s+=0
        if aa == 'P':#Proline (Pro)
            c+=5
            h+=9
            o+=2
            n+=1
            s+=0
        if aa == 'S':#Serine (Ser
            c+=3
            h+=7
            o+=3
            n+=1
            s+=0
        if aa == 'T':#Threonine (Thr)
            c+=4
            h+=9
            o+=3
            n+=1
            s+=0
        if aa == 'W':#Tryptophan (Trp)
            c+=11
            h+=12
            o+=2
            n+=2
            s+=0
        if aa == 'Y':#Tyrosine (Tyr)
            c+=9
            h+=11
            o+=3
            n+=1
            s+=0
        if aa == 'V':#Valine (Val)
            c+=5
            h+=11
            o+=2
            n+=1
            s+=0


            
    return c,h,o,n,s

def secondary_structure_fraction(protein):
    x = ProteinAnalysis(protein)
    raw_values = x.secondary_structure_fraction()
    rounded_values = tuple(round(value, 2) for value in raw_values)  # Round to 2 decimal places
    return rounded_values

def molar_extinction_coefficient(protein):
    x = ProteinAnalysis(protein)
    return(x.molar_extinction_coefficient())

def charge_at_pH(protein, ph):
    x = ProteinAnalysis(protein)
    return round(x.charge_at_pH(ph),2)

def count_amino_acids(protein):
    x = ProteinAnalysis(protein)
    return(x.count_amino_acids())

def get_amino_acids_percent(protein):
    x = ProteinAnalysis(protein)
    return x.get_amino_acids_percent()




