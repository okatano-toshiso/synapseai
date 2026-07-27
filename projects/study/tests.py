from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse

from .models import Card


class CardListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("study:card_list")

    def create_card(self, index=0, **overrides):
        values = {
            "front": f"問題 {index}",
            "back": f"答え {index}",
            "trap": f"解説 {index}",
            "chapter": "章A",
            "topic": "論点A",
            "category": "formula",
        }
        values.update(overrides)
        return Card.objects.create(**values)

    def test_paginates_twenty_cards_and_displays_ids(self):
        cards = [self.create_card(index) for index in range(21)]

        response = self.client.get(self.url)
        page = response.context["page_obj"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(page.paginator.per_page, 20)
        self.assertEqual(page.paginator.count, 21)
        self.assertEqual(page.paginator.num_pages, 2)
        self.assertEqual(len(page.object_list), 20)
        self.assertContains(response, "<th>ID</th>", html=True)
        self.assertContains(response, f"#{cards[-1].id}")

        second_page = self.client.get(self.url, {"page": 2}).context["page_obj"]
        self.assertEqual(second_page.number, 2)
        self.assertEqual(len(second_page.object_list), 1)
        self.assertEqual(self.client.get(self.url, {"page": "invalid"}).context["page_obj"].number, 1)
        self.assertEqual(self.client.get(self.url, {"page": 999}).context["page_obj"].number, 2)

    def test_free_word_searches_text_fields_category_label_and_id(self):
        targets = {
            "frontneedle": self.create_card(1, front="FrontNeedle"),
            "backneedle": self.create_card(2, back="BackNeedle"),
            "trapneedle": self.create_card(3, trap="TrapNeedle"),
            "chapterneedle": self.create_card(4, chapter="ChapterNeedle"),
            "topicneedle": self.create_card(5, topic="TopicNeedle"),
        }

        for query, target in targets.items():
            with self.subTest(query=query):
                page = self.client.get(self.url, {"q": query}).context["page_obj"]
                self.assertEqual(list(page.object_list), [target])

        id_target = self.create_card(
            6,
            front="identifier",
            back="identifier answer",
            trap="identifier explanation",
            chapter="Identifier Chapter",
            topic="Identifier Topic",
        )
        id_page = self.client.get(self.url, {"q": str(id_target.id)}).context["page_obj"]
        self.assertEqual(list(id_page.object_list), [id_target])

        category_target = self.create_card(7, category="pytorch")
        category_page = self.client.get(self.url, {"q": "PyTorch対応"}).context["page_obj"]
        self.assertEqual(list(category_page.object_list), [category_target])

    def test_combines_chapter_topic_and_category_filters(self):
        target = self.create_card(1, front="needle target")
        self.create_card(2, front="needle other chapter", chapter="章B")
        self.create_card(3, front="needle other topic", topic="論点B")
        self.create_card(4, front="needle other category", category="instant")
        self.create_card(5, front="unrelated")
        self.create_card(6, chapter="", topic="")

        response = self.client.get(
            self.url,
            {"q": "needle", "chapter": "章A", "topic": "論点A", "category": "formula"},
        )

        self.assertEqual(list(response.context["page_obj"].object_list), [target])
        self.assertEqual(list(response.context["chapters"]), ["章A", "章B"])
        self.assertEqual(list(response.context["topics"]), ["論点A", "論点B"])
        self.assertContains(response, 'value="needle"')
        self.assertContains(response, '<option value="章A" selected>章A</option>', html=True)
        self.assertContains(response, '<option value="論点A" selected>論点A</option>', html=True)
        self.assertContains(response, '<option value="formula" selected>数式</option>', html=True)

    def test_filtered_pagination_preserves_conditions(self):
        for index in range(21):
            self.create_card(index, front=f"needle {index}")
        self.create_card(99, front="excluded", chapter="章B")
        params = {
            "q": "needle",
            "chapter": "章A",
            "topic": "論点A",
            "category": "formula",
            "page": 2,
        }

        response = self.client.get(self.url, params)
        page = response.context["page_obj"]
        expected_query = urlencode({key: value for key, value in params.items() if key != "page"})

        self.assertEqual(page.paginator.count, 21)
        self.assertEqual(page.number, 2)
        self.assertEqual(len(page.object_list), 1)
        self.assertEqual(response.context["filter_query"], expected_query)
        self.assertContains(response, "q=needle&amp;chapter=")
        self.assertContains(response, "category=formula&amp;page=1")

    def test_empty_search_result_is_explained(self):
        self.create_card()

        response = self.client.get(self.url, {"q": "一致しない語"})

        self.assertEqual(response.context["page_obj"].paginator.count, 0)
        self.assertContains(response, "条件に一致するカードがありません。")
