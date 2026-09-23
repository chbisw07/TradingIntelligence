"""One compiled synthetic calibration recipe. No input file/array/CLI loader."""

import resource

from .sigmoid_contracts import SigmoidParameters, synthetic_sample
from .sigmoid_math import _estimate


def main() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2, 512 * 1024**2))
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    intercept, slope = _estimate(synthetic_sample())
    print(SigmoidParameters(intercept=intercept, slope=slope).model_dump_json())


if __name__ == "__main__":
    main()
