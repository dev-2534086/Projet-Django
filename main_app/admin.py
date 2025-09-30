from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin
from django.contrib import admin
from django import forms
from django.utils.html import format_html

from .models import ContactMessage, Respondent, Interest, Question, Choice, Response
from modeltranslation.admin import TranslationAdmin


# === Respondent ===
@admin.register(Respondent)
class RespondentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'submitted_at', 'get_interests', 'thumbnail')
    search_fields = ('name', 'email')
    readonly_fields = ('image_preview',)

    def get_interests(self, obj):
        return ", ".join([interest.name for interest in obj.interests.all()])
    get_interests.short_description = "Centres d'intérêt"

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.image.url)
        return "-"
    thumbnail.short_description = 'Miniature'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" style="margin-top:10px;" />', obj.image.url)
        return "Aucune image"
    image_preview.short_description = 'Aperçu (image actuelle)'


# === Response ===
@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('respondent', 'get_question', 'get_choice', 'answered_at')
    list_select_related = ('respondent', 'choice', 'choice__question')
    search_fields = ('respondent__name', 'choice__choice_text', 'choice__question__question_text')
    list_filter = ('answered_at',)
    
    def get_question(self, obj):
        return obj.choice.question.question_text
    get_question.short_description = 'Question'
    
    def get_choice(self, obj):
        return obj.choice.choice_text
    get_choice.short_description = 'Réponse'


# === Group personnalisé ===
class CustomGroupAdminForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple('Utilisateurs', is_stacked=False)
    )

    class Meta:
        model = Group
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save(self, commit=True):
        group = super().save(commit=False)
        if commit:
            group.save()
        if group.pk:
            group.user_set.set(self.cleaned_data['users'])
            self.save_m2m()
        return group


class CustomGroupAdmin(GroupAdmin):
    form = CustomGroupAdminForm
    filter_horizontal = ['permissions'] 


admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)


# === Autres modèles traduits ===
@admin.register(Question)
class QuestionAdmin(TranslationAdmin):
    list_display = ('question_text', 'pub_date')


@admin.register(Choice)
class ChoiceAdmin(TranslationAdmin):
    list_display = ('choice_text', 'question', 'votes')


@admin.register(Interest)
class InterestAdmin(TranslationAdmin):
    list_display = ('name',)
