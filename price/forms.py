from django import forms

class CropPriceForm(forms.Form):
    State = forms.CharField(max_length=50)
    District = forms.CharField(max_length=50)
    Market = forms.CharField(max_length=50)
    Commodity = forms.CharField(max_length=50)
    Variety = forms.CharField(max_length=50)
    Grade = forms.CharField(max_length=50)
    Day = forms.IntegerField(min_value=1, max_value=31)
    Month = forms.IntegerField(min_value=1, max_value=12)
    Year = forms.IntegerField(min_value=2000, max_value=2100)
