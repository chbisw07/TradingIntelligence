"""Deterministic caller/operator/capability/profile/budget intersection."""

from datetime import datetime

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.planner.digests import digest

from .contracts import (
    CallerGrant,
    CapabilityDescriptor,
    EffectiveAdmission,
    InvocationBudget,
    OperatorPolicy,
)
from .enums import CapabilityAvailability, EffectClass, InterfaceLevel


def can_discover(
    descriptor: CapabilityDescriptor,
    caller: CallerGrant,
    operator: OperatorPolicy,
    *,
    profile_ref: str,
    authority_ref: str,
) -> bool:
    """Catalog visibility is permission-filtered but never itself a grant."""
    return all(
        (
            descriptor.availability is CapabilityAvailability.AVAILABLE,
            descriptor.capability_id in caller.allowed_capabilities,
            descriptor.capability_id in operator.allowed_capabilities,
            descriptor.required_authority_scope in caller.authority_scopes,
            descriptor.required_authority_scope in operator.authority_scopes,
            profile_ref in caller.allowed_profiles,
            profile_ref in operator.allowed_profiles,
            authority_ref in caller.authority_refs,
            authority_ref in operator.authority_refs,
            descriptor.interface_level is not InterfaceLevel.ENGINEERING
            or (caller.engineering_allowed and operator.engineering_enabled),
            descriptor.effect is not EffectClass.LIVE_READ
            or (caller.live_allowed and operator.live_enabled),
            not descriptor.model_supported
            or (caller.model_allowed and operator.model_enabled),
        )
    )


def admit(
    descriptor: CapabilityDescriptor,
    caller: CallerGrant,
    operator: OperatorPolicy,
    *,
    profile_ref: str,
    authority_ref: str,
    requested_budget: InvocationBudget,
    admitted_at: datetime | None = None,
) -> EffectiveAdmission:
    if not can_discover(
        descriptor,
        caller,
        operator,
        profile_ref=profile_ref,
        authority_ref=authority_ref,
    ):
        raise PermissionError("capability is not permitted by effective trusted policy")
    effective_entitlements = tuple(
        sorted(set(caller.entitlement_refs) & set(operator.entitlement_refs))
    )
    effective_budget = requested_budget.intersect(
        caller.budget_ceiling,
        operator.budget_ceiling,
    )
    when = admitted_at or datetime.now(TIAF_TIMEZONE)
    identity = digest(
        {
            "caller": caller.caller_id,
            "grant": caller.grant_id,
            "operator": (operator.policy_id, operator.policy_version),
            "capability": (descriptor.capability_id, descriptor.capability_version),
            "profile": profile_ref,
            "authority": authority_ref,
            "entitlements": effective_entitlements,
            "budget": effective_budget.model_dump(mode="json"),
        }
    )
    return EffectiveAdmission(
        admission_id=f"facade-admission:{identity[:24]}",
        caller_id=caller.caller_id,
        caller_grant_id=caller.grant_id,
        operator_policy_id=operator.policy_id,
        operator_policy_version=operator.policy_version,
        capability_id=descriptor.capability_id,
        capability_version=descriptor.capability_version,
        authority_scope=descriptor.required_authority_scope,
        effective_authority_ref=authority_ref,
        effective_entitlement_refs=effective_entitlements,
        profile_ref=profile_ref,
        effective_budget=effective_budget,
        model_policy_ref=operator.model_policy_ref,
        effect=descriptor.effect,
        admitted_at=when,
    )
