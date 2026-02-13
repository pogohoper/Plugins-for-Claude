---
name: clarify
description: Analyzes your request and speaks back a concise TTS summary of what it understood and how it plans to do it
user-invocable: true
argument-hint: "<what you want done>"
---

# Intent Clarification

The user described a task. Your ONLY job is to **clarify your understanding back to them via spoken audio**. Do NOT execute the task.

## User's Request

$ARGUMENTS

## Process

1. **Analyze** the request. Determine:
   - The core goal — what concrete outcome do they want?
   - The implicit requirements they didn't spell out
   - Which files, systems, or patterns are involved
   - Your planned approach — what steps, in what order

2. **Draft** a spoken clarification. Rules:
   - **2-4 sentences max** — must be under 25 seconds spoken
   - **Every word earns its place** — no filler, no hedging, no "I think"
   - **Name specifics** — files, functions, tools, patterns, technologies
   - **State approach** — "I'll do X by Y, touching Z"
   - **Surface assumptions** — if you interpreted something ambiguously, say which way you went
   - **Natural speech** — contractions are fine, write for the ear not the eye

3. **Speak it** by invoking the `/tts` skill with your clarification text. Do not output the clarification as regular text — only speak it.

## Tone

Direct and confident. Like a senior engineer confirming a task with a colleague: "Got it — here's what I'll do."

## Examples of Good Clarifications

"You want rate limiting on the API. I'll add an Express middleware using a sliding-window counter in Redis, apply it globally with stricter limits on auth endpoints, and add the config to the existing env schema. Four files: middleware, app setup, env config, and a test."

"So you need the sidebar to collapse on mobile. I'll add a responsive breakpoint at 768px using the existing Tailwind config, toggle visibility with a useState hook in the Layout component, and add a hamburger button that only renders below the breakpoint."

"You want me to split the monolith User model into separate Profile and Auth models. I'll create the new Prisma schemas, write a migration, update the three services that import User, and make sure the existing API responses don't change shape."

## Critical

- Do NOT start working on the task
- Do NOT output the text as a message — ONLY speak it via /tts
- If the request is too vague to form a concrete plan, say what's unclear in the TTS
