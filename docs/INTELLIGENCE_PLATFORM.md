# Intelligence Platform

The intelligence platform is an additive foundation for Roster's future agent runtime. It separates durable memory, intent classification, goal planning, bounded context, local knowledge retrieval, citations, and safety gates.

## Design principles

- deterministic domain objects where possible
- explicit privacy and retention boundaries
- bounded retrieval and context budgets
- explainable decisions rather than opaque execution
- additive integration with the existing Agent and Runtime APIs
- focused regression tests for every new primitive

The platform does not replace the existing execution path; it provides stable seams for future integration.
