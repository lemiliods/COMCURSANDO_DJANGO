from django import forms


class TicketForm(forms.Form):
    """
    Formulário público para envio de prova.
    """
    cliente_nome = forms.CharField(
        label='Nome Completo',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Seu nome completo',
            'class': 'form-control'
        })
    )
    
    cliente_email = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={
            'placeholder': 'seu@email.com (opcional)',
            'class': 'form-control'
        })
    )
    
    cliente_whatsapp = forms.CharField(
        label='WhatsApp',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '+5511966149003',
            'class': 'form-control'
        }),
        help_text='Formato: +55 + DDD + Número'
    )
    
    cliente_pix = forms.CharField(
        label='Chave PIX',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'CPF, e-mail, telefone ou chave aleatória',
            'class': 'form-control'
        })
    )
    
    arquivo_prova = forms.FileField(
        label='Arquivo da Prova',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        help_text='PDF, JPG ou PNG (máx. 10MB)'
    )
    
    aceito_termos = forms.BooleanField(
        label='Li e aceito os termos de consentimento',
        required=True,
        error_messages={
            'required': 'Você precisa aceitar os termos para continuar.'
        }
    )


class RecusarProvaForm(forms.Form):
    """
    Formulário para recusar prova com motivo.
    """
    motivo = forms.CharField(
        label='Motivo da Recusa',
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Descreva o motivo da recusa (será enviado por email ao participante)...'
        }),
        required=True,
        help_text='Este motivo será enviado por email ao participante.'
    )
