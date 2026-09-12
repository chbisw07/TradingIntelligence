"""Explicit static capability catalog; descriptors never contain callables."""

from .contracts import CapabilityDescriptor
from .enums import (
    CostKnowledge,
    EffectClass,
    FacadeAuthorityScope,
    InterfaceLevel,
    ReplaySupport,
)

_CATALOG = (
    CapabilityDescriptor(
        capability_id="a4.evaluate",
        interface_level=InterfaceLevel.PUBLIC,
        request_schema_id="schema:tiaf.facade.a4-evaluate-request",
        result_schema_id="schema:tiaf.facade.a4-evaluate-result",
        effect=EffectClass.CAPTURED_READ,
        deterministic=True,
        model_supported=False,
        replay_support=ReplaySupport.DETERMINISTIC,
        required_authority_scope=FacadeAuthorityScope.EVALUATE_A4,
        cost_knowledge=CostKnowledge.KNOWN_ZERO,
    ),
    CapabilityDescriptor(
        capability_id="a4_input.project",
        interface_level=InterfaceLevel.PUBLIC,
        request_schema_id="schema:tiaf.facade.a4-input-project-request",
        result_schema_id="schema:tiaf.facade.a4-input-project-result",
        effect=EffectClass.CAPTURED_READ,
        deterministic=True,
        model_supported=False,
        replay_support=ReplaySupport.DETERMINISTIC,
        required_authority_scope=FacadeAuthorityScope.PROJECT_A4_INPUT,
        cost_knowledge=CostKnowledge.KNOWN_ZERO,
    ),
    CapabilityDescriptor(
        capability_id="baseline.assess",
        interface_level=InterfaceLevel.PUBLIC,
        request_schema_id="schema:tiaf.facade.baseline-assess-request",
        result_schema_id="schema:tiaf.facade.baseline-assess-result",
        effect=EffectClass.PURE,
        deterministic=True,
        model_supported=False,
        replay_support=ReplaySupport.DETERMINISTIC,
        required_authority_scope=FacadeAuthorityScope.ASSESS_BASELINE,
        cost_knowledge=CostKnowledge.KNOWN_ZERO,
    ),
    CapabilityDescriptor(
        capability_id="capabilities.list",
        interface_level=InterfaceLevel.PUBLIC,
        request_schema_id="schema:tiaf.facade.capability-list-request",
        result_schema_id="schema:tiaf.facade.capability-list-result",
        effect=EffectClass.PURE,
        deterministic=True,
        model_supported=False,
        replay_support=ReplaySupport.NONE,
        required_authority_scope=FacadeAuthorityScope.DISCOVER_CAPABILITIES,
        cost_knowledge=CostKnowledge.KNOWN_ZERO,
    ),
    CapabilityDescriptor(
        capability_id="opportunity.assemble",
        interface_level=InterfaceLevel.PUBLIC,
        request_schema_id="schema:tiaf.facade.opportunity-assemble-request",
        result_schema_id="schema:tiaf.facade.opportunity-assemble-result",
        effect=EffectClass.CAPTURED_READ,
        deterministic=True,
        model_supported=False,
        replay_support=ReplaySupport.DETERMINISTIC,
        required_authority_scope=FacadeAuthorityScope.ASSEMBLE_OPPORTUNITY,
        cost_knowledge=CostKnowledge.KNOWN_ZERO,
    ),
    CapabilityDescriptor(
        capability_id="position.assess",
        interface_level=InterfaceLevel.PUBLIC,
        request_schema_id="schema:tiaf.facade.position-assess-request",
        result_schema_id="schema:tiaf.facade.position-assess-result",
        effect=EffectClass.CAPTURED_READ,
        deterministic=True,
        model_supported=False,
        replay_support=ReplaySupport.DETERMINISTIC,
        required_authority_scope=FacadeAuthorityScope.ASSESS_POSITION,
        cost_knowledge=CostKnowledge.KNOWN_ZERO,
    ),
    CapabilityDescriptor(
        capability_id="replay.recorded",
        interface_level=InterfaceLevel.PUBLIC,
        request_schema_id="schema:tiaf.facade.recorded-replay-request",
        result_schema_id="schema:tiaf.facade.recorded-replay-result",
        effect=EffectClass.CAPTURED_READ,
        deterministic=True,
        model_supported=False,
        replay_support=ReplaySupport.RECORDED,
        required_authority_scope=FacadeAuthorityScope.READ_REPLAY,
        cost_knowledge=CostKnowledge.KNOWN_ZERO,
    ),
    CapabilityDescriptor(
        capability_id="replay.verify",
        interface_level=InterfaceLevel.ENGINEERING,
        request_schema_id="schema:tiaf.facade.replay-verify-request",
        result_schema_id="schema:tiaf.facade.replay-verify-result",
        effect=EffectClass.CAPTURED_READ,
        deterministic=True,
        model_supported=False,
        replay_support=ReplaySupport.DETERMINISTIC,
        required_authority_scope=FacadeAuthorityScope.VERIFY_REPLAY,
        cost_knowledge=CostKnowledge.KNOWN_ZERO,
    ),
)


def capability_catalog() -> tuple[CapabilityDescriptor, ...]:
    """Return the immutable, explicitly authored catalog in stable ID order."""
    return _CATALOG


def descriptor_for(capability_id: str) -> CapabilityDescriptor | None:
    return next((item for item in _CATALOG if item.capability_id == capability_id), None)
