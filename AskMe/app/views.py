import json
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from app.forms import LoginForm, UserForm, ProfileEditForm, QuestionForm, AnswerForm
from .models import Tag, Question, Answer, Profile, QuestionLike, AnswerLike
from django.db.models import Count, F, Q


def paginate(objects_list, request, per_page=10):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(objects_list, per_page)

    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page


def index(request):
    questions = Question.objects.new_questions()
    user_profile = None
    if request.user.is_authenticated:
        user_profile = get_object_or_404(Profile, user=request.user)

    questions = Question.objects.new_questions(user=user_profile)
    page = paginate(questions, request, per_page=5)

    members = set()
    ind = 0
    while ind < len(questions) and len(members) <= 10:
        if not questions[ind].author.user.username in members:
            members.add(questions[ind].author.user.username)
        ind += 1

    tags = set(questions[0].tags.all())

    return render(request, 'index.html',
    context={
        'questions': page.object_list, 
        'page_obj': page, 
        'user_profile': user_profile,
        'members': members,
        'tags': tags
    })


def hot(request):
    user_profile = None
    if request.user.is_authenticated:
        user_profile = get_object_or_404(Profile, user=request.user)

    questions = Question.objects.sorted_by_likes(user=user_profile)
    page = paginate(questions, request, per_page=5)

    members = set()
    ind = 0
    while ind < len(questions) and len(members) <= 10:
        if not questions[ind].author.user.username in members:
            members.add(questions[ind].author.user.username)
        ind += 1

    tags = set(questions[0].tags.all())

    return render(request, 'hot.html',
    context={
        'questions': page.object_list, 
        'page_obj': page, 
        'user_profile': user_profile,
        'members': members,
        'tags': tags
    })


def tag(request, tag_name):
    user_profile = None
    if request.user.is_authenticated:
        user_profile = get_object_or_404(Profile, user=request.user)

    curr_tag = get_object_or_404(Tag, name=tag_name)
    tag_questions = Question.objects.get_tags(curr_tag, user=user_profile)

    page = paginate(tag_questions, request, per_page=5)

    questions = Question.objects.new_questions(user=user_profile)
    members = set()
    ind = 0
    while ind < len(questions) and len(members) <= 10:
        if not questions[ind].author.user.username in members:
            members.add(questions[ind].author.user.username)
        ind += 1

    tags = set(questions[0].tags.all())

    return render(request, 'tags.html',
    context={
        'questions': page.object_list, 
        'page_obj': page, 
        'tag_name': curr_tag.name,
        'user_profile': user_profile,
        'members': members,
        'tags': tags
    })


def one_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    user_profile = None
    if request.user.is_authenticated:
        user_profile = get_object_or_404(Profile, user=request.user)

    question = Question.objects.annotate(
        qlike_count=Count('questionlike', filter=Q(questionlike__type='like')),
        qdislike_count=Count('questionlike', filter=Q(questionlike__type='dislike')),
        qlike_dislike_diff=F('qlike_count') - F('qdislike_count')
    ).get(id=question_id)

    if user_profile:
        question_liked = question.questionlike.filter(user=user_profile, type='like').exists()
        question_disliked = question.questionlike.filter(user=user_profile, type='dislike').exists()
    else:
        question_liked = False
        question_disliked = False
    
    answers = Answer.objects.sorted_by_likes(question, user=user_profile)
    form = AnswerForm(request.POST or None)
    page = paginate(answers, request, per_page=3)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            form.add_error('text', 'Please log in in order to submit answers.')
        elif form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = get_object_or_404(Profile, user=request.user)
            answer.save()
            return redirect(reverse('one_question', kwargs={'question_id': question.id}) + f'?page={page.paginator.num_pages}')

    questions = Question.objects.new_questions(user=user_profile)
    members = set()
    ind = 0
    while ind < len(questions) and len(members) <= 10:
        if not questions[ind].author.user.username in members:
            members.add(questions[ind].author.user.username)
        ind += 1

    tags = set(questions[0].tags.all())

    return render(request, 'answers.html',
        context={
            'question': question,
            'question_liked': question_liked,
            'question_disliked': question_disliked,
            'page_obj': page,
            'answers': answers,
            'form': form,
            'user_profile': user_profile,
            'members': members,
            'tags': tags
        })


@csrf_protect
def login(request):
    form = LoginForm(request.POST or None)
    continue_url = request.POST.get('continue', None)
    if request.method == 'POST':
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)
                continue_url = request.session.get('continue_url', reverse('settings'))
                if 'continue_url' in request.session:
                    del request.session['continue_url']
                return redirect(continue_url)
            else:
                form.add_error('username', 'Invalid password or username.')

    user_profile = None
    if request.user.is_authenticated:
        user_profile = get_object_or_404(Profile, user=request.user)

    questions = Question.objects.new_questions(user=user_profile)
    members = set()
    ind = 0
    while ind < len(questions) and len(members) <= 10:
        if not questions[ind].author.user.username in members:
            members.add(questions[ind].author.user.username)
        ind += 1

    tags = set(questions[0].tags.all())

    return render(request, 'login.html',
        context={
            'form': form,
            'user_profile': user_profile,
            'members': members,
            'tags': tags
        })


