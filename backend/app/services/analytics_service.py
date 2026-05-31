from typing import Dict


class AnalyticsService:
    def compute_interest_score(self, metrics: Dict[str, int]) -> int:
        response_time_score = max(0, min(20, 20 - metrics.get("response_time_seconds", 10)))
        engagement_score = metrics.get("engagement_points", 0) * 4
        cooperation_score = metrics.get("cooperation_points", 0) * 4
        enthusiasm_score = metrics.get("enthusiasm_points", 0) * 5
        curiosity_score = metrics.get("curiosity_points", 0) * 4
        sentiment_score = max(0, metrics.get("sentiment_score", 0)) * 3
        availability_score = metrics.get("availability_score", 0) * 5
        intent_score = metrics.get("job_change_intent_score", 0) * 5
        risk_penalty = max(0, metrics.get("risk_score", 0)) * 4

        raw = (
            response_time_score
            + engagement_score
            + cooperation_score
            + enthusiasm_score
            + curiosity_score
            + sentiment_score
            + availability_score
            + intent_score
            - risk_penalty
        )
        score = int(max(0, min(100, raw)))
        return score

    def category(self, score: int) -> str:
        if score >= 80:
            return "Highly Interested"
        if score >= 60:
            return "Interested"
        if score >= 40:
            return "Neutral"
        if score >= 20:
            return "Low Interest"
        return "Not Interested"

    def recommendation(self, score: int) -> str:
        if score >= 80:
            return "Strongly Recommend"
        if score >= 60:
            return "Recommend"
        if score >= 40:
            return "Review Further"
        if score >= 20:
            return "Low Priority"
        return "Do Not Proceed"

    def build_report(self, candidate: dict, analysis: dict, score: int, category: str) -> dict[str, str]:
        recommendation = self.recommendation(score)
        summary = (
            f"The candidate demonstrated {analysis.get('sentiment', 'neutral')} sentiment, "
            f"{category.lower()} interest, and answered in a professional manner. "
            f"Key strengths include {analysis.get('interest_reasoning', 'core conversation indicators')}."
        )
        key_observations = analysis.get("interest_reasoning", "No specific observations generated.")
        risk_factors = "Minor concerns about response clarity." if analysis.get("clarity") != "clear" else "None identified."
        return {
            "summary": summary,
            "interest_category": category,
            "interest_score": score,
            "recommendation": recommendation,
            "key_observations": key_observations,
            "risk_factors": risk_factors,
        }
