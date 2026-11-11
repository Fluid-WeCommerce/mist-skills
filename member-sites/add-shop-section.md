---
name: Add a shop to a Site
description: Add products to a Site, read live from the storefront catalog, with add to cart, open cart and checkout through fluid.cart and credited storefront links from fluid.storefront.url.
icon: shopping-cart
---

# Goal

Let a Site sell or recommend the company's products: a list of real variants with **Add to cart**, **Open cart** and **Checkout** buttons that use the storefront's own cart, and links to the storefront that keep the credit of whoever shared the site.

# Steps

1. Confirm the active folder is a Site: `read_file("package.json")` and check that `dependencies` or `devDependencies` names `@fluid-app/sites`. If not, stop and say: "This folder isn't a Site (its package.json doesn't depend on @fluid-app/sites), so I didn't change anything." An old Liquid site or a theme uses other patterns; never use `fluid member-site` commands here.
2. Read `src/` first. A site that started from the full demo already has `src/products.ts` and `src/pages/Shop.tsx`: extend those rather than adding a second shop.
3. Choose the products, never their names or prices. Ask the user which products to show and in what order (an optional short line of their own for each is fine). Find each product's `slug`: `fluid_api("/api/v202604/company/products?page[limit]=100", "GET")` lists the catalog. Show the user the name and slug of every product before writing them. Never invent a slug or an id, and never ship a placeholder. The demo's `products.ts` ships names and `variantId: 0`: replace it.
4. List only the slugs in `src/products.ts`, and read each product from the storefront's public catalog when the page loads, so names, images and prices stay current and show the visitor's currency:

   ```ts
   import { fluid } from "@fluid-app/sites";

   export const featured = ["daily-greens", "protein-blend"];

   export interface ProductCard {
     slug: string;
     title: string;
     images: { image_url: string }[];
     pricing: { display_price: string } | null;
     default_variant: { id: number } | null;
   }

   // GET /api/v202604/products/<slug> on the storefront: public, no token.
   export async function loadProducts(country?: string): Promise<ProductCard[]> {
     const me = await fluid.auth.me();
     const read = async (slug: string) => {
       const url = new URL(`/api/v202604/products/${encodeURIComponent(slug)}`, me.storefrontUrl);
       if (country) url.searchParams.set("country", country);
       const res = await fetch(url, { headers: { Accept: "application/json" } });
       return res.ok ? ((await res.json()) as { product: ProductCard }).product : null;
     };
     const found = await Promise.all(featured.map(read));
     return found.filter((p): p is ProductCard => p !== null);
   }
   ```

   - `pricing` is the retail price for `country` (ISO-2; the company's default country when left out). Show `pricing.display_price`; a null `pricing` is unavailable, never free. The cart applies the visitor's own (member) price when they add it.
   - A product that is not live or not sold in that country answers 404 and is left out. For a whole collection or category, read `/api/v202604/collections/<slug>/products` or `/api/v202604/categories/<slug>/products` (`{ products, meta }`).
   - This public catalog is the one thing a Site reads with its own `fetch`. Everything about the member goes through `fluid.api`.

5. Write the shop page:

   ```tsx
   import { fluid } from "@fluid-app/sites";
   import { useEffect, useState } from "react";
   import { loadProducts, type ProductCard } from "../products";

   export function Shop() {
     const [products, setProducts] = useState<ProductCard[] | null>(null);
     const [status, setStatus] = useState<string | null>(null);
     const [storeUrl, setStoreUrl] = useState<string | null>(null);

     useEffect(() => {
       loadProducts().then(setProducts, () => setStatus("The catalog did not answer."));
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
           {(products ?? []).map((product) => (
             <li key={product.slug}>
               {product.images[0] && <img src={product.images[0].image_url} alt="" />}
               <h2>{product.title}</h2>
               <p>{product.pricing ? product.pricing.display_price : "Unavailable"}</p>
               <button
                 type="button"
                 disabled={!product.default_variant || !product.pricing}
                 onClick={() => product.default_variant && add(product.default_variant.id)}
               >
                 Add to cart
               </button>
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
   - Locally there is no storefront around the site, so the catalog may not load, `fluid.cart.add` answers that it needs the storefront shell, `open` and `checkout` only log, and `fluid.storefront.url` has no storefront address, so the store link does not show. That is expected, not a bug to fix.
8. Run `fluid sites lint` through `run_cli` and fix every error.
9. Report the products and slugs you used, and what can only be checked once the site is published and opened at its storefront address: Add to cart, the cart drawer, checkout, member pricing, and the credited store link. Publishing is the **Publish and check** skill.

# Guardrails

- Never copy a product's name, image or price into the code, and never ship a placeholder or guessed slug or id.
- Never start checkout or open the cart without a click.
- Never build a storefront link by hand: it drops the sharer's credit.
- Do not publish in this skill.
