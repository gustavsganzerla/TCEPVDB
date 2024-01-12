import csv
from django.core.management.base import BaseCommand
from poxidb.models import Proteome
from Bio import SeqIO
from Bio.Seq import Seq
import os


class Command(BaseCommand):
    help = 'Import data from a proteome file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type = str)

    def handle(self, *args, **options):
        file_path = options['file_path']
        organism_name = os.path.splitext(os.path.basename(file_path))[0]

        with open (file_path, 'r') as file:

           for line in file:
            aux = line.split("\t")
            if len(aux) == 4:
                Proteome.objects.create(
                    description=str(aux[0]),
                    organism=organism_name,
                    antigen_score=str(aux[2]),
                    protein=str(aux[3])
                )
                          
                    
                                      
        self.stdout.write(self.style.SUCCESS('Data imported successfully.'))