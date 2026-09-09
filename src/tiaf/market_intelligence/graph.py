"""Small immutable evidence graph for replayable company relationships."""

from typing import Annotated, Self

from pydantic import Field, model_validator

from tiaf.contracts import ContractModel, DataQuality
from tiaf.contracts.common import NonEmptyStr, TiafDateTime

from .enums import DerivationClass, GraphEdgeStatus, GraphNodeKind, GraphRelation

UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class EvidenceGraphNode(ContractModel):
    node_id: NonEmptyStr
    kind: GraphNodeKind
    canonical_name: NonEmptyStr
    aliases: tuple[NonEmptyStr, ...] = ()


class EvidenceGraphProvenance(ContractModel):
    provider_id: NonEmptyStr
    evidence_ids: tuple[NonEmptyStr, ...]
    normalization_record_ids: tuple[NonEmptyStr, ...] = ()
    source_references: tuple[NonEmptyStr, ...] = ()
    observed_at: TiafDateTime | None = None
    available_from: TiafDateTime
    acquired_at: TiafDateTime
    last_verified_at: TiafDateTime
    derivation_class: DerivationClass

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        if not self.evidence_ids:
            raise ValueError("graph provenance requires evidence")
        if self.acquired_at < self.available_from:
            raise ValueError("graph acquisition cannot predate availability")
        if self.last_verified_at < self.acquired_at:
            raise ValueError("last verification cannot predate acquisition")
        return self


class EvidenceGraphEdge(ContractModel):
    edge_id: NonEmptyStr
    source_node_id: NonEmptyStr
    target_node_id: NonEmptyStr
    relation: GraphRelation
    status: GraphEdgeStatus
    materiality: UnitFloat
    evidence_quality: DataQuality
    confidence_basis: NonEmptyStr
    provenance: EvidenceGraphProvenance
    valid_from: TiafDateTime | None = None
    valid_to: TiafDateTime | None = None
    contradiction_group_id: NonEmptyStr | None = None
    contradiction_unresolved: bool = False
    edge_version: int = Field(default=1, gt=0)
    supersedes_edge_id: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_edge(self) -> Self:
        if self.source_node_id == self.target_node_id:
            raise ValueError("graph edge cannot be self-referential")
        if self.supersedes_edge_id == self.edge_id:
            raise ValueError("graph edge cannot supersede itself")
        if self.contradiction_unresolved and self.contradiction_group_id is None:
            raise ValueError("unresolved graph contradiction requires a group ID")
        if self.valid_from is not None and self.valid_to is not None:
            if self.valid_to < self.valid_from:
                raise ValueError("graph validity interval must increase")
        if self.status is GraphEdgeStatus.INFERRED:
            if self.provenance.derivation_class is DerivationClass.REPORTED:
                raise ValueError("inferred edge cannot claim reported derivation")
        return self


class SparseEvidenceGraph(ContractModel):
    graph_id: NonEmptyStr
    nodes: tuple[EvidenceGraphNode, ...] = ()
    edges: tuple[EvidenceGraphEdge, ...] = ()

    @model_validator(mode="after")
    def validate_graph(self) -> Self:
        node_ids = tuple(item.node_id for item in self.nodes)
        edge_ids = tuple(item.edge_id for item in self.edges)
        if len(node_ids) != len(set(node_ids)) or len(edge_ids) != len(set(edge_ids)):
            raise ValueError("graph node and edge IDs must be unique")
        node_set = set(node_ids)
        for edge in self.edges:
            if edge.source_node_id not in node_set or edge.target_node_id not in node_set:
                raise ValueError("graph edge endpoints must exist")
        return self

    def with_updates(
        self,
        *,
        nodes: tuple[EvidenceGraphNode, ...] = (),
        edges: tuple[EvidenceGraphEdge, ...] = (),
    ) -> "SparseEvidenceGraph":
        return SparseEvidenceGraph(
            graph_id=self.graph_id,
            nodes=(*self.nodes, *nodes),
            edges=(*self.edges, *edges),
        )

    def neighborhood(self, node_id: str, *, as_of: TiafDateTime) -> tuple[EvidenceGraphEdge, ...]:
        if node_id not in {item.node_id for item in self.nodes}:
            raise LookupError(f"unknown graph node: {node_id}")
        return tuple(
            edge
            for edge in self.edges
            if node_id in {edge.source_node_id, edge.target_node_id}
            and edge.provenance.available_from <= as_of
            and (edge.valid_from is None or edge.valid_from <= as_of)
            and (edge.valid_to is None or as_of <= edge.valid_to)
        )
