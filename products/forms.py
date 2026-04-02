from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'image', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select rounded-3 border-0 bg-light','placeholder': 'Nhập tên danh mục'}),
            'name': forms.TextInput(attrs={'class': 'form-control rounded-3 border-0 bg-light', 'placeholder': 'Nhập tên điện thoại...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control rounded-3 border-0 bg-light', 'placeholder': 'Nhập giá tiền...'}),
            'image': forms.FileInput(attrs={'class': 'form-control rounded-3 border-0 bg-light'}),
            'description': forms.Textarea(attrs={'class': 'form-control rounded-3 border-0 bg-light', 'rows': 5, 'placeholder': 'Mô tả chi tiết sản phẩm...'}),
        }