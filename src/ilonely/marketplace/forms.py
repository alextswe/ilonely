from django import forms
from marketplace.models import Product

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ('name', 'price', 'photo', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class':'form-control'})
        self.fields['price'].widget.attrs.update({'class':'form-control'})
        self.fields['photo'].widget.attrs.update({'id':'productPhoto'})
        self.fields['description'].widget.attrs.update({'class':'form-control'}, rows="4", cols="50", )

class EditProduct(forms.ModelForm):

    class Meta:
        model = Product
        fields = ('name', 'price', 'photo', 'description', 'sold')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class':'form-control'})
        self.fields['price'].widget.attrs.update({'class':'form-control'})
        self.fields['photo'].widget.attrs.update({'id':'productPhoto'})
        self.fields['description'].widget.attrs.update({'class':'form-control'}, rows="4", cols="50", )
        # self.fields['sold'].widget.attrs.update({'class':'form-control'})
    