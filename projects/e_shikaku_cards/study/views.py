import random
from datetime import timedelta
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Avg, Count, Min, Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import CardForm
from .models import Card, Progress, ReviewLog, StudySession

EASY_SECONDS = 3
GOOD_SECONDS = 60
SESSION_SIZE = 10
CARD_LIST_PAGE_SIZE = 20


def _grade_from_speed(is_correct: bool, seconds: float) -> int:
    if not is_correct:
        return 0  # Again
    if seconds <= EASY_SECONDS:
        return 3  # Easy
    if seconds <= GOOD_SECONDS:
        return 2  # Good
    return 1  # Hard


def _build_choices(card: Card, count: int = 4) -> list[dict]:
    pool = list(Card.objects.filter(is_active=True, category=card.category).exclude(id=card.id))
    if len(pool) < count - 1:
        seen_ids = {c.id for c in pool}
        pool += list(Card.objects.filter(is_active=True).exclude(id=card.id).exclude(id__in=seen_ids))
    distractors = random.sample(pool, k=min(count - 1, len(pool)))
    choices = [{"text": card.back, "correct": True}] + [{"text": c.back, "correct": False} for c in distractors]
    random.shuffle(choices)
    return choices


def _ensure_progress() -> None:
    for card in Card.objects.filter(is_active=True):
        Progress.objects.get_or_create(card=card)


def _build_session_queue(size: int = SESSION_SIZE, chapter: str | None = None, category: str | None = None) -> list[int]:
    now = timezone.now()
    due_qs = Progress.objects.filter(card__is_active=True, due_at__lte=now)
    card_qs = Card.objects.filter(is_active=True)
    if chapter:
        due_qs = due_qs.filter(card__chapter=chapter)
        card_qs = card_qs.filter(chapter=chapter)
    if category:
        due_qs = due_qs.filter(card__category=category)
        card_qs = card_qs.filter(category=category)
    due_ids = list(due_qs.values_list("card_id", flat=True))
    random.shuffle(due_ids)
    queue = due_ids[:size]
    if len(queue) < size:
        other_ids = list(card_qs.exclude(id__in=queue).values_list("id", flat=True))
        random.shuffle(other_ids)
        queue += other_ids[:size - len(queue)]
    return queue


def dashboard(request: HttpRequest) -> HttpResponse:
    _ensure_progress()
    now = timezone.now()
    progress = Progress.objects.select_related("card")
    context = {
        "due_count": progress.filter(due_at__lte=now, card__is_active=True).count(),
        "total_cards": Card.objects.filter(is_active=True).count(),
        "mastered": progress.filter(repetitions__gte=3, accuracy__gte=80) if False else progress.filter(repetitions__gte=3),
        "recent_sessions": (
            StudySession.objects.annotate(total=Count("reviews"))
            .filter(total__gt=0)
            .order_by("-started_at")[:5]
        ),
        "chapters": (
            Card.objects.filter(is_active=True).exclude(chapter="")
            .values_list("chapter", flat=True).distinct().order_by("chapter")
        ),
        "categories": Card.CATEGORY_CHOICES,
    }
    context["mastered_count"] = context["mastered"].count()
    return render(request, "study/dashboard.html", context)


def study(request: HttpRequest) -> HttpResponse:
    _ensure_progress()
    if request.GET.get("new") == "1" or "study_queue" not in request.session:
        chapter = request.GET.get("chapter") or None
        category = request.GET.get("category") or None
        queue = _build_session_queue(chapter=chapter, category=category)
        request.session["study_queue"] = queue
        request.session["study_total"] = len(queue)
        request.session["study_session_id"] = StudySession.objects.create(
            chapter_filter=chapter or "", category_filter=category or ""
        ).id

    queue = request.session["study_queue"]
    total = request.session.get("study_total") or len(queue)

    if not queue:
        session_id = request.session.get("study_session_id")
        if session_id:
            StudySession.objects.filter(id=session_id, finished_at__isnull=True).update(finished_at=timezone.now())
        return render(request, "study/study.html", {
            "item": None,
            "session_done": True,
            "progress_total": total,
        })

    item = Progress.objects.select_related("card").filter(card_id=queue[0], card__is_active=True).first()
    if item is None:
        queue.pop(0)
        request.session["study_queue"] = queue
        request.session.modified = True
        return redirect("study:study")

    choices = _build_choices(item.card)
    context = {
        "item": item,
        "choices": choices,
        "easy_seconds": EASY_SECONDS,
        "good_seconds": GOOD_SECONDS,
        "progress_current": total - len(queue) + 1,
        "progress_total": total,
    }
    return render(request, "study/study.html", context)


@require_POST
def review(request: HttpRequest, card_id: int) -> HttpResponse:
    card = get_object_or_404(Card, id=card_id, is_active=True)
    progress, _ = Progress.objects.get_or_create(card=card)
    seconds = max(0.0, min(600.0, float(request.POST.get("seconds", 0) or 0)))
    is_correct = request.POST.get("correct") == "1"
    grade = _grade_from_speed(is_correct, seconds)

    progress.total_reviews += 1
    if grade >= 1:  # Hard/Good/Easy はすべて「正解」。Againのみ不正解。
        progress.correct_reviews += 1
    old_total = progress.total_reviews - 1
    progress.avg_seconds = ((progress.avg_seconds * old_total) + seconds) / progress.total_reviews
    progress.last_grade = grade

    now = timezone.now()
    if grade == 0:  # Again
        progress.repetitions = 0
        progress.interval_days = 0
        progress.lapses += 1
        progress.due_at = now + timedelta(minutes=10)
    elif grade == 1:  # Hard
        progress.interval_days = max(1, progress.interval_days or 1)
        progress.due_at = now + timedelta(days=progress.interval_days)
        progress.ease_factor = max(1.3, progress.ease_factor - 0.15)
    else:
        progress.repetitions += 1
        if progress.repetitions == 1:
            progress.interval_days = 1
        elif progress.repetitions == 2:
            progress.interval_days = 3
        else:
            factor = progress.ease_factor + (0.15 if grade == 3 else 0)
            progress.interval_days = max(4, round(progress.interval_days * factor))
        progress.due_at = now + timedelta(days=progress.interval_days)
        if grade == 3:
            progress.ease_factor += 0.15

    progress.save()
    ReviewLog.objects.create(
        card=card, grade=grade, seconds=seconds,
        session_id=request.session.get("study_session_id"),
    )

    queue = request.session.get("study_queue", [])
    if queue and queue[0] == card.id:
        queue.pop(0)
        request.session["study_queue"] = queue
        request.session.modified = True

    return redirect("study:study")


