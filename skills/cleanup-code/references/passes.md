# KISS / YAGNI / DRY Pass Details

## KISS Pass

Simplify code that makes readers jump through unnecessary indirection:

- One-use helpers that hide a direct call.
- Mapper functions representable as data on the relevant type.
- Overly defensive branching around impossible states.
- Tests that assert implementation details without protecting behavior.
- Stale comments that describe removed behavior (also a YAGNI signal).

Prefer the simplest form that preserves:

- Clear error semantics.
- Testability.
- Existing public API.
- Local architectural rules.

**Apply KISS relative to the idioms of the language and framework in use.** Do not flag idiomatic patterns as complexity - Go error returns, Rust trait bounds, Java interface patterns, and similar conventions are expected, not accidental complexity. Use the team's conventions as the baseline, not an idealized minimum.

> Note: simplicity is domain-relative. Some problems are inherently complex. KISS means "don't add accidental complexity," not "avoid all complexity."

## YAGNI Pass

Look for code that exists only for hypothetical future use:

- Unused helpers, imports, parameters, config options, validators, adapters, or wrappers.
- Convenience APIs that duplicate a generic API without adding behavior.
- "Future-proof" parsing or compatibility logic with no tests, docs, or call sites.
- Stale comments describing behavior that no longer exists.

**Before removing, ask:**

- Is it documented as public surface?
- Is it imported outside the module?
- Is it needed for a framework hook, plugin registration, or generated schema?
- Does a test depend on the current contract?
- Does removing it foreclose a reasonable, near-term extension point without a clear path to add it back?

If any answer is "yes" or "unclear," report it as a compatibility risk - do not delete.

> **YAGNI misapplication guard**: YAGNI targets speculative _implementations_, not structural _seams_.

## DRY Pass

Reduce duplication only when the duplication has maintenance cost.

**Good DRY targets:**

- Repeated error mapping, task setup, serialization, validation, or result shaping across modules.
- Multiple tests reimplementing the same nontrivial fixture or async fake.
- Docs repeating stale architecture in several places.

**Rule of Three**: Duplicate code once if necessary. On the third occurrence across distinct call sites, treat it as a DRY candidate and extract a shared helper.

**Skip DRY when:**

- Two call sites are similar but likely to evolve differently (shared name, different policy).
- A helper would obscure a simple one-liner.
- The abstraction name would be vaguer than the code it replaces.
- Forcing DRY would conflict with KISS or YAGNI.

Good DRY cleanup creates one small helper at the same architectural layer as the repeated behavior. It does not create new layers or cross module boundaries without justification.
