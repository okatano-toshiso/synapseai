from django.db import models
from django.utils import timezone

class Card(models.Model):
    CATEGORY_CHOICES = [
        ("instant", "即答"),
        ("elimination", "選択肢消去"),
        ("formula", "数式"),
        ("pytorch", "PyTorch対応"),
        ("term", "用語"),
    ]
    front = models.CharField("問題", max_length=255)
    back = models.TextField("答え・判断基準")
    category = models.CharField("種類", max_length=20, choices=CATEGORY_CHOICES, default="instant")
    chapter = models.CharField("章", max_length=100, blank=True)
    topic = models.CharField("論点", max_length=100, blank=True)
    trap = models.TextField("解説", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.front

class Progress(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE, related_name="progress")
    due_at = models.DateTimeField(default=timezone.now)
    interval_days = models.PositiveIntegerField(default=0)
    ease_factor = models.FloatField(default=2.5)
    repetitions = models.PositiveIntegerField(default=0)
    lapses = models.PositiveIntegerField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    correct_reviews = models.PositiveIntegerField(default=0)
    avg_seconds = models.FloatField(default=0)
    last_grade = models.PositiveSmallIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def accuracy(self):
        return round(self.correct_reviews / self.total_reviews * 100, 1) if self.total_reviews else 0

class StudySession(models.Model):
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    chapter_filter = models.CharField("絞り込んだ章", max_length=100, blank=True)
    category_filter = models.CharField("絞り込んだ種類", max_length=20, blank=True)

    @property
    def total_answered(self):
        return self.reviews.count()

    @property
    def accuracy(self):
        total = self.total_answered
        if not total:
            return 0
        correct = self.reviews.filter(grade__gte=1).count()
        return round(correct / total * 100, 1)

    @property
    def avg_seconds(self):
        agg = self.reviews.aggregate(avg=models.Avg("seconds"))
        return round(agg["avg"], 1) if agg["avg"] is not None else 0

    @property
    def chapters(self):
        return self.chapter_filter or "すべて"

    @property
    def categories(self):
        if not self.category_filter:
            return "すべて"
        return dict(Card.CATEGORY_CHOICES).get(self.category_filter, self.category_filter)

class ReviewLog(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="reviews")
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    grade = models.PositiveSmallIntegerField(help_text="0=Again, 1=Hard, 2=Good, 3=Easy")
    seconds = models.FloatField(default=0)
    reviewed_at = models.DateTimeField(auto_now_add=True)
