"""Public FLC seams and backward-compatible native-envelope imports.

The family-neutral execution contract lives in inference_contracts. Original
InferenceRequest/Result names remain legacy codecs, not extension points.
"""

from .forecaster_legacy import (
    InferenceForecaster as InferenceForecaster,
)
from .forecaster_legacy import (
    InferenceRequest as InferenceRequest,
)
from .forecaster_legacy import (
    InferenceResult as InferenceResult,
)
from .forecaster_legacy import (
    describe_forecaster as describe_forecaster,
)
from .forecaster_legacy import (
    inference_descriptors as inference_descriptors,
)
from .inference_contracts import (
    CalibratableOutput as CalibratableOutput,
)
from .inference_contracts import (
    DiagnosableForecaster as DiagnosableForecaster,
)
from .inference_contracts import (
    DiagnosticReport as DiagnosticReport,
)
from .inference_contracts import (
    DiagnosticRequest as DiagnosticRequest,
)
from .inference_contracts import (
    FamilyIdentifier as FamilyIdentifier,
)
from .inference_contracts import (
    ForecasterArtifacts as ForecasterArtifacts,
)
from .inference_contracts import (
    ForecasterCapability as ForecasterCapability,
)
from .inference_contracts import (
    ForecasterFamily as ForecasterFamily,
)
from .inference_contracts import (
    ForecasterKey as ForecasterKey,
)
from .inference_contracts import (
    ForecasterLifecycle as ForecasterLifecycle,
)
from .inference_contracts import (
    ForecasterRole as ForecasterRole,
)
from .inference_contracts import (
    InferenceAdapter as InferenceAdapter,
)
from .inference_contracts import (
    InferenceDescriptor as InferenceDescriptor,
)
from .inference_contracts import (
    InferenceProvenance as InferenceProvenance,
)
from .inference_contracts import (
    LifecycleIdentity as LifecycleIdentity,
)
from .inference_contracts import (
    NeutralInferenceRequest as NeutralInferenceRequest,
)
from .inference_contracts import (
    NeutralInferenceResult as NeutralInferenceResult,
)
from .inference_contracts import (
    TrainableForecaster as TrainableForecaster,
)
from .inference_contracts import (
    TrainingRequest as TrainingRequest,
)
from .inference_contracts import (
    TrainingResult as TrainingResult,
)
from .inference_contracts import (
    run_inference as run_inference,
)
