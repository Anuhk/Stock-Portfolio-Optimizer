from django.db import models

# Create your models here.


class CompanyStock(models.Model):
    company_id = models.CharField(max_length=20, primary_key=True)
    cname = models.CharField(max_length=100)
    current_price = models.FloatField()

class UserPortfolio(models.Model):
    user_id = models.IntegerField()
    company_id = models.IntegerField()
    total_shares = models.IntegerField()
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    
    def __str__(self):
        return f"Portfolio for User {self.user_id}"
