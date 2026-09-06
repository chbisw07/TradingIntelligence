"""Public AnalysisContext API tests."""

import tiaf.context as context


def test_context_public_inventory() -> None:
    expected = {
        "AnalysisContext",
        "AnalysisContextBatchItem",
        "AnalysisContextBuildError",
        "AnalysisContextBuilder",
        "AnalysisContextDeferredError",
        "AnalysisContextRequirement",
        "AnalysisContextResolutionError",
        "AnalysisPurpose",
        "AnalysisSubject",
        "BatchItemStatus",
        "ContextSummary",
        "EvidenceDescriptor",
        "EvidenceRequirement",
        "EvidenceStatus",
        "HistoricalOptionRequirement",
        "RequiredEvidenceUnavailableError",
        "summarize_context",
    }
    assert expected <= set(context.__all__)
    assert all(getattr(context, name) is not None for name in expected)
