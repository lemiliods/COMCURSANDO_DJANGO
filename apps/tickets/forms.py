from django import forms


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
