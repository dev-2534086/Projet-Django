from django.contrib import admin
from .models import ContactMessage, Respondent, Interest, Question, Choice, Response
from django.utils.html import format_html

@admin.register(Respondent)
class RespondentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'submitted_at', 'get_interests', 'image_preview')
    search_fields = ('name', 'email')
    
    def get_interests(self, obj):
        return ", ".join([interest.name for interest in obj.interests.all()])
    get_interests.short_description = "Centres d'intérêt"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"
    
    image_preview.short_description = 'Aperçu'

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


# Pour l'admin
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Interest)
admin.site.register(ContactMessage)