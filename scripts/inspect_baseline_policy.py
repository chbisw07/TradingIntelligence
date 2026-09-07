"""Print the complete deterministic A2.9 policy for human review."""

import argparse

from tiaf.baseline import default_policy, summarize_policy
from tiaf.contracts import TradeStyle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--horizon",
        choices=tuple(item.value for item in TradeStyle),
        required=True,
        help="Select the DAY or POSITIONAL version 1.0 engineering policy.",
    )
    args = parser.parse_args()
    args.horizon = TradeStyle(args.horizon)
    return args


def main() -> int:
    """Render a policy without provider access or mutable state."""
    print(summarize_policy(default_policy(parse_args().horizon)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
