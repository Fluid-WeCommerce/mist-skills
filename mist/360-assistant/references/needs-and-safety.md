# Problem → product matching, and the medical guard

Two subjects in one file because they are inseparable: the moment an assistant can answer *"my skin
is dry"*, it can also answer *"can this fix my eczema?"* — and the second answer is regulated.

This is the most portable capability in the skill. Every company has customers who describe a need
rather than a SKU. It is also the one most likely to cause real harm if the guards are skipped, so
the guards are the design, not a polish pass.

---

## Part 1 — Answering a described problem

"My skin is dry." "I can't sleep." "My bathroom smells." "My back aches after work." The customer has
told you the **job**, not the product.

### Why search cannot do this

**Product search is title-only.** Verified live: a query for a word that appears in a product's
*description* — not its title — returns **zero results**, on a catalogue that literally contains that
word. Re-verify it at every new company (Part A probe), but expect it to hold.

A problem statement almost never contains a product's title words. Nobody types "lotion" when their
skin is dry; nobody types the brand's product name for a thing they don't know exists yet.

So needs are matched against product **descriptions**. List endpoints don't return descriptions, so
the implementation lists once, fetches detail per product in bounded batches, and caches per country.
**Suppression still applies**, so a spare part can never surface as the answer to a problem.

### Nothing in this lane knows what the company sells

This is what makes it work at the next company with no edits. The mapping from "dry skin" to a
moisturiser comes from **the moisturiser's own description saying "dry skin"**. The company already
wrote the answer on the product; this finds it.

The lexicon that bridges customer words to marketing words is deliberately made of **language**
facts, never catalogue facts:

```
dry     → hydrat, moistur
tired   → energis, revital
smelly  → odour, deodor, fresh
bloated → digest, fibre
sore    → sooth, relief-adjacent marketing vocabulary
```

Both sides of one idea, in any category. **If you find yourself adding a product name to it, stop** —
that belongs in the company profile, and it means the lane has stopped being general.

### The four guards

**1. An evidence floor.** Require a title hit, **or two independent description hits**. One
incidental word in a long description is not a recommendation.

**2. No match is a good answer.** Return nothing and ask what they're after. Answering an unrelated
problem with whatever ranks first is how someone with dry skin gets offered a doormat.

**3. A stem you chose may prefix-match; a word the customer typed may not.** This one was found in
production: *"my car keeps breaking down"* recommended **gift cards**, because `car` prefix-matched
"Cards".

So terms carry their matching mode:

| Origin | Matching | Why |
|---|---|---|
| A stem **you** chose (`hydrat`) | prefix | must catch hydrating / hydration |
| A word the **customer** typed (`car`) | whole word + ordinary inflections | must not catch "Cards" |

Same family of bug: a bare substring match found `night` inside "Overnight" and handed a sleep
question to a face balm. **Anchor at a word boundary.**

**4. Quote the product's own sentence; never paraphrase it.** Return the exact sentence that earned
the match and say it verbatim. Paraphrase is precisely how *"supports regularity"* becomes *"fixes
your constipation"* — which is Part 2's problem.

### Testing it

Fixtures for this lane should be a **different kind of shop** than the one you're building on — a
skincare-and-homeware catalogue works well regardless of the real company. If the tests only pass
against the current company's products, something has been hardcoded and the matcher has stopped
being general.

---

## Part 2 — The medical guard

A large share of merchants sell supplements, skincare, wellness or personal care. Presenting one as
**treating a condition** is a regulated claim — FTC substantiation rules, FDA disease-claim rules —
not merely over-enthusiasm. A company's own compliance record may exist precisely because it has
promised not to make those claims.

### What to flag

Condition language, in two families:

- **Named conditions:** eczema, IBS, constipation, migraine, UTI, insomnia, pregnancy, pain, rash,
  and the rest of the obvious set.
- **Treatment verbs:** treat, cure, heal, remedy, fix.

Keep this list, like the lexicon, as **language** facts. A product name appearing in it means
something has gone wrong.

**Any medical term counts as a need signal on its own**, regardless of sentence shape. People don't
phrase complaints tidily — *"I've been constipated lately"* matches no "my X is Y" pattern but is
plainly a request for help.

### Flagged does not mean refusing

Refusing outright is both unhelpful and unnecessary. The correct behaviour is four things at once:

1. **Show what the catalogue holds, in the product's own words.** The verbatim-sentence rule from
   Part 1 is what makes this safe: you are reporting what the company published, not making a claim.
2. **Say the caution line** — something plain and human that points them at a professional, in the
   brand's own register, without alarm.
3. **Offer a human.**
4. **Arm no cart.** Nudging someone toward checkout off the back of a health complaint is the wrong
   instinct even when the product is entirely legitimate. This is the rule most likely to be
   optimised away by someone measuring conversion; don't.

And never, in any phrasing: *treats · cures · prevents · relieves · fixes · helps with `<condition>`*.

### Allergens and ingredients — a different failure mode, on food and personal care

The medical guard above is about **regulated claims**. Allergens are about **physical safety**, and
they need their own handling because the failure mode is anaphylaxis rather than embarrassment.

If the catalogue is food, drink, supplements or anything applied to skin, expect: *"is this gluten
free?"*, *"does this have peanuts?"*, *"is it dairy free?"*, *"is this vegan?"*

**The rule is stricter than everywhere else in this skill: quote a published ingredient or allergen
statement verbatim, or hand off. There is no third option.**

- **Never infer from a product name, a category, or the absence of a mention.** "It doesn't say
  peanuts" is not "it has no peanuts", and a fried item's shared fryer or a facility's cross-contact
  will never appear in a marketing description.
- **Never generalise across a range.** One item's statement says nothing about its siblings.
- **No published statement ⇒ hand off**, and say why in the customer's terms — you want them to have
  the real answer, not your reading of a product page.
- **Preparation claims are out of scope entirely.** Cross-contamination, shared equipment and
  substitutions are operational facts an assistant cannot know.
- **Never soften with a hedge** ("should be fine", "I think so"). A hedge reads as reassurance.

Worth recording in the company profile as an explicit handoff topic whenever the catalogue is
ingestible and no allergen page exists — which, on a freshly imported catalogue, is the usual case.

### Why condition words are still bridged into product vocabulary

It would be simpler to drop flagged messages entirely. Don't — **matching is discovery, not
claiming.** Finding a candidate is not the same as asserting it works, and without the bridge
(constipation → regular / digest / fibre) a real need goes unanswered, which helps nobody.

The bridge finds the product. The guard governs what you're allowed to say about it. Those are
separate jobs and both are needed.

### Worked shape

> **Customer:** "I've been constipated lately, does anything here help?"
>
> **Assistant:** *names the product the catalogue actually holds, quotes its own description sentence
> verbatim, adds the caution line, offers a human — and offers no cart.*

The reply contains no assertion that the product treats anything. It contains what the company wrote,
which is a fact about the catalogue rather than a claim about the customer's body.

---

## Checklist before shipping either part

- Does a problem with **no** match return nothing, rather than the top-ranked unrelated product?
- Is every recommendation's evidence a **quoted sentence** from the product, not a paraphrase?
- Does a customer-typed word match as a **whole word**, and only your own stems as prefixes?
- Do the fixtures describe a **different catalogue** than the live company's?
- Does a condition word **suppress the cart** on every path, including the ones that reach the
  recommendation by another route?
- Is there a test asserting **no treatment claim** appears, across several phrasings of the same
  question?
