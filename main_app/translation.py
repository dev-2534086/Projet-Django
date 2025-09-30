from modeltranslation.translator import register, TranslationOptions
from .models import Interest, Question, Choice

@register(Interest)
class InterestTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ('question_text',)

@register(Choice)
class ChoiceTranslationOptions(TranslationOptions):
    fields = ('choice_text',)
