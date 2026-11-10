---
name: Add a shop to a member site
description: Add products by real variant id to a static member site, with add to cart, open cart and checkout through fluid.cart and credited storefront links from fluid.storefront.url.
icon: shopping-cart
---

# Goal

Let a static member site sell or recommend the company's products: a list of real variants with **Add to cart**, **Open cart** and **Checkout** buttons that use the storefront's own cart, and links to the storefront that keep the credit of whoever shared the site.

# Steps

1. Confirm the active folder is a static member site: `read_file("package.json")` and check that `dependencies` or `devDependencies` names `@fluid-app/sites`. If not, stop and say: "This folder isn't a static member site (its package.json doesn't depend on @fluid-app/sites), so I didn't change anything." A Liquid member site or a theme uses other patterns; never use `fluid member-site` commands here.
2. Read `src/` first. A site that started from the full demo already has `src/products.ts` and `src/pages/Shop.tsx`: extend those rather than adding a second shop.
3. Get the products. Ask the user which products to show and in what order, with a short line for each if they want one. Find each variant id:
   - `fluid_api("/api/v202604/company/products?page[limit]=100", "GET")` lists the catalog; each product's `default_variant` carries its master variant's `id`.
   - When a product has several variants (sizes, flavors) or no default variant, `fluid_api("/api/v202604/company/products/<id>", "GET")` returns its `variants`; ask the user which one.
   - Show the user the name and variant id of every product before writing them. Never invent an id and never ship a placeholder. The demo's `products.ts` ships `variantId: 0`: replace it.
4. List them in `src/products.ts`:

   ```ts
   export interface Recommendation {
     variantId: number;
     name: string;
     blurb: string;
   }

   export const recommendations: Recommendation[] = [
     { variantId: 123456, name: "Daily Greens", blurb: "What I start every day with." },
   ];
   ```

5. Write the shop page, the shape the reference demo uses:

   ```tsx
   import { fluid } from "@fluid-app/sites";
   import { useEffect, useState } from "react";
   import { recommendations } from "../products";

   export function Shop() {
     const [status, setStatus] = useState<string | null>(null);
     const [storeUrl, setStoreUrl] = useState<string | null>(null);

     useEffect(() => {
       fluid.storefront.url("/shop").then(setStoreUrl, () => setStoreUrl(null));
     }, []);

     const add = async (variantId: number) => {
       setStatus("Adding…");
       try {
         await fluid.cart.add([{ variant_id: variantId, quantity: 1 }]);
         setStatus("Added to your cart.");
       } catch (error) {
         setStatus(error instanceof Error ? error.message : "The cart did not answer.");
       }
     };

     return (
       <section>
         <h1>Shop</h1>
         <ul className="products">
           {recommendations.map((product) => (
             <li key={product.variantId}>
               <h2>{product.name}</h2>
               <p>{product.blurb}</p>
               <button type="button" onClick={() => add(product.variantId)}>Add to cart</button>
             </li>
           ))}
         </ul>
         {status && <p role="status">{status}</p>}
         <p className="actions">
           <button type="button" onClick={() => fluid.cart.open()}>Open cart</button>
           <button type="button" onClick={() => fluid.cart.checkout()}>Checkout</button>
           {storeUrl && <a href={storeUrl}>The whole store</a>}
         </p>
       </section>
     );
   }
   ```

   - `fluid.cart.add` rejects when the cart fails, so always show its message. `open()` and `checkout()` log a failure and never throw.
   - Call `checkout()` and `open()` only from a button the member clicks, never on load or from a timer: checkout moves the storefront's window.
   - Every link to the storefront (its shop, a product, a collection) is a plain `<a href>` whose address comes from `fluid.storefront.url(path)`. That address carries the visit's credit, so the sale is credited to whoever shared the site. Never hard-code a storefront URL, and never use `window.open(url, "_top")`, `top.location` or `target="_top"`: the frame refuses them.
   - The cart needs no scope in `config/access.json`.
6. Wire it in: the page's path in `src/App.tsx`, a `<Link to="/shop">` in the header (never a bare `<a>` between the site's own pages), and its title and description in `config/meta.json`. Style it with the tokens at the top of `src/styles.css`; name no new colors elsewhere.
7. Check it locally:
   - `npm run build` through `run_cli`: it typechecks, then writes `dist/`.
   - `start_preview` (Mist runs `fluid sites dev`), then `screenshot_preview` at the shop's path: every product and button renders. `read_preview_console` for errors.
   - Locally there is no storefront around the site, so `fluid.cart.add` answers that it needs the storefront shell, `open` and `checkout` only log, and `fluid.storefront.url` has no storefront address, so the store link does not show. That is expected, not a bug to fix.
8. Run `fluid sites lint` through `run_cli` and fix every error.
9. Report the products and variant ids you used, and what can only be checked once the site is published and opened at its storefront address: Add to cart, the cart drawer, checkout, member pricing, and the credited store link. Publishing is the **Publish and check** skill.

# Guardrails

- Never ship a placeholder or guessed variant id.
- Never start checkout or open the cart without a click.
- Never build a storefront link by hand: it drops the sharer's credit.
- Do not publish in this skill.
