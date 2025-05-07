from django.db import models

class gear_value(models.Model):
    date = models.DateField(auto_now_add=True)  
    time = models.TimeField(auto_now_add=True)  
    value = models.CharField(max_length=450)    

    def __str__(self):
        return f"{self.date} {self.time} {self.value}"