@csrf_protect
def signup(request):
    form = UserForm(request.POST or None, request.FILES or None)
    user_profile = None
    if request.user.is_authenticated:
        user_profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect(reverse('settings'))

    questions = Question.objects.new_questions(user=user_profile)
    members = set()
    ind = 0
    while ind < len(questions) and len(members) <= 10:
        if not questions[ind].author.user.username in members:
            members.add(questions[ind].author.user.username)
        ind += 1

    tags = set(questions[0].tags.all())

    return render(request, 'signup.html',
        context={
            'form': form,
            'user_profile': user_profile,
            'members': members,
            'tags': tags
        })


@csrf_protect
def ask(request):
    if not request.user.is_authenticated:
        continue_url = request.POST.get('continue', reverse('ask'))
        request.session['continue_url'] = continue_url
        return redirect(reverse('login'))
    else:
        user = request.user
        user_profile = get_object_or_404(Profile, user=user)
        form = QuestionForm(request.POST or None)

        questions = Question.objects.new_questions(user=user_profile)
        members = set()
        ind = 0
        while ind < len(questions) and len(members) <= 10:
            if not questions[ind].author.user.username in members:
                members.add(questions[ind].author.user.username)
            ind += 1

        tags = set(questions[0].tags.all())

        if request.method == 'POST':
            if form.is_valid():
                question = form.save(get_object_or_404(Profile, user=request.user))
                return redirect('one_question', question_id=question.id)
            else:
                return render(request, 'ask.html',
                    context={
                        'form': form,
                        'user_profile': user_profile,
                        'members': members,
                        'tags': tags
                    })
        return render(request, 'ask.html',
            context={
                'form': form,
                'user_profile': user_profile,
                'members': members,
                'tags': tags
            })


@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))


@csrf_protect
def settings(request):
    if not request.user.is_authenticated:
        continue_url = request.POST.get('continue', reverse('profile/edit/'))
        request.session['continue_url'] = continue_url
        return redirect(reverse('login'))
    else:
        user = request.user
        user_profile, created = Profile.objects.get_or_create(user=user)
        form = ProfileEditForm(request.POST or None, request.FILES or None, instance=request.user)

        questions = Question.objects.new_questions(user=user_profile)
        members = set()
        ind = 0
        while ind < len(questions) and len(members) <= 10:
            if not questions[ind].author.user.username in members:
                members.add(questions[ind].author.user.username)
            ind += 1

        tags = set(questions[0].tags.all())

        if request.method == 'POST':
            if form.is_valid():
                user, user_profile = form.save()
                return redirect(reverse('settings'))
            else:
                return render(request, 'settings.html',
                    context={
                        'form': form,
                        'user_profile': user_profile,
                        'members': members,
                        'tags': tags
                    })
        return render(request, 'settings.html',
            context={
                'form': form,
                'user_profile': user_profile,
                'members': members,
                'tags': tags
            })


@csrf_protect
@login_required
def rate_question(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question_id = data.get("question_id")
            action = data.get("action")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return JsonResponse({"error": "Question not found"}, status=404)

        profile = request.user.profile
        
        existing_like = QuestionLike.objects.filter(user=profile, question=question).first()

        if existing_like:
            if existing_like.type == action:
                existing_like.delete()
            else:
                existing_like.type = action
                existing_like.save()
        else:
            QuestionLike.objects.create(user=profile, question=question, type=action)
        
        print(f"New rate: {question.rate}, like_count: {question.like_count()}, dislike_count: {question.dislike_count()}")

        question.refresh_from_db()
        return JsonResponse({
            "new_rate": question.rating(),  
            "like_count": question.like_count(),
            "dislike_count": question.dislike_count(),
        })

    return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_protect
@login_required
def rate_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            answer_id = data.get('answer_id')
            action = data.get("action")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            return JsonResponse({"error": "Question not found"}, status=404)

        profile = request.user.profile
        
        existing_like = AnswerLike.objects.filter(user=profile, answer=answer).first()

        if existing_like:
            if existing_like.type == action:
                existing_like.delete()
            else:
                existing_like.type = action
                existing_like.save()
        else:
            AnswerLike.objects.create(user=profile, answer=answer, type=action)

        answer.refresh_from_db()
        return JsonResponse({
            "new_rate": answer.rating(),  
            "like_count": answer.like_count(),
            "dislike_count": answer.dislike_count(),
        })

    return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_protect
@login_required
def mark_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged in to perform this action.'}, status=401)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            answer_id = data.get("answer_id")
            question_id = data.get("question_id")

            print(answer_id)
            print(question_id)

            question = get_object_or_404(Question, id=question_id)
            answer = get_object_or_404(Answer, id=answer_id)

            if question.author.user != request.user:
                return JsonResponse({'error': 'You are not the author of the question.'}, status=403)

            if answer.is_correct:
                answer.is_correct = False
                answer.save()
                return JsonResponse({'message': 'Answer unmarked as correct', 'answer_id': answer.id})
            
            answer.is_correct = True
            answer.save()

            return JsonResponse({'message': 'Answer marked as correct', 'answer_id': answer.id})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
