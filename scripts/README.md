# Scripts

`dhan_option_chain_smoke.py` is an optional read-only A1.3 inspection utility.
Without `--expiry` it lists active expiries and stops; chain retrieval always
requires an explicit expiry. It uses Dhan credentials from the environment and
never prints them.

`dhan_expired_options_smoke.py` is the optional read-only A1.4 rolling-history
inspection utility. It requires an explicit underlying, option class, expiry
context, relative strike, interval, and half-open date range.

Development and operational scripts will be added when a concrete milestone
requires them. The bootstrap baseline intentionally has no runtime scripts.
