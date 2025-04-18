from django import forms
from .models import CompanyStock

class PortfolioForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PortfolioForm, self).__init__(*args, **kwargs)
        for stock in CompanyStock.objects.all():
            self.fields[f'stock_{stock.company_id}'] = forms.IntegerField(
                label=f"{stock.cname} ({stock.company_id})",
                required=False,
                min_value=0
            )
