# Project: Token Efficiency & AI Value-Attribution Startup Research

*This is the team's locked scope as of July 2026. The article feed
(`config/keywords.yml`) is tuned to this brief — update both together.*

## Thesis under validation

Enterprises track AI adoption by token volume, a metric everyone now agrees is
broken (see: Amazon/Meta "tokenmaxxing," FT May 2026). The replacement category
— measuring output per token and attributing AI spend to business outcomes per
employee, workflow, and agent — has no owner yet. We are validating whether a
product here is buildable and defensible by a small team.

## Scope (locked in) — Layers 3 and 4 only

1. **Token cost optimization / AI FinOps**, specifically the gaps: remediation
   (not just dashboards), and visibility into developer-tool and internal-agent
   traffic that server-side gateways can't see (Claude Code, Cursor, internal
   agent platforms).
2. **Enterprise oversight of employee token usage**, framed as efficiency and
   value attribution, not security surveillance. Privacy constraint is hard:
   usage patterns and spend signals, **never prompt content**.

**Explicitly out of scope:** public prompt marketplaces, generic prompt
sharing, generic semantic caching (absorbed by providers via native prompt
caching).

## Competitors to monitor (daily news watch)

| Bucket | Companies |
|---|---|
| Direct conceptual | Revenium (spend-to-outcome attribution, tokenmaxxing positioning), Mavvrik (AI financial control layer) |
| AI FinOps | Vantage, Finout, Amnic, PointFive, nOps, FinOps Foundation "Tokenomics" workstream |
| Gateways that could expand | Portkey, LiteLLM, Kong AI Gateway, OpenRouter |
| Observability that could expand | Langfuse, Helicone, Braintrust, LangSmith, Datadog LLM observability |
| Shadow-AI governance that could pivot | Larridin, Lasso, Nudge Security, CloudEagle, Knostic |
| Platform risk | OpenAI and Anthropic native caching / usage-analytics announcements |

## News triggers worth flagging

- Funding rounds or launches by any of the above
- Any enterprise announcing a shift from volume-based to outcome-based AI metrics
- New tokenmaxxing or AI-usage-monitoring reporting
- Gartner / FinOps Foundation publications on token efficiency
- Provider API changes to caching, usage reporting, or admin analytics

## Open validation questions

1. Who is the buyer: CFO (cost optimization is their #1 2026 priority) vs. VP Eng vs. platform teams?
2. How do you measure "output" per role in a defensible way?
3. Can developer-tool token traffic be instrumented without being spyware or requiring an agent install that security teams reject?
4. Does the adoption-theater incentive (execs wanting usage numbers up) block sales, or does the CFO counterweight win?

## Next deliverables

1. Deep-dive competitor map of the narrow wedge (Revenium, Mavvrik, adjacent movers): funding, team size, pricing, exact positioning.
2. Prototype scope assessment: what a two-person student team can build (likely a local proxy/plugin that logs per-task token usage from coding agents and computes an efficiency metric).
3. 5–10 customer-discovery interview targets (eng managers or FinOps leads at AI-heavy mid-size companies).
