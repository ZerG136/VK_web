from django.core.management.base import BaseCommand
from app.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike

class Command(BaseCommand):
    help = "Очистить базу данных"

    def handle(self, *args, **options):
        Profile.objects.all().delete()
        Question.objects.all().delete()
        Answer.objects.all().delete()
        Tag.objects.all().delete()
        QuestionLike.objects.all().delete()
        AnswerLike.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("База данных очищена"))
