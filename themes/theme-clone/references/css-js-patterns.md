# Fluid CSS and JavaScript patterns

These patterns extend the canonical base-theme sections. They do not replace the Section
Shell + Container contract in `section-template.md`.

## Theme-driven CSS

Map source values into `config/settings_data.json`, then use the variables wired by
`layouts/theme.liquid`. Section CSS must not hardcode brand colors or font families.

```css
.feature {
  color: var(--clr-body);
  background: var(--clr-light);
  font-family: var(--ff-body);
}

.feature__title {
  color: var(--clr-primary);
  font-family: var(--ff-heading);
  font-size: clamp(2.5rem, 6vw, 6rem);
  line-height: 0.95;
}

.feature__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 32px;
}

@media (max-width: 991px) {
  .feature__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 24px;
  }
}

@media (max-width: 767px) {
  .feature__grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
```

Canonical breakpoints are exactly `991px` and `767px`, both expressed as `max-width`.
Do not introduce 749, 768, 1023, 1024, or one-off breakpoints in cloned sections.

## CSS scroll-snap carousel

Do not add Splide or another carousel runtime. The current base theme uses scroll-snap,
which works without a dependency, remains usable before JavaScript loads, and does not
duplicate slides.

```liquid
<div class="carousel" data-carousel="{{ section.id }}">
  <div class="carousel__track" data-carousel-track>
    {% for block in section.blocks %}
      <article class="carousel__slide" data-carousel-slide {{ block.fluid_attributes }}>
        {{ block.settings.text }}
      </article>
    {% endfor %}
  </div>
  <button type="button" class="carousel__control" data-carousel-previous aria-label="Previous slide">
    Previous
  </button>
  <button type="button" class="carousel__control" data-carousel-next aria-label="Next slide">
    Next
  </button>
</div>
```

```css
.carousel__track {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(280px, 32%);
  gap: 24px;
  overflow-x: auto;
  overscroll-behavior-inline: contain;
  scroll-snap-type: inline mandatory;
  scrollbar-width: none;
}

.carousel__track::-webkit-scrollbar {
  display: none;
}

.carousel__slide {
  min-width: 0;
  scroll-snap-align: start;
}

@media (max-width: 991px) {
  .carousel__track {
    grid-auto-columns: minmax(260px, 48%);
  }
}

@media (max-width: 767px) {
  .carousel__track {
    grid-auto-columns: 86%;
    gap: 16px;
  }
}
```

```javascript
(() => {
  const root = document.currentScript?.closest("[data-section-id]");
  const track = root?.querySelector("[data-carousel-track]");
  if (!(track instanceof HTMLElement)) return;

  const step = () => {
    const slide = track.querySelector("[data-carousel-slide]");
    if (!(slide instanceof HTMLElement)) return track.clientWidth;
    const gap = Number.parseFloat(getComputedStyle(track).columnGap) || 0;
    return slide.getBoundingClientRect().width + gap;
  };

  root.querySelector("[data-carousel-previous]")?.addEventListener("click", () => {
    track.scrollBy({ left: -step(), behavior: "smooth" });
  });
  root.querySelector("[data-carousel-next]")?.addEventListener("click", () => {
    track.scrollBy({ left: step(), behavior: "smooth" });
  });
})();
```

Scope every query to the current section instance. Never use a global ID shared by
multiple section instances.

## Accordion

Prefer native disclosure semantics:

```liquid
<div class="faq">
  {% for block in section.blocks %}
    <details class="faq__item" {{ block.fluid_attributes }}>
      <summary>{{ block.settings.question }}</summary>
      <div class="rte">{{ block.settings.answer }}</div>
    </details>
  {% endfor %}
</div>
```

Use `richtext` for `question` and `answer` when the visual editor must control their
typography. If richtext produces wrapping elements inside `summary`, render and inspect
the actual DOM before shipping.

## Reveal animation

Animation is progressive enhancement. Content must remain visible when JavaScript fails
or the user requests reduced motion.

```css
@media (prefers-reduced-motion: no-preference) {
  .has-reveal-js [data-reveal] {
    opacity: 0;
    transform: translateY(20px);
    transition:
      opacity 500ms ease,
      transform 500ms ease;
  }

  .has-reveal-js [data-reveal].is-visible {
    opacity: 1;
    transform: none;
  }
}
```

```javascript
(() => {
  const root = document.currentScript?.closest("[data-section-id]");
  if (!root) return;
  const items = [...root.querySelectorAll("[data-reveal]")];
  if (items.length === 0) return;
  root.classList.add("has-reveal-js");

  if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
    items.forEach((item) => item.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    },
    { rootMargin: "0px 0px -10% 0px" },
  );
  items.forEach((item) => observer.observe(item));
})();
```

## DOM-ready and editor re-rendering

Inline section scripts should execute after their markup and initialize only their own
section instance. Initialization must be idempotent because the Fluid editor can replace
or re-render a section without a full page load.

```javascript
(() => {
  const root = document.currentScript?.closest("[data-section-id]");
  if (!root || root.dataset.enhanced === "true") return;
  root.dataset.enhanced = "true";
  // Bind this section instance.
})();
```

## Fluid hooks are contracts

Never rename or remove the scaffold's cart and locale hooks:

- `#show-cart`
- `#fluid-cart-count`
- `#show-language-country-dropdown`
- `#mobile-country-language`
- `.saveLocaleBtn`
- `.country-selector`
- `.language-selector`
- `.locale-selector`

Compose the canonical block/component markup that owns these hooks. Do not recreate it
from a screenshot.

## Performance and accessibility gate

- Reserve image dimensions to prevent layout shift.
- Use responsive DAM variants instead of source-CDN hotlinks.
- Lazy-load below-the-fold images, not the LCP hero.
- Do not autoplay motion when reduced motion is requested.
- Every control is a real button or link with an accessible name.
- Keyboard interaction and visible focus must work.
- A carousel remains scrollable without JavaScript.
- No client code may create horizontal document overflow at 390px.
