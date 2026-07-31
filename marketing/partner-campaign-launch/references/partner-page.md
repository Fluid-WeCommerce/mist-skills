# Professional partner page boundary

The public page should look like the partner's own business collaborating with
the company: for example, a gym's coaching offer with an approved WHOOP product
path—not a counterfeit company-owned page. It should contain the partner name,
business identity, factual program framing, disclosure, and a clear attributed
CTA. Do not imply employment, exclusivity, medical endorsement, or an official
partnership unless the company has approved that exact language.

## Safe automated checks

- Require public `https://`, no `user:password@host`, no fragments or sensitive
  query keys, and an allowlisted initial/final hostname. Reject private-network,
  loopback, local, and non-HTTP(S) destinations.
- Open the supplied public URL with `crawl` or `web_fetch`.
- Compare screenshot/markup to the user-supplied approved partner identity and
  company. A text response alone does not prove the copy is visibly rendered.
- Inspect the CTA `href` without opening it. Verify its host/product separately;
  following a tracking link requires separate approval because it can emit analytics.
- Record the presence and kind of attribution parameter; redact its value. Do
  not claim it survives another device or becomes a paid membership.
- Capture desktop/mobile evidence when browser tools are available.

## MySite mutation boundary

This v1 skill validates a partner page and makes no MySite API mutation.

- Do not call `GET /api/me` merely to discover identity: its response can include
  credentials, and those must never be persisted in chat or evidence.
- Do not use `PUT /api/me` for profile copy while mutation-history preflight can
  store that sensitive response.
- `PUT /api/mysite` is self-scoped and currently lacks an automatic inverse;
  theme/slug changes require a separate explicit approval and manual rollback.
- A future, separately approved activation may create an absent link under
  `/api/users/{user_id}/links` or favorite under
  `/api/user_companies/{membership_id}/favorites` only after proving the current
  authenticated membership is the intended partner and checking exact duplicates.
  That path id does not let an admin select another member. Updates, deletes,
  bulk operations, and reorder operations remain prohibited.
- Admin credentials cannot safely assign another member's MySite theme or
  favorites through the legacy member-scoped endpoints.

Treat full partner enrollment, invite-only access, campaign conversion reports,
membership rewards, and retained-member rewards as separate capabilities. The
launch skill must not pretend UI copy implements those systems.
