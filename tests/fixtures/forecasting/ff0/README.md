# FF-0.1 synthetic foundation fixtures

`foundation_cases.json` is a test-case manifest, not a persisted forecast corpus.
`tests/unit/forecasting/_support.py` constructs the corresponding target, three
supplied sessions S20–S22, exact reference price, provenance references and
request/result specimens. All facts and clock histories are synthetic.

No actual issuer/exchange evidence, fitted BaseRate, outcome label, journal,
replay run or historical deployment is claimed. The 0.6 output is an authored
contract example, not calculated inference. Equal-close tests assert the target
policy; the Ground Truth resolver remains FF-0.2 work.