@require_POST
def reset_progress(request: HttpRequest) -> HttpResponse:
    ReviewLog.objects.all().delete()
    Progress.objects.all().delete()
    return redirect("study:dashboard")


def history_list(request: HttpRequest) -> HttpResponse:
    sessions = (
        StudySession.objects.annotate(total=Count("reviews"))
        .filter(total__gt=0)
        .order_by("-started_at")
    )
    return render(request, "study/history.html", {"sessions": sessions})


def stats_overview(request: HttpRequest) -> HttpResponse:
    _ensure_progress()
    chapter_totals = (
        Progress.objects.filter(card__is_active=True)
        .exclude(card__chapter="")
        .values("card__chapter")
        .annotate(total_reviews=Sum("total_reviews"), correct_reviews=Sum("correct_reviews"))
        .order_by("card__chapter")
    )
    avg_speed_by_chapter = {
        row["card__chapter"]: row["avg_speed"]
        for row in (
            ReviewLog.objects.filter(card__is_active=True)
            .exclude(card__chapter="")
            .values("card__chapter")
            .annotate(avg_speed=Avg("seconds"))
        )
    }
    rows = []
    for row in chapter_totals:
        total = row["total_reviews"] or 0
        correct = row["correct_reviews"] or 0
        rows.append({
            "chapter": row["card__chapter"],
            "total_reviews": total,
            "accuracy": round(correct / total * 100, 1) if total else 0,
            "avg_speed": avg_speed_by_chapter.get(row["card__chapter"]),
        })
    return render(request, "study/stats.html", {"rows": rows})


def stats_detail(request: HttpRequest, chapter: str) -> HttpResponse:
    _ensure_progress()
    cards = (
        Card.objects.filter(chapter=chapter, is_active=True)
        .select_related("progress")
        .annotate(fastest=Min("reviews__seconds"))
        .order_by("topic", "front")
    )
    rows = [{
        "card": card,
        "reviews": card.progress.total_reviews,
        "accuracy": card.progress.accuracy,
        "fastest": card.fastest,
        "avg_speed": card.progress.avg_seconds if card.progress.total_reviews else None,
    } for card in cards]
    return render(request, "study/stats_detail.html", {"chapter": chapter, "rows": rows})


def card_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    chapter = request.GET.get("chapter", "").strip()
    topic = request.GET.get("topic", "").strip()
    category = request.GET.get("category", "").strip()

    cards = Card.objects.all()
    if query:
        search_condition = (
            Q(front__icontains=query)
            | Q(back__icontains=query)
            | Q(trap__icontains=query)
            | Q(chapter__icontains=query)
            | Q(topic__icontains=query)
        )
        matching_categories = [
            value
            for value, label in Card.CATEGORY_CHOICES
            if query.casefold() in value.casefold() or query.casefold() in str(label).casefold()
        ]
        if matching_categories:
            search_condition |= Q(category__in=matching_categories)
        if query.isascii() and query.isdecimal() and len(query) <= 18:
            search_condition |= Q(id=int(query))
        cards = cards.filter(search_condition)
    if chapter:
        cards = cards.filter(chapter=chapter)
    if topic:
        cards = cards.filter(topic=topic)
    if category:
        cards = cards.filter(category=category)

    cards = cards.order_by("-created_at", "-id")
    paginator = Paginator(cards, CARD_LIST_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    filter_values = {
        "q": query,
        "chapter": chapter,
        "topic": topic,
        "category": category,
    }
    filter_query = urlencode({key: value for key, value in filter_values.items() if value})

    context = {
        "cards": page_obj,
        "page_obj": page_obj,
        "chapters": (
            Card.objects.exclude(chapter="")
            .values_list("chapter", flat=True)
            .distinct()
            .order_by("chapter")
        ),
        "topics": (
            Card.objects.exclude(topic="")
            .values_list("topic", flat=True)
            .distinct()
            .order_by("topic")
        ),
        "categories": Card.CATEGORY_CHOICES,
        "query": query,
        "selected_chapter": chapter,
        "selected_topic": topic,
        "selected_category": category,
        "filter_query": filter_query,
    }
    return render(request, "study/card_list.html", context)


def card_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save()
            Progress.objects.get_or_create(card=card)
            return redirect("study:card_list")
    else:
        form = CardForm()
    return render(request, "study/card_form.html", {"form": form, "is_new": True})


def card_update(request: HttpRequest, card_id: int) -> HttpResponse:
    card = get_object_or_404(Card, id=card_id)
    if request.method == "POST":
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            return redirect("study:card_list")
    else:
        form = CardForm(instance=card)
    return render(request, "study/card_form.html", {"form": form, "is_new": False, "card": card})


@require_POST
def card_delete(request: HttpRequest, card_id: int) -> HttpResponse:
    get_object_or_404(Card, id=card_id).delete()
    return redirect("study:card_list")
