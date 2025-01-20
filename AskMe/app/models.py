from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, F, Q

class QuestionManager(models.Manager):
    def new_questions(self, user=None):
        questions = self.annotate(
            like_count=Count('questionlike', filter=Q(questionlike__type='like')),
            dislike_count=Count('questionlike', filter=Q(questionlike__type='dislike')),
            rating=F('like_count') - F('dislike_count')
        ).order_by('-created_at')

        if user:
            questions = questions.annotate(
                liked=Count('questionlike', filter=Q(questionlike__user=user, questionlike__question=F('id'), questionlike__type='like')),
                disliked=Count('questionlike', filter=Q(questionlike__user=user, questionlike__question=F('id'), questionlike__type='dislike'))
            )
        else:
            questions = questions.annotate(
                liked=models.Value(False, output_field=models.BooleanField()),
                disliked=models.Value(False, output_field=models.BooleanField())
            )

        return questions

    def sorted_by_likes(self, user=None):
        questions = self.annotate(
            like_count=Count('questionlike', filter=Q(questionlike__type='like')),
            dislike_count=Count('questionlike', filter=Q(questionlike__type='dislike')),
            rating=F('like_count') - F('dislike_count')
        ).order_by('-rating', '-created_at') 

        if user:
            questions = questions.annotate(
                liked=Count('questionlike', filter=Q(questionlike__user=user, questionlike__question=F('id'), questionlike__type='like')),
                disliked=Count('questionlike', filter=Q(questionlike__user=user, questionlike__question=F('id'), questionlike__type='dislike'))
            )
        else:
            questions = questions.annotate(
                liked=models.Value(False, output_field=models.BooleanField()),
                disliked=models.Value(False, output_field=models.BooleanField())
            )

        return questions

    def get_tags(self, tag, user=None):
        questions = self.annotate(
            like_count=Count('questionlike', filter=Q(questionlike__type='like')),
            dislike_count=Count('questionlike', filter=Q(questionlike__type='dislike')),
            rating=F('like_count') - F('dislike_count')
        ).filter(tags__name=tag).order_by('-created_at')

        if user:
            questions = questions.annotate(
                liked=Count('questionlike', filter=Q(questionlike__user=user, questionlike__question=F('id'), questionlike__type='like')),
                disliked=Count('questionlike', filter=Q(questionlike__user=user, questionlike__question=F('id'), questionlike__type='dislike'))
            )
        else:
            questions = questions.annotate(
                liked=models.Value(False, output_field=models.BooleanField()),
                disliked=models.Value(False, output_field=models.BooleanField())
            )

        return questions


class AnswerManager(models.Manager):
    def sorted_by_likes(self, question, user=None):
        answers = self.filter(question=question).annotate(
            like_count=Count('answerlike', filter=Q(answerlike__type='like')),
            dislike_count=Count('answerlike', filter=Q(answerlike__type='dislike')),
            rating=F('like_count') - F('dislike_count')
        ).order_by('-is_correct', '-rating', '-created_at')

        if user:
            answers = answers.annotate(
                liked=Count('answerlike', filter=Q(answerlike__user=user, answerlike__answer=F('id'), answerlike__type='like')),
                disliked=Count('answerlike', filter=Q(answerlike__user=user, answerlike__answer=F('id'), answerlike__type='dislike'))
            )
        else:
            answers = answers.annotate(
                liked=models.Value(False, output_field=models.BooleanField()),
                disliked=models.Value(False, output_field=models.BooleanField())
            )

        return answers


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='questions')
    title = models.CharField(max_length=256)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects = QuestionManager()  

    @property
    def answer_count(self):
        return self.answers.count() 
    
    @property
    def rate(self):
        return self.rating
    
    def like_count(self):
        return self.questionlike.filter(type='like').count()

    def dislike_count(self):
        return self.questionlike.filter(type='dislike').count()
    
    def rating(self):
        return self.like_count() - self.dislike_count()

    def __str__(self):
        return self.title


class Answer(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = AnswerManager()

    @property
    def rate(self):
        return self.rating

    def like_count(self):
        return self.answerlike.filter(type='like').count()

    def dislike_count(self):
        return self.answerlike.filter(type='dislike').count()
    
    def rating(self):
        return self.like_count() - self.dislike_count()

    def __str__(self):
        return f'Answer by {self.author.user.username} to {self.question.title}'


class QuestionLike(models.Model):
    LIKE_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='questionlike')
    type = models.CharField(max_length=7, choices=LIKE_CHOICES, default='like') 

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f'{self.type.capitalize()} from {self.user.user.username} to {self.question.title}'


class AnswerLike(models.Model):
    LIKE_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='answerlike')
    type = models.CharField(max_length=7, choices=LIKE_CHOICES, default='like')

    class Meta:
        unique_together = ('user', 'answer')

    def __str__(self):
        return f'{self.type.capitalize()} from {self.user.user.username} to {self.answer}'
