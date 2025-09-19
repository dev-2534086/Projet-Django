from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Count
from django.core.paginator import Paginator

from main_app.forms import ChoiceForm, ContactForm, QuestionForm, RespondentForm
from .models import Choice, Question, Respondent, Response

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login


def home(request):
    sort_param = request.GET.get('sort', 'pub_date')  # par défaut tri par date
    sort_order = request.GET.get('order', 'desc')     # par défaut décroissant

    order_prefix = '-' if sort_order == 'desc' else ''
    sort_field = f"{order_prefix}{sort_param}"

    # 🔸 Afficher selon l'état de connexion
    if request.user.is_authenticated:
        questions = Question.objects.filter(creator=request.user)
    else:
        questions = Question.objects.all()

    questions = questions.annotate(
        response_count=Count('choice__response')
    ).order_by(sort_field)

    paginator = Paginator(questions, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main_app/home.html', {
        'page_obj': page_obj,
        'current_sort': sort_param,
        'current_order': sort_order,
    })

def about(request):
    return render(request, 'main_app/about.html')

def contact(request):
    form = ContactForm()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact')

    return render(request, 'main_app/contact.html', {
        'form': form
    })

def respondents_list(request):
    respondents = Respondent.objects.all().order_by('-submitted_at')
    context = {'respondents': respondents}
    return render(request, 'main_app/respondents_list.html', context)

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        choice_id = request.POST.get('choice')
        if choice_id:
            choice = get_object_or_404(Choice, pk=choice_id, question=question)
            choice.votes += 1
            choice.save()
            return redirect('home')
        else:
            return HttpResponse("Vous devez sélectionner une option.", status=400)
    else:
        return HttpResponse("Méthode non autorisée", status=405)
    
def question_detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.user.is_authenticated:
        # 🔐 Si utilisateur connecté : afficher les réponses à cette question
        responses = Response.objects.filter(choice__question=question).select_related('respondent', 'choice')
        return render(request, 'main_app/question_detail_admin.html', {
            'question': question,
            'responses': responses,
        })

    # 🔓 Si non connecté : traitement du formulaire
    if request.method == "POST":
        form = RespondentForm(request.POST, request.FILES, question=question)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            name = form.cleaned_data.get('name')
            interests = form.cleaned_data.get('interests')
            image = form.cleaned_data.get('image')

            # Recherche ou création du respondent
            respondent = Respondent.objects.filter(email=email).first() if email else None

            if respondent is None:
                respondent = Respondent.objects.create(name=name, email=email)
            else:
                if respondent.name != name:
                    respondent.name = name
                if image:
                    respondent.image = image
                respondent.save()

            if interests:
                respondent.interests.set(interests)
            else:
                respondent.interests.clear()

            choice = form.cleaned_data['choice']
            Response.objects.create(respondent=respondent, choice=choice)

            return redirect('home')
    else:
        form = RespondentForm(question=question)

    return render(request, 'main_app/question_detail.html', {
        'question': question,
        'form': form,
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Votre compte a été créé avec succès ! Vous êtes connecté.")
            login(request, user)
            return redirect('question_list')
    else:
        form = UserCreationForm()
    return render(request, 'main_app/register.html', {'form': form})

@login_required
def question_list(request):
    # Questions créées par l'utilisateur connecté
    questions = Question.objects.filter(creator=request.user).order_by('-pub_date')
    return render(request, 'main_app/question_list.html', {'questions': questions})

# Créer un sondage
@login_required
def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.creator = request.user
            question.pub_date = timezone.now()
            question.save()
            return redirect('question_list')
    else:
        form = QuestionForm()
    return render(request, 'main_app/question_form.html', {'form': form})

# Modifier un sondage
@login_required
def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if question.creator != request.user:
        return HttpResponseForbidden("Vous n'avez pas le droit de modifier ce sondage.")
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('question_list')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'main_app/question_form.html', {'form': form})

def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    question.delete()
    return redirect('question_list')

# Ajouter un choix
@login_required
def add_choice(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.creator != request.user:
        return redirect('question_list')

    if request.method == "POST":
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            return redirect('edit_question', pk=question.pk)
    else:
        form = ChoiceForm()

    return render(request, 'main_app/add_choice.html', {'form': form, 'question': question})

# Supprimer un choix
@login_required
def delete_choice(request, pk):
    choice = get_object_or_404(Choice, pk=pk)
    question_id = choice.question.pk
    choice.delete()
    return redirect('edit_question', pk=question_id)
