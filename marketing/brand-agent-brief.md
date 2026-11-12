---
name: Brand Agent Brief
description: Build the business profile, answer pack and guardrails an AI brand agent needs (ChatGPT business profile and Business Agent, an on-site shopper assistant) from this store's real catalog, shipping and brand voice, and flag what is missing before anything is published.
icon: bot
category: marketing
---

# Goal

AI assistants now let a business claim a profile and publish its own agent that answers shoppers' questions about the store's products. The agent is only as good as what it is told. Produce a brief for {{company.name}} that a person can paste into an agent setup form or hand to a developer: who the business is, what it sells, the policies the agent may quote, the questions it must be able to answer, and the things it must never promise. Read-only: this skill changes nothing in Fluid.

Do not quote conversion rates, traffic numbers or benchmarks. Do not invent a policy. If a fact is not in the store's own data, mark it MISSING and say who has to supply it.

Today is {{today}}.

# Steps

1. **Read the store in parallel.**
   - `fluid_api("/api/v202604/products?page[limit]=50", "GET")` - the public catalog, live products only. Follow `meta.pagination.next_cursor` as `page[cursor]` until you have the top 50 products or the end. Note each product's title, description, price and currency, availability, variants and images.
   - `fluid_api("/api/v2025-06/shipping_methods", "GET")` - the shipping methods the store offers.
   - `fluid_api("/api/settings/brand_guidelines", "GET")` - name, colors and any voice notes.
   - `run_cli` `fluid countries list` - the countries the store sells in.
   - Fetch the store's own `/llms.txt` and `/agents.md` from its storefront domain if they exist. They are the policy text the store already publishes for agents. If a fetch fails, say so and carry on.
   - Read `brand.md` if the workspace has one; it sets the agent's tone.
2. **Business profile.** Draft: display name, one-sentence description, what it sells in three categories or fewer, who it sells to, the countries it ships to, a support contact if the store publishes one. Mark anything not found as MISSING.
3. **Policy answers.** From the published policy text and shipping methods, write plain answers for: shipping options and cost, delivery time, returns and refunds, order changes, payment methods, warranty. Quote the source (a page or method name) beside each. If a policy is not published, write MISSING and name it. Never fill the gap with a typical policy.
4. **Product answer pack.** For the 20 products with the most complete data, list the questions a shopper asks before buying (what is it made of, size or fit, who is it for, how do I use or care for it, what is in the box, is it in stock) and answer each only from the product's own fields. A question the data cannot answer goes in the gaps table, not in the pack.
5. **Gaps table.** One row per missing fact: product or policy, the question it blocks, who fills it (merchant, supplier, or Fluid), and how many of the 50 products have the same gap.
6. **Guardrails.** Draft the rules the agent runs under: quote only prices and stock shown in the brief or read live from the catalog; never promise delivery dates the shipping methods do not state; never give medical, legal or income claims, and hand those questions to a person; send refund and order-status requests to the store's support contact; say "I do not know" when the brief is silent. If {{company.name}} sells under a direct-sales or health-adjacent model, say plainly that claims review belongs to the brand's own compliance owner and list the products whose descriptions contain health or earnings language for that review.
7. **Output.** One document with these headings: Business profile, Policy answers, Product answer pack, Gaps, Guardrails. Put the gaps first in your chat reply so the user sees what blocks publishing. End by asking whether to save it to the workspace as `agent-brief.md`; write the file only after they say yes.

# What this skill does not do

It does not claim or verify a business on any AI platform, publish an agent, or change catalog data. Whether {{company.name}} is eligible for a platform's business agent depends on that platform; tell the user to check eligibility in the platform's own business settings.
