# Scripts

`dhan_option_chain_smoke.py` is an optional read-only A1.3 inspection utility.
Without `--expiry` it lists active expiries and stops; chain retrieval always
requires an explicit expiry. It uses Dhan credentials from the environment and
never prints them.

Development and operational scripts will be added when a concrete milestone
requires them. The bootstrap baseline intentionally has no runtime scripts.
