from django.db import models

class CropInfo(models.Model):
    name = models.CharField(max_length=100, unique=True)
    growth_duration_days = models.IntegerField()
    fertilizer_info = models.TextField()
    per_hectare_yield = models.FloatField()
    total_production = models.FloatField()
    
    def __str__(self):
        return self.name
