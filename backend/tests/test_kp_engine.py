import unittest

from app.schemas.chart import ChartCalculationRequest
from app.services.kp_engine import build_chart, build_question_answer


def make_reference_chart():
    payload = ChartCalculationRequest(
        name="Aaradhya",
        dateOfBirth="2016-04-11",
        timeOfBirth="13:30",
        birthPlace="Secunderabad",
        state="Telangana",
        country="India",
        timezone="Asia/Kolkata",
        latitude=17.4337246,
        longitude=78.5006827,
        questionCategory="Education",
        question="How will her education develop and what stream may suit her later?",
    )
    return build_chart(payload)


class KPEngineQuestionQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = make_reference_chart()

    def ask(self, question: str):
        return build_question_answer(self.chart, question, None)

    def test_finance_question_classifies_correctly(self):
        answer = self.ask("Will she be financially strong later in life?")
        self.assertEqual(answer.classified_topic, "Finance")
        self.assertIn("age 22 to 30", answer.plain_explanation.lower())

    def test_career_answer_uses_life_stage_projection(self):
        answer = self.ask("How will her career develop and what kind of job will she likely do?")
        plain = answer.plain_explanation.lower()
        self.assertEqual(answer.classified_topic, "Career")
        self.assertIn("stream-selection years around age 14 to 17", plain)
        self.assertIn("job-entry promise should be judged more seriously around age 20 to 23", plain)
        self.assertTrue(any("Rule evaluation" == item.step for item in answer.calculation_trail))

    def test_health_answer_avoids_profession_wording(self):
        answer = self.ask("How is her eye health as per jathakam?")
        plain = answer.plain_explanation.lower()
        self.assertEqual(answer.classified_topic, "Health Caution")
        self.assertIn("monitoring, routine, resilience, and parental awareness", plain)
        self.assertNotIn("professional signature", plain)

    def test_foreign_settlement_answer_is_minor_aware(self):
        answer = self.ask("Is foreign settlement indicated for her later?")
        plain = answer.plain_explanation.lower()
        self.assertEqual(answer.classified_topic, "Foreign Settlement")
        self.assertIn("because the native is still a minor", plain)
        self.assertIn("age 21 to 29", plain)

    def test_property_answer_uses_property_specific_signature(self):
        answer = self.ask("Will she buy property later in life?")
        plain = answer.plain_explanation.lower()
        self.assertEqual(answer.classified_topic, "Property")
        self.assertIn("beautiful home, comfort, and lifestyle property", plain)
        self.assertIn("age 25 to 35", plain)


if __name__ == "__main__":
    unittest.main()
