"""Explicit static capability catalog; descriptors never contain callables."""

from .contracts import CapabilityDependency, CapabilityDescriptor, CapabilityDiscoveryDescriptor
from .enums import (
    CapabilityDependencyKind,
    CapabilityDiscoveryState,
    CapabilityEntitlement,
    CapabilityReadinessState,
    CapabilityRegistrationState,
    CapabilitySemanticRole,
    CostKnowledge,
    EffectClass,
    FacadeAuthorityScope,
    InterfaceLevel,
    MonitoringCompatibility,
    PluggabilityLevel,
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
        capability_id="expression.assess",
        interface_level=InterfaceLevel.PUBLIC,
        request_schema_id="schema:tiaf.facade.expression-assess-request",
        result_schema_id="schema:tiaf.facade.expression-assess-result",
        effect=EffectClass.CAPTURED_READ,
        deterministic=True,
        model_supported=False,
        replay_support=ReplaySupport.DETERMINISTIC,
        required_authority_scope=FacadeAuthorityScope.ASSESS_EXPRESSION,
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


def _input_contract(contract_id: str) -> CapabilityDependency:
    return CapabilityDependency(
        dependency_id=contract_id,
        kind=CapabilityDependencyKind.INPUT_CONTRACT,
        version_specifier="==1.0",
    )


def _discovery(
    capability_id: str,
    *,
    semantic_role: CapabilitySemanticRole,
    required_dependencies: tuple[CapabilityDependency, ...] = (),
    required_entitlements: tuple[CapabilityEntitlement, ...] = (),
    monitoring_compatibility: MonitoringCompatibility,
    limitations: tuple[str, ...],
) -> CapabilityDiscoveryDescriptor:
    descriptor = next(item for item in _CATALOG if item.capability_id == capability_id)
    return CapabilityDiscoveryDescriptor(
        **descriptor.model_dump(),
        descriptor_id=f"descriptor:{capability_id}/{descriptor.capability_version}",
        semantic_role=semantic_role,
        pluggability_level=PluggabilityLevel.STRUCTURAL,
        replaceable=False,
        composable=False,
        required_dependencies=required_dependencies,
        required_authorities=(descriptor.required_authority_scope,),
        required_entitlements=required_entitlements,
        registration_state=CapabilityRegistrationState.REGISTERED,
        discovery_state=CapabilityDiscoveryState.REGISTERED,
        readiness_state=CapabilityReadinessState.REQUIRES_RUNTIME_CHECK,
        monitoring_compatibility=monitoring_compatibility,
        limitations=limitations,
    )


_CAPTURED_LIMITATIONS = (
    "limitation:captured-input-only",
    "limitation:discovery-does-not-grant-authority",
    "limitation:no-live-freshness",
)

_DISCOVERY_CATALOG = (
    _discovery(
        "a4.evaluate",
        semantic_role=CapabilitySemanticRole.CHALLENGE_ARBITRATION,
        required_dependencies=(
            _input_contract("contract:tiaf.source-semantics.foundation-capture"),
        ),
        required_entitlements=(CapabilityEntitlement.CAPTURED_EVIDENCE,),
        monitoring_compatibility=MonitoringCompatibility.SEMANTICALLY_REPEATABLE,
        limitations=_CAPTURED_LIMITATIONS,
    ),
    _discovery(
        "a4_input.project",
        semantic_role=CapabilitySemanticRole.CHALLENGE_ARBITRATION,
        required_dependencies=(
            _input_contract("contract:tiaf.source-semantics.projection-build-input"),
        ),
        required_entitlements=(CapabilityEntitlement.CAPTURED_EVIDENCE,),
        monitoring_compatibility=MonitoringCompatibility.SEMANTICALLY_REPEATABLE,
        limitations=_CAPTURED_LIMITATIONS,
    ),
    _discovery(
        "baseline.assess",
        semantic_role=CapabilitySemanticRole.BASELINE,
        required_dependencies=(
            _input_contract("contract:tiaf.baseline.deterministic-baseline-request"),
        ),
        monitoring_compatibility=MonitoringCompatibility.SEMANTICALLY_REPEATABLE,
        limitations=(
            "limitation:discovery-does-not-grant-authority",
            "limitation:no-live-freshness",
            "limitation:supplied-input-only",
        ),
    ),
    _discovery(
        "capabilities.list",
        semantic_role=CapabilitySemanticRole.CAPABILITY_DISCOVERY,
        monitoring_compatibility=MonitoringCompatibility.NOT_MONITORABLE,
        limitations=(
            "limitation:discovery-does-not-grant-authority",
            "limitation:no-runtime-health-assertion",
        ),
    ),
    _discovery(
        "expression.assess",
        semantic_role=CapabilitySemanticRole.TRADE_EXPRESSION_INTELLIGENCE,
        required_dependencies=(
            _input_contract("contract:tiaf.facade.expression-assess-input"),
        ),
        required_entitlements=(CapabilityEntitlement.CAPTURED_EVIDENCE,),
        monitoring_compatibility=MonitoringCompatibility.MONITORING_FUTURE,
        limitations=(
            "limitation:advisory-only",
            "limitation:captured-input-only",
            "limitation:discovery-does-not-grant-authority",
            "limitation:no-execution-authority",
            "limitation:no-live-freshness",
            "limitation:no-monitoring-runtime",
        ),
    ),
    _discovery(
        "opportunity.assemble",
        semantic_role=CapabilitySemanticRole.OPPORTUNITY_INTELLIGENCE,
        required_dependencies=(
            _input_contract("contract:tiaf.a3-hardening.orchestration-capture"),
        ),
        required_entitlements=(CapabilityEntitlement.CAPTURED_EVIDENCE,),
        monitoring_compatibility=MonitoringCompatibility.SEMANTICALLY_REPEATABLE,
        limitations=_CAPTURED_LIMITATIONS,
    ),
    _discovery(
        "position.assess",
        semantic_role=CapabilitySemanticRole.POSITION_INTELLIGENCE,
        required_dependencies=(
            _input_contract("contract:tiaf.a5.position-intelligence-request"),
        ),
        required_entitlements=(CapabilityEntitlement.POSITION_DATA,),
        monitoring_compatibility=MonitoringCompatibility.MONITORING_FUTURE,
        limitations=(
            "limitation:captured-input-only",
            "limitation:discovery-does-not-grant-authority",
            "limitation:no-live-freshness",
            "limitation:no-monitoring-runtime",
        ),
    ),
    _discovery(
        "replay.recorded",
        semantic_role=CapabilitySemanticRole.REPLAY,
        required_dependencies=(
            _input_contract("contract:tiaf.facade.trusted-replay-artifact"),
        ),
        required_entitlements=(CapabilityEntitlement.CAPTURED_EVIDENCE,),
        monitoring_compatibility=MonitoringCompatibility.NOT_MONITORABLE,
        limitations=(
            "limitation:discovery-does-not-grant-authority",
            "limitation:no-live-freshness",
            "limitation:recorded-input-only",
        ),
    ),
    _discovery(
        "replay.verify",
        semantic_role=CapabilitySemanticRole.ENGINEERING,
        required_dependencies=(
            _input_contract("contract:tiaf.facade.trusted-replay-artifact"),
        ),
        required_entitlements=(
            CapabilityEntitlement.CAPTURED_EVIDENCE,
            CapabilityEntitlement.ENGINEERING,
        ),
        monitoring_compatibility=MonitoringCompatibility.NOT_MONITORABLE,
        limitations=(
            "limitation:discovery-does-not-grant-authority",
            "limitation:engineering-only",
            "limitation:no-live-freshness",
            "limitation:recorded-input-only",
        ),
    ),
)


def capability_catalog() -> tuple[CapabilityDescriptor, ...]:
    """Return the immutable, explicitly authored catalog in stable ID order."""
    return _CATALOG


def capability_discovery_catalog() -> tuple[CapabilityDiscoveryDescriptor, ...]:
    """Return static registered metadata; caller discovery still requires admission."""
    return _DISCOVERY_CATALOG


def descriptor_for(capability_id: str) -> CapabilityDescriptor | None:
    return next((item for item in _CATALOG if item.capability_id == capability_id), None)
