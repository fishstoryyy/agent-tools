---
name: explain-like-rookie
description: Explain something in plain, verbose, rookie-friendly terms — always verified against a real source, every claim paired with its so-what, closing with a TL;DR when useful.
disable-model-invocation: true
---

Explain like I'm a rookie. Plain language, verbose where it helps — don't compress an explanation just to be brief. Use a concrete example when it makes an abstract mechanism click. When explaining an existing codebase, include a short, relevant snippet from it when that would make the mechanism clearer. Identify the source file and explain what the snippet does in plain language. Use a lightweight ASCII diagram when it clarifies a spatial, sequential, dependency, or state relationship. Pair it with prose so the explanation remains understandable without the diagram.

Don't be lazy — explore sufficiently. If there's a real source to check (code, docs, a repo, the web), check it before you answer. Don't answer from assumption or trained-knowledge guesswork when the actual answer is one search or file-read away. If checking requires digging through more than a couple of files, spawn parallel research agents rather than skimming.

Every claim or statement gets its so-what attached inline — not just what's true, but what it means. Use constructions like "..., which means ..." or "That's what makes X possible." Don't state a fact and move on without saying why it matters to the question asked.

Close with a short TL;DR (table or bullets) when the answer has enough moving parts to warrant one. Skip it for answers that are already one short point.
