"""Provider-neutral orchestration for deterministic baseline policies."""

from tiaf.contracts import TradeStyle

from .errors import BaselinePolicyError
from .models import BaselinePolicy, DeterministicBaselineRequest, OpportunityAssessment
from .policy import default_policy
from .scoring import score_request


class BaselineEngine:
    """Resolve an explicit policy and score already-produced evidence only."""

    def __init__(self, policies: tuple[BaselinePolicy, ...] = ()) -> None:
        selected = policies or (
            default_policy(TradeStyle.DAY),
            default_policy(TradeStyle.POSITIONAL),
        )
        keys = tuple((item.trade_style, item.policy_version) for item in selected)
        if len(keys) != len(set(keys)):
            raise BaselinePolicyError("baseline policies must have unique style/version keys")
        self._policies = {key: policy for key, policy in zip(keys, selected, strict=True)}

    def policies(self) -> tuple[BaselinePolicy, ...]:
        """Return a stable policy snapshot."""
        return tuple(self._policies[key] for key in sorted(self._policies))

    def assess(
        self,
        request: DeterministicBaselineRequest,
        *,
        policy: BaselinePolicy | None = None,
    ) -> OpportunityAssessment:
        """Produce one deterministic assessment without fetching any evidence."""
        selected = policy or self._resolve(request)
        return score_request(request, selected)

    def _resolve(self, request: DeterministicBaselineRequest) -> BaselinePolicy:
        try:
            return self._policies[(request.trade_style, request.policy_version)]
        except KeyError as exc:
            raise BaselinePolicyError(
                f"no policy for {request.trade_style.value} version {request.policy_version}"
            ) from exc
