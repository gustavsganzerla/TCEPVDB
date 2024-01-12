import csv
from django.core.management.base import BaseCommand
from poxidb.models import Epitope
import os


class Command(BaseCommand):
    help = 'Import data from a proteome file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type = str)

    def handle(self, *args, **options):
        file_path = options['file_path']
        organism_name = os.path.splitext(os.path.basename(file_path))[0]

        with open(file_path, 'r') as file:
            vetor_dados= file.readlines() #jogar o arquivo de entrada para uma lista
            vetor_dados = [line3.strip() for line3 in vetor_dados]#retira o \n da list

            for item in vetor_dados:
                aux = item.split("\t")
                fk = aux[0]

                for element in aux[2:]:
                    if element!='NA':
                        if '.' not in element:
                            epitope = element
                        else:
                            score = element

                            Epitope.objects.create(
                                description = fk,
                                sequence = epitope,
                                epitope_score = score,
                                organism = organism_name
                                )           
                
                
                

                          
                    
                                      
        self.stdout.write(self.style.SUCCESS('Data imported successfully.'))