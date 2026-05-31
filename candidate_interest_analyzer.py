import time
import textwrap
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


@dataclass
class CandidateInfo:
    name: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    current_role: Optional[str] = None
    expected_salary: Optional[str] = None
    notice_period: Optional[str] = None
    preferred_location: Optional[str] = None
    availability: Optional[str] = None
    additional_answers: Dict[str, str] = field(default_factory=dict)


@dataclass
class BehavioralMetrics:
    response_times: List[float] = field(default_factory=list)
    engagement_points: int = 0
    cooperation_points: int = 0
    enthusiasm_points: int = 0
    curiosity_points: int = 0
    questions_asked_by_candidate: int = 0
    sentiment_score: int = 0

    def average_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)


class CandidateInterestAnalyzer:
    def __init__(self, recruiter_requirements: Optional[List[str]] = None):
        self.recruiter_requirements = recruiter_requirements or []
        self.info = CandidateInfo()
        self.metrics = BehavioralMetrics()
        self.voice_engine = None
        if pyttsx3 is not None:
            try:
                self.voice_engine = pyttsx3.init()
            except Exception:
                self.voice_engine = None

        self.questions = [
            ("name", "Can you please start by telling me your full name?"),
            ("current_role", "What is your current role and employer?"),
            ("education", "Could you describe your educational background?"),
            ("skills", "What are the key skills and technologies you bring to this role?"),
            ("experience", "Can you summarize your relevant work experience for this position?"),
            ("expected_salary", "What salary range are you expecting for this opportunity?"),
            ("notice_period", "What is your notice period or earliest possible start date?"),
            ("preferred_location", "Do you have a preferred location or are you open to remote work?"),
            ("availability", "When are you available for the next interview?"),
        ]
        self.follow_ups = {
            "skills": "Could you share an example of how you applied those skills in a recent role?",
            "experience": "Can you tell me about a project that best represents your experience?",
            "availability": "Would mornings or afternoons work better for you for an interview?",
        }

    def speak(self, text: str) -> None:
        print(text)
        if self.voice_engine is not None:
            self.voice_engine.say(text)
            self.voice_engine.runAndWait()

    def ask_question(self, prompt: str) -> str:
        self.speak(prompt)
        start = time.perf_counter()
        answer = input("Candidate: ").strip()
        elapsed = time.perf_counter() - start
        self.metrics.response_times.append(elapsed)
        self._score_response(answer, elapsed)
        return answer

    def _score_response(self, answer: str, response_time: float) -> None:
        lower = answer.lower()
        if len(answer) > 80:
            self.metrics.engagement_points += 2
        elif len(answer) > 30:
            self.metrics.engagement_points += 1

        if response_time < 10:
            self.metrics.cooperation_points += 2
        elif response_time < 20:
            self.metrics.cooperation_points += 1

        if any(word in lower for word in ["excited", "thrilled", "eager", "interested", "strong fit"]):
            self.metrics.enthusiasm_points += 2
        elif any(word in lower for word in ["open", "interested", "happy", "good fit"]):
            self.metrics.enthusiasm_points += 1

        if any(word in lower for word in ["question", "learn more", "understand", "how does", "what is"]):
            self.metrics.curiosity_points += 2

        if any(word in lower for word in ["not sure", "maybe", "depends", "i don't know", "later"]):
            self.metrics.sentiment_score -= 1
        if any(word in lower for word in ["excited", "eager", "happy", "great", "positive"]):
            self.metrics.sentiment_score += 1

    def run_conversation(self) -> None:
        self.speak(textwrap.dedent(
            """
            Welcome. I’m here to help guide the conversation and collect the information your recruiter needs.
            Please answer each question naturally. I will follow up if I need a bit more detail.
            """
        ))

        for field_name, question in self.questions:
            answer = self.ask_question(question)
            self._set_info_field(field_name, answer)

            if field_name in self.follow_ups:
                if not answer:
                    follow_up = self.follow_ups[field_name]
                    answer = self.ask_question(follow_up)
                    self._set_info_field(field_name, answer)
                else:
                    follow_up = self.follow_ups[field_name]
                    follow_up_answer = self.ask_question(follow_up)
                    self.metrics.cooperation_points += 1
                    self.metrics.questions_asked_by_candidate += self._count_questions_in_answer(follow_up_answer)

        self._ask_additional_recruiter_questions()
        self._ask_candidate_questions()
        self.print_report()

    def _set_info_field(self, field_name: str, answer: str) -> None:
        if not answer:
            return
        if hasattr(self.info, field_name):
            setattr(self.info, field_name, answer)
        else:
            self.info.additional_answers[field_name] = answer

    def _ask_additional_recruiter_questions(self) -> None:
        for requirement in self.recruiter_requirements:
            question = f"I have one more question from the recruiter: {requirement}. Could you share your response?"
            answer = self.ask_question(question)
            self.info.additional_answers[requirement] = answer

    def _ask_candidate_questions(self) -> None:
        question = "Do you have any questions about the role, the company, or the next steps?"
        answer = self.ask_question(question)
        self.metrics.questions_asked_by_candidate += self._count_questions_in_answer(answer)
        if answer:
            self.metrics.curiosity_points += 2
            self.metrics.engagement_points += 1

    @staticmethod
    def _count_questions_in_answer(answer: str) -> int:
        return answer.count("?")

    def _normalize_score(self, raw_score: float, max_score: float) -> float:
        if max_score <= 0:
            return 0.0
        return max(0.0, min(100.0, (raw_score / max_score) * 100))

    def compute_interest_score(self) -> int:
        average_response_time = self.metrics.average_response_time()
        response_time_score = max(0, 20 - average_response_time)
        raw = (
            response_time_score
            + self.metrics.engagement_points * 4
            + self.metrics.cooperation_points * 4
            + self.metrics.enthusiasm_points * 5
            + self.metrics.curiosity_points * 4
            + max(0, self.metrics.sentiment_score) * 3
        )
        return int(self._normalize_score(raw, 200))

    def interest_category(self, score: int) -> str:
        if score >= 80:
            return "Highly Interested"
        if score >= 60:
            return "Interested"
        if score >= 40:
            return "Neutral"
        if score >= 20:
            return "Low Interest"
        return "Not Interested"

    def sentiment_label(self) -> str:
        if self.metrics.sentiment_score >= 3:
            return "Highly Positive"
        if self.metrics.sentiment_score >= 1:
            return "Positive"
        if self.metrics.sentiment_score == 0:
            return "Neutral"
        return "Negative"

    def print_report(self) -> None:
        score = self.compute_interest_score()
        category = self.interest_category(score)
        sentiment = self.sentiment_label()
        avg_response = self.metrics.average_response_time()

        print("\n--- Final Analysis Report ---")
        self.speak("Candidate Interest Analyzer final report is being presented.")
        print("Candidate Information:")
        print(f"- Name: {self.info.name or 'Not provided'}")
        print(f"- Education: {self.info.education or 'Not provided'}")
        print(f"- Skills: {self.info.skills or 'Not provided'}")
        print(f"- Experience: {self.info.experience or 'Not provided'}")
        print(f"- Expected Salary: {self.info.expected_salary or 'Not provided'}")
        print(f"- Notice Period: {self.info.notice_period or 'Not provided'}")
        print(f"- Interview Availability: {self.info.availability or 'Not provided'}")

        print("\nBehavioral Analysis:")
        print(f"- Average Response Time: {avg_response:.1f} seconds")
        print(f"- Engagement Level: {self._level_label(self.metrics.engagement_points, [0, 3, 6, 9])}")
        print(f"- Cooperation Level: {self._level_label(self.metrics.cooperation_points, [0, 3, 6, 9])}")
        print(f"- Enthusiasm Level: {self._level_label(self.metrics.enthusiasm_points, [0, 2, 4, 6])}")
        print(f"- Questions Asked: {self.metrics.questions_asked_by_candidate}")
        print(f"- Sentiment: {sentiment}")

        print("\nInterest Assessment:")
        print(f"- Interest Score: {score}/100")
        print(f"- Interest Category: {category}")

        print("\nReasoning:")
        print("- Key indicators observed during the conversation:")
        print(f"  - Average response speed was {avg_response:.1f} seconds.")
        print(f"  - Engagement points: {self.metrics.engagement_points}.")
        print(f"  - Enthusiasm points: {self.metrics.enthusiasm_points}.")
        print(f"  - Curiosity points: {self.metrics.curiosity_points}.")
        print(f"- Evidence: candidate answered follow-up questions and asked {self.metrics.questions_asked_by_candidate} questions.")

        print("\nRecruiter Recommendation:")
        recommendation = self._recommendation_label(score)
        print(f"- {recommendation}")

        print("\nSummary:")
        print(self._summary_text(score, category, sentiment))

    @staticmethod
    def _level_label(points: int, thresholds: List[int]) -> str:
        if points <= thresholds[0]:
            return "Low"
        if points <= thresholds[1]:
            return "Moderate"
        if points <= thresholds[2]:
            return "Good"
        return "Strong"

    @staticmethod
    def _recommendation_label(score: int) -> str:
        if score >= 80:
            return "Strongly Recommend"
        if score >= 60:
            return "Recommend"
        if score >= 40:
            return "Review Further"
        if score >= 20:
            return "Low Priority"
        return "Do Not Proceed"

    def _summary_text(self, score: int, category: str, sentiment: str) -> str:
        return (
            f"The candidate showed {sentiment.lower()} sentiment and a {category.lower()} level of interest. "
            f"Responses were provided with an average delay of {self.metrics.average_response_time():.1f} seconds, "
            f"and the overall interaction suggests {'strong readiness for next steps' if score >= 60 else 'more evaluation is needed before moving forward'}."
        )


if __name__ == "__main__":
    print("Candidate Interest Analyzer Agent")
    print("You can press Enter to skip any question if the candidate does not answer.")
    extra = []
    use_extra = input("Would you like to add recruiter-specific questions? (yes/no): ").strip().lower()
    if use_extra == "yes":
        while True:
            req = input("Enter a recruiter requirement or leave blank to continue: ").strip()
            if not req:
                break
            extra.append(req)

    analyzer = CandidateInterestAnalyzer(recruiter_requirements=extra)
    analyzer.run_conversation()
