from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.core.config import settings
from app.schemas.chart import ChartData, ChartQuestionResponse, ChartSessionResponse


@dataclass
class InMemoryChartSession:
    chart_id: str
    created_at: datetime
    expires_at: datetime
    chart_data: ChartData
    question_history: list[ChartQuestionResponse] = field(default_factory=list)

    def to_response(self) -> ChartSessionResponse:
        return ChartSessionResponse(
            chartId=self.chart_id,
            createdAt=self.created_at,
            expiresAt=self.expires_at,
            chartData=self.chart_data,
            questionHistory=self.question_history,
        )


class ChartSessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, InMemoryChartSession] = {}

    def _purge_expired(self) -> None:
        now = datetime.now(UTC)
        expired = [chart_id for chart_id, session in self._sessions.items() if session.expires_at <= now]
        for chart_id in expired:
            del self._sessions[chart_id]

    def create(self, chart_data: ChartData) -> ChartSessionResponse:
        self._purge_expired()
        now = datetime.now(UTC)
        session = InMemoryChartSession(
            chart_id=str(uuid4()),
            created_at=now,
            expires_at=now + timedelta(minutes=settings.session_ttl_minutes),
            chart_data=chart_data,
        )
        self._sessions[session.chart_id] = session
        return session.to_response()

    def get(self, chart_id: str) -> ChartSessionResponse | None:
        self._purge_expired()
        session = self._sessions.get(chart_id)
        if session is None:
            return None

        return session.to_response()

    def add_question_answer(self, chart_id: str, answer: ChartQuestionResponse) -> None:
        self._purge_expired()
        session = self._sessions.get(chart_id)
        if session is None:
            return

        session.question_history.append(answer)


chart_session_store = ChartSessionStore()

