from django.db import models

# Create your models here.

class Proteome(models.Model):
    id = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=1000)
    protein = models.CharField(max_length=10000)
    organism = models.CharField(max_length=100)
    antigen = models.CharField(max_length=50)
    antigen_score = models.FloatField()

    def __str__(self):
        return f"{self.description}, {self.protein}, {self.antigen_score}, {self.antigen}"
    

class Epitope(models.Model):
    id = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=1000)
    sequence = models.CharField(max_length=50)
    epitope_score = models.FloatField()
    organism = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.description}, {self.sequence}, {self.epitope_score}"
