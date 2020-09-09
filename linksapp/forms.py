from django import forms


class EmailForm(forms.Form):
    email = forms.EmailField(label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'type': 'email', })
