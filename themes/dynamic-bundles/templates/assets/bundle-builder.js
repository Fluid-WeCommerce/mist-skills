/* =============================================================================
 * Fluid Dynamic Bundles — universal client engine
 * -----------------------------------------------------------------------------
 * Four isolated layers. Every platform data trap lives in exactly one of them.
 *
 *   normalize(raw, ctx)          drop JSON  -> typed, country-resolved BundleModel
 *   rules(model, selection)      pure       -> per-group state + violations
 *   render(model, state, refs)   DOM only   -> clones <template>s, sets text/attrs
 *   cart(model, selection)       money      -> bundled_items, SDK call, read-back
 *
 * No company constants. No bundle/product/group ids. No markup strings outside
 * render(). Restyling never touches logic; a drop-shape change lands only in
 * normalize().
 *
 * Contract: reference/03-data-contract.md + reference/07-cart-contract.md
 * ========================================================================== */
(function (root) {
  'use strict';

  /* ---------------------------------------------------------------------- *
   * 0. Primitives
   * ---------------------------------------------------------------------- */

  /** Coerce anything the platform emits into a finite number.
   *  Handles: floats, decimal strings, BigDecimal engineering notation
   *  ("0.4999e2"), null, "", and the literal integer 0. */
  function num(v) {
    if (v === null || v === undefined || v === '') return null;
    if (typeof v === 'number') return isFinite(v) ? v : null;
    var n = parseFloat(String(v));
    return isFinite(n) ? n : null;
  }

  /** First strictly-positive number in the chain, else null. A zero price on
   *  the platform means "unset", never "free" — that distinction is made by the
   *  caller via *Configured flags, not here. */
  function firstPositive() {
    for (var i = 0; i < arguments.length; i++) {
      var n = num(arguments[i]);
      if (n !== null && n > 0) return n;
    }
    return null;
  }

  /** Strict boolean — the backend compares with `== true`, so "true" and 1 are
   *  false everywhere. Mirror that exactly. */
  function strictBool(v) {
    return v === true;
  }

  function asArray(v) {
    return Array.isArray(v) ? v : [];
  }

  function str(v) {
    return v === null || v === undefined ? '' : String(v);
  }

  function upper(v) {
    return str(v).toUpperCase();
  }

  /* ---------------------------------------------------------------------- *
   * 1. normalize — every data trap in the platform lives here
   * ---------------------------------------------------------------------- */

  var KNOWN_GROUP_KEYS = [
    'id', 'title', 'description', 'group_type', 'sort_order', 'selection_type',
    'min_selections', 'max_selections', 'pricing_type', 'fixed_price', 'min_price',
    'max_price', 'compare_at_price', 'group_cv', 'group_qv', 'track_quantity',
    'country_pricing', 'pricing_config', 'allow_subscriptions', 'force_subscriptions',
    'image_urls', 'images', 'bundle_group_items', 'created_at', 'updated_at'
  ];

  var KNOWN_ITEM_KEYS = [
    'id', 'quantity', 'sort_order', 'price', 'cv', 'qv', 'is_default',
    'display_quantity', 'max_quantity', 'allow_subscription', 'force_subscription',
    'product_id', 'product_title', 'product_image_url', 'product_bundles',
    'image_url', 'available_country_codes', 'country_prices',
    'country_subscription_prices', 'subscription_plan_id', 'subscription_plans',
    'in_stock', 'available_quantity', 'config', 'variant'
  ];

  function unknownKeys(obj, known) {
    var out = [];
    for (var k in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, k) && known.indexOf(k) === -1) out.push(k);
    }
    return out;
  }

  /** variant_countries row for this ISO, or null. */
  function variantCountry(variant, iso) {
    var rows = asArray(variant && variant.variant_countries);
    for (var i = 0; i < rows.length; i++) {
      if (upper(rows[i].country_iso) === iso) return rows[i];
    }
    return null;
  }

  /** country_pricing[] row for this ISO where enabled === true, or null. */
  function countryPricingRow(list, iso) {
    var rows = asArray(list);
    for (var i = 0; i < rows.length; i++) {
      if (upper(rows[i].country_code) === iso && strictBool(rows[i].enabled)) return rows[i];
    }
    return null;
  }

  /** item.country_prices is keyed by ISO; the value is either a decimal string
   *  or an object { price, wholesale }. Both shapes occur. */
  function itemCountryPrice(item, iso) {
    var map = item && item.country_prices;
    if (!map || typeof map !== 'object') return null;
    var v = map[iso] !== undefined ? map[iso] : map[iso.toLowerCase()];
    if (v === undefined || v === null) return null;
    if (typeof v === 'object') return num(v.price);
    return num(v);
  }

  /** Image chain. item.image_url and variant.image_url are blank essentially
   *  always; some bundles have no image anywhere, so '' is a legal answer and
   *  the placeholder path must work. */
  function itemImage(item, fallback) {
    var v = item.variant || {};
    var imgs = asArray(v.images);
    var first = imgs[0] || {};
    return (
      str(v.image_url) ||
      str(first.preview_image && first.preview_image.src) ||
      str(first.src) ||
      str(item.image_url) ||
      str(item.product_image_url) ||
      str(fallback) ||
      ''
    );
  }

  /** Repair the selection bounds the platform's own normalize_selection_bounds
   *  leaves nil, and flag the configurations that would 500 the cart (P16). */
  function selectionBounds(group, warnings) {
    var type = group.selection_type;
    var rawMin = num(group.min_selections);
    var rawMax = num(group.max_selections);
    var min = null, max = null, configError = null;

    if (group.group_type !== 'customizable') return { min: null, max: null, configError: null };

    switch (type) {
      case 'exact':
        min = rawMin;
        max = rawMin;
        if (min === null) configError = 'exact group has no min_selections';
        break;
      case 'min_only':
        min = rawMin;
        max = null;
        if (min === null) configError = 'min_only group has no min_selections';
        break;
      case 'max_only':
        min = 0;
        max = rawMax;
        if (max === null) configError = 'max_only group has no max_selections';
        break;
      case 'min_and_max':
        min = rawMin === null ? 0 : rawMin;
        max = rawMax;
        if (max === null) configError = 'min_and_max group has no max_selections';
        break;
      default:
        configError = 'customizable group has no selection_type';
    }
    if (configError) warnings.push('Group "' + str(group.title) + '": ' + configError);
    return { min: min, max: max, configError: configError };
  }

  /** mutually_exclusive_groups holds SORT ORDERS, not group ids, in two shapes,
   *  and is null (not []) on older bundles. Read bundle_config first — the
   *  top-level key exists only in the 40-key ProductDrop shape. */
  function exclusiveSets(raw) {
    var cfg = raw.bundle_config || {};
    var src = cfg.mutually_exclusive_groups;
    if (!src) src = raw.mutually_exclusive_groups;
    var list = asArray(src);
    var sets = [];
    for (var i = 0; i < list.length; i++) {
      var e = list[i];
      if (typeof e === 'number') {
        // legacy bare Array<Integer> — one flat set of sort_orders
        if (!sets.length) sets.push({ sortOrders: [], defaultSortOrder: null });
        sets[0].sortOrders.push(e);
      } else if (e && Array.isArray(e.ids)) {
        sets.push({
          sortOrders: e.ids.map(function (n) { return num(n); }).filter(function (n) { return n !== null; }),
          defaultSortOrder: e['default'] === null || e['default'] === undefined ? null : num(e['default'])
        });
      }
    }
    return sets.filter(function (s) { return s.sortOrders.length > 1; });
  }

  function normalize(raw, ctx) {
    ctx = ctx || {};
    var iso = upper(ctx.countryIso || 'US');
    var warnings = [];
    var unknown = [];
    raw = raw || {};

    var bundleCfg = raw.bundle_config || {};
    var pricingCfg = bundleCfg.bundle_pricing_config || {};
    var bundlePricingEnabled = strictBool(bundleCfg.bundle_pricing_enabled);
    var bundleRow = countryPricingRow(pricingCfg.country_pricing, iso);

    var groups = asArray(raw.product_bundle_groups)
      // Hidden groups are filtered in the drop shape but NOT in page scope.
      .filter(function (g) {
        return !strictBool(g.pricing_config && g.pricing_config.hidden);
      })
      .map(function (g) {
        unknown = unknown.concat(unknownKeys(g, KNOWN_GROUP_KEYS));
        var gpc = g.pricing_config || {};
        var gRow = countryPricingRow(g.country_pricing || gpc.country_pricing, iso);
        var bounds = selectionBounds(g, warnings);

        // fixed_price reads "0.0" when unset — key presence is the only way to
        // tell an unset price from a real zero.
        var fixedConfigured = Object.prototype.hasOwnProperty.call(gpc, 'fixed_price') &&
          gpc.fixed_price !== null && gpc.fixed_price !== '';
        var fixedPrice = gRow ? num(gRow.price) : (fixedConfigured ? num(gpc.fixed_price) : null);

        var items = asArray(g.bundle_group_items).map(function (it) {
          unknown = unknown.concat(unknownKeys(it, KNOWN_ITEM_KEYS));
          var v = it.variant || {};
          var vc = variantCountry(v, iso);
          var codes = asArray(it.available_country_codes).map(upper);

          var price = firstPositive(
            itemCountryPrice(it, iso),
            it.price,
            vc && vc.price
          );
          var subPrice = firstPositive(
            it.country_subscription_prices && it.country_subscription_prices[iso],
            vc && vc.subscription_price
          );
          var comparePrice = num(vc && vc.compare_price);

          return {
            id: num(it.id),
            variantId: num(v.id),
            sourceProductId: num(it.product_id),
            title: str(it.product_title) || str(v.display_name) || str(v.title),
            variantTitle: v.is_master ? '' : str(v.title),
            image: itemImage(it, ctx.fallbackImage),
            quantity: num(it.quantity) || 1,
            displayQuantity: num(it.display_quantity) || num(it.quantity) || 1,
            maxQuantity: num(it.max_quantity),
            isDefault: strictBool(it.is_default),
            allowSubscription: strictBool(it.allow_subscription),
            forceSubscription: strictBool(it.force_subscription),
            subscriptionPlanId: num(it.subscription_plan_id),
            subscriptionPlans: asArray(it.subscription_plans),
            price: price,
            priced: price !== null,
            comparePrice: comparePrice !== null && price !== null && comparePrice > price ? comparePrice : null,
            subscriptionPrice: subPrice,
            // CV/QV are Integers here and strings in both APIs. Only display
            // them for dynamic_price groups (see model.cvFlows).
            cv: num(vc && vc.cv) || 0,
            qv: num(vc && vc.qv) || 0,
            inStock: it.in_stock !== false,
            availableQuantity: num(it.available_quantity),
            // Two independent gates: the BGI country list, and whether the
            // variant actually has a priced row for this country (P6).
            availableInCountry: (codes.length === 0 || codes.indexOf(iso) !== -1) && !!vc
          };
        });

        var pricingType = str(g.pricing_type) || 'fixed_price';
        return {
          id: num(g.id),
          sortOrder: num(g.sort_order) || 0,
          type: g.group_type === 'included' ? 'included' : 'customizable',
          title: str(g.title),
          description: str(g.description),
          selectionType: str(g.selection_type) || null,
          min: bounds.min,
          max: bounds.max,
          configError: bounds.configError,
          pricingType: pricingType,
          fixedPrice: fixedPrice,
          fixedPriceConfigured: fixedConfigured || !!gRow,
          allowSubscriptions: strictBool(g.allow_subscriptions),
          forceSubscriptions: strictBool(g.force_subscriptions),
          items: items
        };
      })
      .sort(function (a, b) { return a.sortOrder - b.sortOrder; });

    // An included group with no explicit price displays as its item sum and
    // charges $0.00 (finding C). Warn loudly — it is real money.
    groups.forEach(function (g) {
      if (g.type === 'included' && !g.fixedPriceConfigured && !bundlePricingEnabled) {
        warnings.push('Group "' + g.title + '" is included with no configured price — it will charge $0.00.');
      }
      g.items.forEach(function (it) {
        if (!it.availableInCountry) {
          warnings.push('"' + it.title + '" has no priced row for ' + iso + ' — it would zero the bundle total.');
        }
      });
    });

    var sets = exclusiveSets(raw).map(function (s) {
      return {
        sortOrders: s.sortOrders,
        defaultSortOrder: s.defaultSortOrder,
        groupIds: s.sortOrders.map(function (so) {
          var g = groups.filter(function (gg) { return gg.sortOrder === so; })[0];
          return g ? g.id : null;
        }).filter(function (x) { return x !== null; })
      };
    }).filter(function (s) { return s.groupIds.length > 1; });

    return {
      productId: num(raw.id),
      title: str(raw.title),
      parentVariantId: num(
        (raw.selected_or_first_available_variant && raw.selected_or_first_available_variant.id) ||
        (asArray(raw.variants)[0] || {}).id
      ),
      countryIso: iso,
      bundlePricingEnabled: bundlePricingEnabled,
      bundleFlatPrice: bundleRow ? num(bundleRow.price) : null,
      bundleSubscriptionPrice: bundleRow ? num(bundleRow.subscription_price) : null,
      subscriptionPlans: asArray(raw.subscription_plans),
      // CV/QV only flow from dynamic_price groups. Anything else credits 0/0
      // unless re-entered on the group/bundle country row.
      cvFlows: groups.some(function (g) { return g.pricingType === 'dynamic_price'; }),
      groups: groups,
      exclusiveSets: sets,
      warnings: warnings,
      unknownFields: unknown.filter(function (v, i, a) { return a.indexOf(v) === i; })
    };
  }

  /* ---------------------------------------------------------------------- *
   * 2. rules — mirrors CartBundleValidator, client-side, before the request
   * ---------------------------------------------------------------------- */

  function key(groupId, variantId) { return groupId + ':' + variantId; }

  /** selection: { "<groupId>:<variantId>": { qty, subscribe, planId } }
   *  branches:  { "<setIndex>": <groupId> }  — chosen exclusive branch */
  function rules(model, selection, branches) {
    selection = selection || {};
    branches = branches || {};
    var perGroup = {};
    var violations = [];

    var inactive = {};
    model.exclusiveSets.forEach(function (set, i) {
      var chosen = branches[i];
      if (chosen === undefined || chosen === null) {
        violations.push({ type: 'exclusive_unchosen', setIndex: i, message: 'Choose one option to continue' });
        set.groupIds.forEach(function (gid) { inactive[gid] = true; });
      } else {
        set.groupIds.forEach(function (gid) { if (gid !== chosen) inactive[gid] = true; });
      }
    });

    model.groups.forEach(function (g) {
      // The server counts UNITS (sum of quantity), not entries, and drops
      // quantity-0 entries before counting.
      var count = 0, lines = 0;
      g.items.forEach(function (it) {
        var e = selection[key(g.id, it.variantId)];
        if (e && e.qty > 0) { count += e.qty; lines += 1; }
      });

      var isInactive = !!inactive[g.id];
      var state = {
        groupId: g.id,
        type: g.type,
        inactive: isInactive,
        count: count,
        lines: lines,
        min: g.min,
        max: g.max,
        atMax: g.max !== null && count >= g.max,
        remaining: g.max === null ? null : Math.max(0, g.max - count),
        satisfied: true,
        blocked: false,
        reason: ''
      };

      if (g.type === 'included' || isInactive) {
        perGroup[g.id] = state;
        return;
      }

      if (g.configError) {
        state.satisfied = false;
        state.blocked = true;
        state.reason = 'This option group is misconfigured and cannot be ordered.';
        violations.push({ type: 'config_error', groupId: g.id, message: state.reason });
        perGroup[g.id] = state;
        return;
      }

      if (g.min !== null && count < g.min) {
        state.satisfied = false;
        state.reason = g.selectionType === 'exact'
          ? 'Choose ' + g.min
          : 'Choose at least ' + g.min;
        violations.push({ type: 'under_min', groupId: g.id, message: '"' + g.title + '" ' + state.reason.toLowerCase() });
      } else if (g.max !== null && count > g.max) {
        state.satisfied = false;
        state.reason = 'Remove ' + (count - g.max) + ' to continue';
        violations.push({ type: 'over_max', groupId: g.id, message: '"' + g.title + '" allows at most ' + g.max });
      }

      // Per-item cap and subscription legality — both are hard 422s server-side.
      g.items.forEach(function (it) {
        var e = selection[key(g.id, it.variantId)];
        if (!e || e.qty <= 0) return;
        if (it.maxQuantity !== null && e.qty > it.maxQuantity) {
          violations.push({ type: 'over_item_max', groupId: g.id, variantId: it.variantId,
            message: '"' + it.title + '" is limited to ' + it.maxQuantity });
        }
        if (e.subscribe && !it.allowSubscription && !it.forceSubscription) {
          violations.push({ type: 'sub_not_allowed', groupId: g.id, variantId: it.variantId,
            message: '"' + it.title + '" cannot be subscribed' });
        }
        if (it.forceSubscription && !e.subscribe) {
          violations.push({ type: 'sub_required', groupId: g.id, variantId: it.variantId,
            message: '"' + it.title + '" requires a subscription' });
        }
        if (!it.availableInCountry) {
          violations.push({ type: 'country_unavailable', groupId: g.id, variantId: it.variantId,
            message: '"' + it.title + '" is not available in your region' });
        }
      });

      perGroup[g.id] = state;
    });

    return {
      perGroup: perGroup,
      violations: violations,
      complete: violations.length === 0
    };
  }

  /* ---------------------------------------------------------------------- *
   * 3. pricing — display total, mirroring the server's charge path
   * ---------------------------------------------------------------------- */

  function total(model, selection, branches, subscribeAll) {
    var inactive = {};
    model.exclusiveSets.forEach(function (set, i) {
      var chosen = (branches || {})[i];
      set.groupIds.forEach(function (gid) { if (gid !== chosen) inactive[gid] = true; });
    });

    // Bundle-level flat pricing collapses every layer beneath it.
    if (model.bundlePricingEnabled && model.bundleFlatPrice !== null) {
      var flat = subscribeAll && model.bundleSubscriptionPrice !== null
        ? model.bundleSubscriptionPrice
        : model.bundleFlatPrice;
      return { amount: flat, recurring: model.bundleSubscriptionPrice, mode: 'bundle_flat', cv: 0, qv: 0 };
    }

    var amount = 0, recurring = 0, cv = 0, qv = 0, anyRecurring = false;

    model.groups.forEach(function (g) {
      if (inactive[g.id]) return;

      if (g.pricingType === 'dynamic_price') {
        g.items.forEach(function (it) {
          var e = (selection || {})[key(g.id, it.variantId)];
          var qty = g.type === 'included' ? it.quantity : (e && e.qty > 0 ? e.qty : 0);
          if (!qty) return;
          amount += (it.price || 0) * qty;
          cv += it.cv * qty;
          qv += it.qv * qty;
          if ((e && e.subscribe) || it.forceSubscription || subscribeAll) {
            anyRecurring = true;
            recurring += (it.subscriptionPrice !== null ? it.subscriptionPrice : (it.price || 0)) * qty;
          }
        });
      } else {
        // fixed_price: picks and quantities never move the charge.
        if (g.fixedPrice !== null) amount += g.fixedPrice;
        g.items.forEach(function (it) {
          var e = (selection || {})[key(g.id, it.variantId)];
          var subscribed = (e && e.subscribe) || it.forceSubscription || subscribeAll;
          if (subscribed && (g.type === 'included' || (e && e.qty > 0))) {
            anyRecurring = true;
            // P7: renewal comes from the child variant's own country row, not
            // the group/bundle price. We cannot fix it — we disclose it.
            recurring += (it.subscriptionPrice || 0) * (g.type === 'included' ? it.quantity : e.qty);
          }
        });
      }
    });

    return {
      amount: amount,
      recurring: anyRecurring ? recurring : null,
      mode: 'sum',
      // CV/QV only flow from dynamic groups; never promise volume otherwise.
      cv: model.cvFlows ? cv : 0,
      qv: model.cvFlows ? qv : 0
    };
  }

  /* ---------------------------------------------------------------------- *
   * 4. cart — the money path
   * ---------------------------------------------------------------------- */

  /** Build bundled_items exactly as the server expects. */
  function buildCartPayload(model, selection, branches, subscribeAll, bundlePlanId) {
    var inExclusive = {};
    model.exclusiveSets.forEach(function (set) {
      set.groupIds.forEach(function (gid) { inExclusive[gid] = true; });
    });
    var inactive = {};
    model.exclusiveSets.forEach(function (set, i) {
      var chosen = (branches || {})[i];
      set.groupIds.forEach(function (gid) { if (gid !== chosen) inactive[gid] = true; });
    });

    var byKey = {};
    var order = [];

    function push(groupId, item, qty, subscribe, planId) {
      if (!qty || qty <= 0) return;                 // qty 0 is a delete instruction
      var k = key(groupId, item.variantId);
      if (byKey[k]) {                                // collapse duplicates into quantity
        byKey[k].quantity += qty;
        return;
      }
      var entry = {
        variant_id: item.variantId,
        quantity: qty,
        product_bundle_group_id: groupId            // ALWAYS. Never optional in practice.
      };
      if (subscribe) {
        entry.subscription = true;
        var pid = planId || item.subscriptionPlanId;
        if (pid) entry.subscription_plan_id = pid;
      }
      byKey[k] = entry;
      order.push(k);
    }

    model.groups.forEach(function (g) {
      if (inactive[g.id]) return;

      if (g.type === 'included') {
        // Included items are reconstituted server-side and must NOT be sent —
        // EXCEPT inside an exclusive set, where the server cannot know the branch.
        if (!inExclusive[g.id]) return;
        g.items.forEach(function (it) {
          push(g.id, it, it.quantity, it.forceSubscription || (subscribeAll && it.allowSubscription), null);
        });
        return;
      }

      g.items.forEach(function (it) {
        var e = (selection || {})[key(g.id, it.variantId)];
        if (!e || e.qty <= 0) return;
        var subscribe = it.forceSubscription || (!!e.subscribe && it.allowSubscription) ||
          (subscribeAll && it.allowSubscription);
        push(g.id, it, e.qty, subscribe, e.planId);
      });
    });

    var payload = {
      quantity: 1,
      bundled_items: order.map(function (k) { return byKey[k]; })
    };
    // A bundle-wide subscription is distinct from per-item and suppresses the
    // per-item forced-subscription check server-side.
    if (subscribeAll) {
      payload.subscribe = true;
      if (bundlePlanId) payload.subscription_plan_id = bundlePlanId;
    }
    return payload;
  }

  /** The SDK's methods attach asynchronously, so `typeof SDK === "object"` is
   *  not sufficient. Gate on the function itself (P17: no SDK = dead button,
   *  perfect-looking page, no console error). */
  function sdk() {
    var s = root.FairShareSDK || root.FluidCommerceSDK;
    return s && typeof s.addCartItems === 'function' ? s : null;
  }

  /** The SDK replaces the server's message with a generic string before we can
   *  see it. Capture the real body ourselves. Narrow: cart endpoints only. */
  var lastServerError = null;
  function installErrorCapture() {
    if (!root.fetch || root.__fluidBundleErrorCapture) return;
    root.__fluidBundleErrorCapture = true;
    var orig = root.fetch;
    root.fetch = function (input, init) {
      var url = typeof input === 'string' ? input : (input && input.url) || '';
      return orig.apply(this, arguments).then(function (res) {
        if (!res.ok && url.indexOf('/commerce/carts') !== -1) {
          res.clone().json().then(function (b) {
            lastServerError = (b && (b.error_message || (b.error && b.error.message))) || null;
          }).catch(function () {});
        }
        return res;
      });
    };
  }

  /** Add to cart and PROVE it. Resolves { ok, cart, line, error, skipped }. */
  function addToCart(model, payload) {
    var s = sdk();
    if (!s) {
      return Promise.resolve({ ok: false, error: 'Cart is still loading. Please try again in a moment.' });
    }
    lastServerError = null;
    var skipped = [];
    function onSkip(e) {
      var d = (e && e.detail) || {};
      if (Array.isArray(d.skipped_items)) skipped = skipped.concat(d.skipped_items);
    }
    root.addEventListener('ADD_TO_CART', onSkip);
    root.addEventListener('CREATE_CART', onSkip);

    return s.addCartItems(model.parentVariantId, payload)
      .then(function (cart) {
        root.removeEventListener('ADD_TO_CART', onSkip);
        root.removeEventListener('CREATE_CART', onSkip);

        // The promise NEVER rejects. undefined IS the failure signal.
        if (!cart) {
          return { ok: false, error: lastServerError || 'We could not add that bundle. Please review your selections.' };
        }

        var line = null;
        asArray(cart.items).forEach(function (i) {
          if (i && i.metadata && i.metadata.is_bundle && num(i.variant_id) === model.parentVariantId) line = i;
        });

        // HTTP 200 is not success: inspect per-line errors even on a resolved cart.
        if (line && asArray(line.errors).length) {
          return { ok: false, cart: cart, line: line, skipped: skipped,
            error: 'That bundle cannot be shipped to your region.' };
        }
        // A $0.00 bundle that should not be free means a child has no priced
        // country row (P6). The platform gives no other signal.
        if (line && num(line.total) === 0 && !model.expectedFree) {
          return { ok: false, cart: cart, line: line, skipped: skipped,
            error: 'Something went wrong pricing that bundle. Please try again.' };
        }
        if (skipped.length) {
          return { ok: false, cart: cart, line: line, skipped: skipped,
            error: 'Some items in that bundle are out of stock.' };
        }
        return { ok: true, cart: cart, line: line, skipped: skipped };
      });
  }

  /* ---------------------------------------------------------------------- *
   * 5. render — DOM only. Knows nothing about pricing or rules.
   * ---------------------------------------------------------------------- */

  function money(ctx, n) {
    if (n === null || n === undefined) return '';
    if (ctx.currencyCode && root.Intl && Intl.NumberFormat) {
      try {
        return new Intl.NumberFormat(ctx.locale || undefined, {
          style: 'currency', currency: ctx.currencyCode,
          minimumFractionDigits: ctx.decimalPlaces, maximumFractionDigits: ctx.decimalPlaces
        }).format(n);
      } catch (e) { /* fall through */ }
    }
    return ctx.currencySymbol + n.toFixed(ctx.decimalPlaces);
  }

  function tpl(rootEl, name) {
    var t = rootEl.querySelector('[data-bb-tpl="' + name + '"]');
    return t ? t.content.firstElementChild.cloneNode(true) : null;
  }

  function q(el, sel) { return el.querySelector(sel); }
  function qa(el, sel) { return Array.prototype.slice.call(el.querySelectorAll(sel)); }
  function setText(el, sel, text) { var n = q(el, sel); if (n) n.textContent = text; }
  function show(el, on) { if (el) el.hidden = !on; }

  /* ---------------------------------------------------------------------- *
   * 6. mount — wiring
   * ---------------------------------------------------------------------- */

  function mount(rootEl) {
    var cfgEl = q(rootEl, '[data-bb-config]');
    var prodEl = q(rootEl, '[data-bb-product]');
    if (!cfgEl || !prodEl) return;                 // not a bundle — leave the page alone

    var cfg, raw;
    try {
      cfg = JSON.parse(cfgEl.textContent);
      raw = JSON.parse(prodEl.textContent);
    } catch (e) {
      if (root.console) console.error('[bundle-builder] bad payload', e);
      return;
    }

    var ctx = {
      countryIso: upper(cfg.countryIso || 'US'),
      currencySymbol: cfg.currencySymbol || '$',
      currencyCode: cfg.currencyCode || null,
      decimalPlaces: cfg.decimalPlaces === undefined ? 2 : cfg.decimalPlaces,
      locale: cfg.locale || undefined,
      fallbackImage: cfg.fallbackImage || ''
    };

    var model = normalize(raw, ctx);
    if (!model.groups.length) return;

    if (cfg.debug && model.warnings.length && root.console) {
      model.warnings.forEach(function (w) { console.warn('[bundle-builder] ' + w); });
    }
    if (cfg.debug && model.unknownFields.length && root.console) {
      // Future platform features surface here instead of silently doing nothing.
      console.info('[bundle-builder] unrecognised fields (not rendered): ' + model.unknownFields.join(', '));
    }

    installErrorCapture();

    var selection = {};
    var branches = {};
    var subscribeAll = false;
    var bundlePlanId = null;

    // ---- defaults: clamp to max, skip out-of-stock / unavailable (P19) ----
    model.groups.forEach(function (g) {
      if (g.type !== 'customizable' || g.max === null) {
        if (g.type !== 'customizable') return;
      }
      var used = 0;
      g.items.forEach(function (it) {
        if (!it.isDefault || !it.inStock || !it.availableInCountry) return;
        var qty = Math.min(it.quantity || 1, it.maxQuantity === null ? Infinity : it.maxQuantity);
        if (g.max !== null && used + qty > g.max) return;   // never pre-select past max
        used += qty;
        selection[key(g.id, it.variantId)] = { qty: qty, subscribe: it.forceSubscription, planId: it.subscriptionPlanId };
      });
    });
    model.exclusiveSets.forEach(function (set, i) {
      if (set.defaultSortOrder !== null) {
        var g = model.groups.filter(function (gg) { return gg.sortOrder === set.defaultSortOrder; })[0];
        if (g) branches[i] = g.id;
      }
    });

    var groupsHost = q(rootEl, '[data-bb-groups]');
    var groupEls = {};

    // ---- build the grids (group shells are server-rendered) ----
    model.groups.forEach(function (g) {
      var gEl = q(rootEl, '[data-bb-group="' + g.id + '"]');
      if (!gEl && groupsHost) {
        gEl = tpl(rootEl, 'group');
        if (!gEl) return;
        gEl.setAttribute('data-bb-group', g.id);
        groupsHost.appendChild(gEl);
      }
      if (!gEl) return;
      groupEls[g.id] = gEl;
      gEl.setAttribute('data-bb-group-type', g.type);

      setText(gEl, '[data-bb-group-title]', g.title);
      var desc = q(gEl, '[data-bb-group-desc]');
      if (desc) { desc.textContent = g.description; show(desc, !!g.description); }

      var grid = q(gEl, '[data-bb-grid]');
      if (grid && g.type === 'customizable') {
        grid.innerHTML = '';
        g.items.forEach(function (it) { grid.appendChild(buildCard(g, it)); });
      }

      var choose = q(gEl, '[data-bb-choose]');
      var setIndex = -1;
      model.exclusiveSets.forEach(function (s, i) { if (s.groupIds.indexOf(g.id) !== -1) setIndex = i; });
      show(choose, setIndex !== -1);
      if (choose && setIndex !== -1) {
        choose.addEventListener('click', function () {
          branches[setIndex] = g.id;
          // Switching a branch clears the sibling's selections atomically.
          model.exclusiveSets[setIndex].groupIds.forEach(function (gid) {
            if (gid === g.id) return;
            Object.keys(selection).forEach(function (k) {
              if (k.indexOf(gid + ':') === 0) delete selection[k];
            });
          });
          update();
        });
      }
    });

    function buildCard(g, it) {
      var card = tpl(rootEl, 'card');
      card.setAttribute('data-bb-variant', it.variantId);
      card.setAttribute('data-bb-card-group', g.id);

      var img = q(card, '[data-bb-card-image]');
      var ph = q(card, '[data-bb-card-placeholder]');
      if (it.image && img) { img.src = it.image; img.alt = it.title; show(img, true); show(ph, false); }
      else { show(img, false); show(ph, true); }

      setText(card, '[data-bb-card-title]', it.title);
      var vt = q(card, '[data-bb-card-variant]');
      if (vt) { vt.textContent = it.variantTitle; show(vt, !!it.variantTitle); }

      var priceEl = q(card, '[data-bb-card-price]');
      if (priceEl) {
        // A fixed_price group's item prices are display noise — the pick never
        // moves the charge, so showing them is a lie.
        var showPrice = g.pricingType === 'dynamic_price' && !model.bundlePricingEnabled && it.price;
        priceEl.textContent = showPrice ? '+' + money(ctx, it.price) : '';
        show(priceEl, !!showPrice);
      }
      var cmpEl = q(card, '[data-bb-card-compare]');
      if (cmpEl) {
        var showCmp = g.pricingType === 'dynamic_price' && !model.bundlePricingEnabled && it.comparePrice;
        cmpEl.textContent = showCmp ? money(ctx, it.comparePrice) : '';
        show(cmpEl, !!showCmp);
      }

      var sub = q(card, '[data-bb-card-subscribe]');
      show(sub, it.allowSubscription || it.forceSubscription);
      if (sub) {
        var box = q(sub, 'input');
        if (box) {
          box.checked = it.forceSubscription;
          box.disabled = it.forceSubscription;
          box.addEventListener('change', function () {
            var e = selection[key(g.id, it.variantId)];
            if (e) { e.subscribe = box.checked; update(); }
          });
        }
        var lbl = q(sub, '[data-bb-card-subscribe-label]');
        if (lbl) lbl.textContent = it.forceSubscription ? 'Subscription required' : 'Subscribe & save';
      }

      var toggle = q(card, '[data-bb-toggle]');
      var stepper = q(card, '[data-bb-stepper]');
      var maxQty = it.maxQuantity === null ? Infinity : it.maxQuantity;

      if (toggle) {
        toggle.addEventListener('click', function () {
          var k = key(g.id, it.variantId);
          var st = rules(model, selection, branches).perGroup[g.id];
          if (selection[k]) { delete selection[k]; update(); return; }
          if (!it.inStock || !it.availableInCountry) return;
          // At max: swap out the oldest pick rather than silently ignoring the
          // click (P15 — the single biggest source of support tickets).
          if (st && st.atMax) {
            if (g.max === 1) {
              Object.keys(selection).forEach(function (kk) {
                if (kk.indexOf(g.id + ':') === 0) delete selection[kk];
              });
            } else { return; }
          }
          selection[k] = { qty: Math.min(it.quantity || 1, maxQty), subscribe: it.forceSubscription, planId: it.subscriptionPlanId };
          update();
        });
      }
      if (stepper) {
        var minus = q(stepper, '[data-bb-minus]');
        var plus = q(stepper, '[data-bb-plus]');
        if (minus) minus.addEventListener('click', function () {
          var e = selection[key(g.id, it.variantId)];
          if (!e) return;
          e.qty -= 1;
          if (e.qty <= 0) delete selection[key(g.id, it.variantId)];
          update();
        });
        if (plus) plus.addEventListener('click', function () {
          var e = selection[key(g.id, it.variantId)];
          var st = rules(model, selection, branches).perGroup[g.id];
          if (!e) return;
          if (e.qty + 1 > maxQty) return;
          if (st && g.max !== null && st.count + 1 > g.max) return;
          e.qty += 1;
          update();
        });
      }
      return card;
    }

    // ---- summary / CTA refs ----
    var summaryHost = q(rootEl, '[data-bb-summary-items]');
    var totalEl = q(rootEl, '[data-bb-total]');
    var recurringEl = q(rootEl, '[data-bb-recurring]');
    var cta = q(rootEl, '[data-bb-cta]');
    var msgEl = q(rootEl, '[data-bb-message]');
    var errEl = q(rootEl, '[data-bb-error]');
    var subAllEl = q(rootEl, '[data-bb-subscribe-all]');
    var planSel = q(rootEl, '[data-bb-plan-select]');

    if (subAllEl) {
      var subAllBox = q(subAllEl, 'input');
      show(subAllEl, model.subscriptionPlans.length > 0);
      if (subAllBox) subAllBox.addEventListener('change', function () {
        subscribeAll = subAllBox.checked; update();
      });
    }
    if (planSel) {
      planSel.innerHTML = '';
      model.subscriptionPlans.forEach(function (p) {
        var o = document.createElement('option');
        o.value = p.id; o.textContent = p.name;
        if (p['default'] || p.selected) { o.selected = true; bundlePlanId = num(p.id); }
        planSel.appendChild(o);
      });
      // Multi-plan selection is unproven upstream — hide it rather than fake it.
      show(planSel, model.subscriptionPlans.length > 1);
      planSel.addEventListener('change', function () { bundlePlanId = num(planSel.value); update(); });
    }

    function update() {
      var r = rules(model, selection, branches);
      var t = total(model, selection, branches, subscribeAll);

      model.groups.forEach(function (g) {
        var gEl = groupEls[g.id];
        if (!gEl) return;
        var st = r.perGroup[g.id] || {};
        gEl.classList.toggle('is-inactive', !!st.inactive);
        gEl.classList.toggle('is-complete', !!st.satisfied && g.type === 'customizable' && st.count > 0);

        var tracker = q(gEl, '[data-bb-tracker]');
        if (tracker) {
          var showTracker = g.type === 'customizable' && g.max !== null && cfg.showProgress !== false;
          show(tracker, showTracker);
          if (showTracker) {
            setText(tracker, '[data-bb-tracker-label]', st.count + ' / ' + g.max);
            var fill = q(tracker, '[data-bb-tracker-fill]');
            if (fill) fill.style.width = Math.min(100, (st.count / g.max) * 100) + '%';
            tracker.setAttribute('aria-valuenow', st.count);
            tracker.setAttribute('aria-valuemax', g.max);
          }
        }

        var rule = q(gEl, '[data-bb-rule]');
        if (rule) {
          var text = '';
          if (g.type === 'customizable' && !g.configError) {
            if (g.selectionType === 'exact') text = 'Choose ' + g.min;
            else if (g.selectionType === 'min_only') text = 'Choose at least ' + g.min;
            else if (g.selectionType === 'max_only') text = 'Choose up to ' + g.max + ' (optional)';
            else if (g.min > 0) text = 'Choose ' + g.min + '–' + g.max;
            else text = 'Choose up to ' + g.max;
          }
          rule.textContent = text;
          show(rule, !!text);
        }

        var choose = q(gEl, '[data-bb-choose]');
        if (choose && !choose.hidden) {
          var active = !st.inactive;
          choose.setAttribute('aria-pressed', active ? 'true' : 'false');
          setText(choose, '[data-bb-choose-label]', active ? 'Selected' : 'Choose this');
        }

        qa(gEl, '[data-bb-variant]').forEach(function (card) {
          var vid = num(card.getAttribute('data-bb-variant'));
          var it = g.items.filter(function (x) { return x.variantId === vid; })[0];
          if (!it) return;
          var e = selection[key(g.id, vid)];
          var selected = !!e;
          card.classList.toggle('is-selected', selected);
          card.setAttribute('aria-checked', selected ? 'true' : 'false');

          var unavailable = !it.inStock || !it.availableInCountry;
          // At max with nothing selected here: a real disabled affordance with a
          // reason, never a live-looking button that silently ignores clicks.
          var blocked = !selected && st.atMax && g.max !== 1;
          card.classList.toggle('is-unavailable', unavailable);
          card.classList.toggle('is-blocked', !!blocked);
          card.setAttribute('aria-disabled', (unavailable || blocked) ? 'true' : 'false');

          var t2 = q(card, '[data-bb-toggle]');
          if (t2) {
            t2.disabled = unavailable || blocked;
            setText(card, '[data-bb-toggle-label]',
              unavailable ? (it.inStock ? 'Unavailable in your region' : 'Out of stock')
                : blocked ? 'Remove one to choose another'
                  : selected ? 'Selected' : 'Add');
          }
          var stepEl = q(card, '[data-bb-stepper]');
          show(stepEl, selected && (it.maxQuantity === null || it.maxQuantity > 1));
          if (selected && stepEl) setText(stepEl, '[data-bb-qty]', String(e.qty));
        });
      });

      // ---- summary ----
      if (summaryHost) {
        summaryHost.innerHTML = '';
        model.groups.forEach(function (g) {
          var st = r.perGroup[g.id] || {};
          if (st.inactive) return;
          g.items.forEach(function (it) {
            var e = selection[key(g.id, it.variantId)];
            var qty = g.type === 'included' ? it.quantity : (e ? e.qty : 0);
            if (!qty) return;
            var row = tpl(rootEl, 'summary-row');
            if (!row) return;
            setText(row, '[data-bb-sum-title]', it.title);
            setText(row, '[data-bb-sum-qty]', qty > 1 ? '×' + qty : '');
            var p = q(row, '[data-bb-sum-price]');
            if (p) {
              var showP = g.pricingType === 'dynamic_price' && !model.bundlePricingEnabled && it.price;
              p.textContent = showP ? money(ctx, it.price * qty) : '';
            }
            var b = q(row, '[data-bb-sum-badge]');
            if (b) {
              var subbed = (e && e.subscribe) || it.forceSubscription || subscribeAll;
              b.textContent = subbed ? 'Subscription' : '';
              show(b, !!subbed);
            }
            summaryHost.appendChild(row);
          });
        });
      }

      if (totalEl) totalEl.textContent = money(ctx, t.amount);
      if (recurringEl) {
        // P7/P10: renewal can differ wildly from the first charge and the
        // platform first reveals it at checkout. Disclose it here.
        var showRec = cfg.showRecurring !== false && t.recurring !== null && t.recurring > 0;
        recurringEl.textContent = showRec ? 'Then ' + money(ctx, t.recurring) + ' per renewal' : '';
        show(recurringEl, showRec);
      }

      if (cta) cta.disabled = !r.complete;
      if (msgEl) {
        var first = r.violations[0];
        msgEl.textContent = first ? first.message : '';
        show(msgEl, !!first);
      }
      if (errEl && errEl.dataset.sticky !== 'true') show(errEl, false);
    }

    if (cta) {
      cta.addEventListener('click', function () {
        var r = rules(model, selection, branches);
        if (!r.complete) { update(); return; }
        var payload = buildCartPayload(model, selection, branches, subscribeAll, bundlePlanId);
        model.expectedFree = total(model, selection, branches, subscribeAll).amount === 0;

        cta.disabled = true;
        cta.classList.add('is-loading');
        addToCart(model, payload).then(function (res) {
          cta.classList.remove('is-loading');
          cta.disabled = false;
          if (!res.ok) {
            if (errEl) { errEl.textContent = res.error; errEl.dataset.sticky = 'true'; show(errEl, true); }
            if (root.console) console.error('[bundle-builder] add failed', res);
            return;
          }
          if (errEl) { errEl.dataset.sticky = 'false'; show(errEl, false); }
          var s = sdk();
          if (s && s.cart && s.cart.control && s.cart.control.open) s.cart.control.open();
        });
      });
    }

    update();
    rootEl.setAttribute('data-bb-ready', 'true');
  }

  function boot() {
    Array.prototype.slice.call(document.querySelectorAll('[data-bb-root]')).forEach(mount);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  root.FluidBundleBuilder = {
    normalize: normalize,
    rules: rules,
    total: total,
    buildCartPayload: buildCartPayload,
    addToCart: addToCart,
    mount: mount
  };
})(window);
