from django import forms

class SendMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Type your message here ...',
        'maxlength': 1000,
        'style': 'height: 80px;',
        'id': 'chat-input',
        'class': "form-control input"
    }), label="")