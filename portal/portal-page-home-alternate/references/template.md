# `component_tree` — Home v3 (alternate)

Post this as the screen's `component_tree` on the PUT, exactly as written —
it is already the array form the endpoint expects. Do not add another
wrapping array, and do not lift the single top-level LayoutWidget out of it:
that node is the page wrapper the live portal needs.
Placeholders are listed in the skill body; replace them before publishing.

```json
[
  {
    "id": "PageWrap-v3",
    "type": "LayoutWidget",
    "props": {
      "gapSize": "none",
      "padding": 0,
      "children": [
        {
          "id": "CarouselWidget-v3-hero",
          "type": "CarouselWidget",
          "props": {
            "align": {
              "vertical": "bottom",
              "horizontal": "left"
            },
            "slides": [
              {
                "id": "CarouselWidget-v3-hero-s",
                "title": "Give a friend $10. Get $10 back.",
                "content": {
                  "type": "ImageWidget",
                  "props": {
                    "alt": "Three [Brand] members receiving a warm welcome around the platform",
                    "src": "https://picsum.photos/seed/img37/1200/1500",
                    "displayFit": "cover",
                    "focusPoint": "center",
                    "useCustomUrl": true
                  }
                },
                "eyebrow": "REFER A FRIEND",
                "buttonLink": "/friend-share",
                "buttonText": "Share & get $10",
                "description": "Send your link. They save <strong>$10</strong> on their first order \u2014 you get <strong>$10</strong> when they buy.",
                "buttonEnabled": true,
                "secondaryButtonLink": "/friend-share",
                "secondaryButtonText": "How it works"
              }
            ],
            "padding": 10,
            "textSize": "md",
            "className": "mb-8",
            "textColor": "background",
            "textWidth": "560px",
            "buttonSize": "lg",
            "frameColor": "foreground",
            "headerSize": "2xl",
            "showButton": true,
            "borderWidth": "none",
            "buttonColor": "background",
            "headerColor": "background",
            "overlayType": "gradient",
            "borderRadius": "none",
            "carouselHeight": "460px",
            "editorialFrame": true,
            "overlayEnabled": true,
            "enableAutoScroll": false,
            "overlayIntensity": 68
          },
          "columnIndex": 0
        },
        {
          "id": "LayoutWidget-v3-row2",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "lg",
            "padding": 0,
            "children": [
              {
                "id": "lbl-v3-link",
                "type": "TextWidget",
                "props": {
                  "title": "Your referral link",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "background",
                  "borderWidth": "none",
                  "description": "Send it \u2014 they save $10, you get $10.",
                  "borderRadius": "none",
                  "titleFontSize": "lg",
                  "titleFontWeight": "bold",
                  "descriptionColor": "background",
                  "descriptionFontSize": "sm",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 0
              },
              {
                "id": "QuickShareWidget-v3",
                "type": "QuickShareWidget",
                "props": {
                  "padding": 5,
                  "titleText": "Refer a friend",
                  "background": {
                    "type": "color",
                    "color": "foreground"
                  },
                  "accentColor": "background",
                  "borderColor": "muted",
                  "borderWidth": "none",
                  "overlayType": "gradient",
                  "borderRadius": "xl",
                  "buyButtonLink": "REPLACE_TARGET_URL",
                  "buyButtonText": "View Product",
                  "showBuyButton": false,
                  "overlayEnabled": true,
                  "overlayIntensity": 50,
                  "showDomainPrefix": true,
                  "showResourceType": true,
                  "showShareActions": true,
                  "shareableResource": {
                    "id": "REPLACE_PRODUCT_ID",
                    "name": "Featured Product 16",
                    "slug": "US-kit-beauty-focus-collagen-plus-ageloc-youth-ageloc-meta-nu-biome-subscription-kit-US",
                    "type": "Product",
                    "price": "$00.00",
                    "title": "Featured Product 16",
                    "images": [
                      {
                        "alt": "Refer a friend",
                        "url": "https://picsum.photos/seed/img03/1200/1500"
                      }
                    ],
                    "status": "active",
                    "imageUrl": "https://picsum.photos/seed/img03/1200/1500",
                    "image_url": "https://picsum.photos/seed/img03/1200/1500",
                    "shareLink": "REPLACE_TARGET_URL",
                    "productUrl": "REPLACE_TARGET_URL",
                    "share_link": "REPLACE_TARGET_URL",
                    "description": "One-line product description goes here.",
                    "product_url": "REPLACE_TARGET_URL",
                    "display_price": "$00.00",
                    "shareableType": "Product",
                    "shareable_type": "Product"
                  }
                },
                "columnIndex": 0
              },
              {
                "id": "CardWidget-v3-who",
                "type": "TextWidget",
                "props": {
                  "title": "Who to send it to",
                  "padding": 6,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "background",
                  "borderWidth": "none",
                  "description": "A friend chasing energy, someone who can\u2019t switch off at night, or anyone curious about wellness.",
                  "borderRadius": "xl",
                  "titleFontSize": "lg",
                  "titleFontWeight": "semibold",
                  "descriptionColor": "background",
                  "descriptionFontSize": "sm",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 0
              },
              {
                "id": "QuickLinksWidget-v3-share",
                "type": "QuickLinksWidget",
                "props": {
                  "title": "Your share kit",
                  "layout": "list",
                  "padding": 5,
                  "link1Url": "/the-hub",
                  "link2Url": "/my-site",
                  "link3Url": "/friend-share",
                  "link1Icon": "BookOpen",
                  "link2Icon": "Globe",
                  "link3Icon": "Gift",
                  "textColor": "background",
                  "background": {
                    "type": "color",
                    "color": "transparent"
                  },
                  "iconRadius": "none",
                  "link1Color": "accent",
                  "link1Label": "Social media kit",
                  "link2Color": "accent",
                  "link2Label": "My [Brand] site",
                  "link3Color": "accent",
                  "link3Label": "Friend Share page",
                  "borderWidth": "none",
                  "borderRadius": "xl",
                  "link2Enabled": true,
                  "link3Enabled": true,
                  "link4Enabled": false,
                  "link5Enabled": false,
                  "link6Enabled": false,
                  "link7Enabled": false,
                  "link8Enabled": false,
                  "openInNewTab": false
                },
                "columnIndex": 0
              },
              {
                "id": "lbl-v3-film",
                "type": "TextWidget",
                "props": {
                  "title": "Content to send",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "background",
                  "borderWidth": "none",
                  "description": "Two films and a caption, ready to go.",
                  "borderRadius": "none",
                  "titleFontSize": "lg",
                  "titleFontWeight": "bold",
                  "descriptionColor": "background",
                  "descriptionFontSize": "sm",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 1
              },
              {
                "id": "VideoWidget-v3-film",
                "type": "VideoWidget",
                "props": {
                  "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                  "tag": "BRAND FILM",
                  "title": "The [Brand] story in 90 seconds",
                  "poster": "https://picsum.photos/seed/img19/1200/1500",
                  "eyebrow": "WATCH",
                  "tagline": "The one to send first.",
                  "frameColor": "foreground",
                  "displayMode": "card",
                  "borderRadius": "xl",
                  "useCustomUrl": true,
                  "editorialFrame": true,
                  "showFullscreenPill": true
                },
                "columnIndex": 1
              },
              {
                "id": "VideoWidget-v3-cso",
                "type": "VideoWidget",
                "props": {
                  "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                  "tag": "THE SCIENCE",
                  "title": "The science behind [science]",
                  "poster": "https://picsum.photos/seed/img02/1200/1500",
                  "eyebrow": "WATCH",
                  "tagline": "From our Chief Science Officer.",
                  "frameColor": "foreground",
                  "displayMode": "card",
                  "borderRadius": "xl",
                  "useCustomUrl": true,
                  "editorialFrame": true,
                  "showFullscreenPill": true
                },
                "columnIndex": 1
              },
              {
                "id": "CardWidget-v3-caption",
                "type": "TextWidget",
                "props": {
                  "title": "A caption to copy",
                  "padding": 6,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "background",
                  "borderWidth": "none",
                  "description": "\u201cObsessed with how I feel on [Brand] \u2014 science-backed peptides for energy, focus, and sleep. Want my link?\u201d",
                  "borderRadius": "xl",
                  "titleFontSize": "lg",
                  "titleFontWeight": "semibold",
                  "descriptionColor": "background",
                  "descriptionFontSize": "sm",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 1
              },
              {
                "id": "lbl-v3-save",
                "type": "TextWidget",
                "props": {
                  "title": "Ways to save",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "background",
                  "borderWidth": "none",
                  "description": "Use them \u2014 and pass them on.",
                  "borderRadius": "none",
                  "titleFontSize": "lg",
                  "titleFontWeight": "bold",
                  "descriptionColor": "background",
                  "descriptionFontSize": "sm",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 2
              },
              {
                "id": "CardWidget-v3-give",
                "type": "TextWidget",
                "props": {
                  "title": "Give $10, Get $10",
                  "padding": 6,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "background",
                  "borderWidth": "none",
                  "description": "Every friend who orders puts $10 in your pocket \u2014 and $10 off theirs.",
                  "borderRadius": "xl",
                  "titleFontSize": "lg",
                  "titleFontWeight": "semibold",
                  "descriptionColor": "background",
                  "descriptionFontSize": "sm",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 2
              },
              {
                "id": "CardWidget-v3-sub",
                "type": "TextWidget",
                "props": {
                  "title": "Subscribe & Save",
                  "padding": 6,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "background",
                  "borderWidth": "none",
                  "description": "Lock in member pricing on the routines you reorder.",
                  "borderRadius": "xl",
                  "titleFontSize": "lg",
                  "titleFontWeight": "semibold",
                  "descriptionColor": "background",
                  "descriptionFontSize": "sm",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 2
              },
              {
                "id": "QuickLinksWidget-v3",
                "type": "QuickLinksWidget",
                "props": {
                  "title": "Deals & sharing",
                  "layout": "list",
                  "padding": 5,
                  "link1Url": "/friend-share",
                  "link2Url": "/subscription-discounts",
                  "link3Url": "/shop",
                  "link1Icon": "Gift",
                  "link2Icon": "BadgePercent",
                  "link3Icon": "ShoppingBag",
                  "textColor": "background",
                  "background": {
                    "type": "color",
                    "color": "transparent"
                  },
                  "iconRadius": "none",
                  "link1Color": "accent",
                  "link1Label": "Refer a friend",
                  "link2Color": "accent",
                  "link2Label": "Subscription discounts",
                  "link3Color": "accent",
                  "link3Label": "Shop the line",
                  "borderWidth": "none",
                  "borderRadius": "xl",
                  "link2Enabled": true,
                  "link3Enabled": true,
                  "link4Enabled": false,
                  "link5Enabled": false,
                  "link6Enabled": false,
                  "link7Enabled": false,
                  "link8Enabled": false,
                  "openInNewTab": false
                },
                "columnIndex": 2
              }
            ],
            "className": "px-6 sm:px-10 mb-8",
            "background": {
              "type": "solid",
              "color": "transparent"
            },
            "borderWidth": "none",
            "borderRadius": "xl",
            "sectionLayout": "3c-equal"
          },
          "columnIndex": 0
        },
        {
          "id": "LayoutWidget-v3-proof",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "sm",
            "padding": 0,
            "children": [
              {
                "id": "LayoutWidget-v3-proof-band",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "md",
                  "padding": 4,
                  "children": [
                    {
                      "id": "LayoutWidget-v3-proof-h",
                      "type": "TextWidget",
                      "props": {
                        "title": "Real people. Real routines. Real results.",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "description": "Six honest product moments from the community \u2014 watch, learn, and share what feels true to you.",
                        "borderRadius": "none",
                        "titleFontSize": "2xl",
                        "titleFontWeight": "bold",
                        "descriptionColor": "foreground",
                        "descriptionFontSize": "sm",
                        "descriptionFontWeight": "normal"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "LayoutWidget-v3-proof-grid",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "sm",
                        "padding": 0,
                        "children": [
                          {
                            "id": "v3-ugc-group-1",
                            "type": "LayoutWidget",
                            "props": {
                              "gapSize": "sm",
                              "padding": 0,
                              "children": [
                                {
                                  "id": "v3-ugc-card-1",
                                  "type": "LayoutWidget",
                                  "props": {
                                    "gapSize": "xs",
                                    "padding": 0,
                                    "children": [
                                      {
                                        "id": "v3-ugc-video-1",
                                        "type": "VideoWidget",
                                        "props": {
                                          "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                                          "tag": "UGC",
                                          "date": "",
                                          "loop": false,
                                          "muted": true,
                                          "title": "",
                                          "author": "",
                                          "poster": "https://picsum.photos/seed/img04/1200/1500",
                                          "eyebrow": "REAL ROUTINE 01",
                                          "tagline": "",
                                          "autoplay": false,
                                          "controls": true,
                                          "duration": "",
                                          "displayFit": "cover",
                                          "focusPoint": "center",
                                          "frameColor": "foreground",
                                          "borderColor": "muted",
                                          "borderWidth": "none",
                                          "displayMode": "inline",
                                          "fixedHeight": "400px",
                                          "borderRadius": "lg",
                                          "useCustomUrl": true,
                                          "editorialFrame": false,
                                          "primaryCtaLink": "",
                                          "primaryCtaText": "",
                                          "verticalSizing": "fixed",
                                          "secondaryCtaLink": "",
                                          "secondaryCtaText": "",
                                          "showFullscreenPill": false
                                        },
                                        "columnIndex": 0
                                      },
                                      {
                                        "id": "v3-ugc-caption-1",
                                        "type": "TextWidget",
                                        "props": {
                                          "title": "The device inside my routine",
                                          "padding": 0,
                                          "background": {
                                            "type": "solid",
                                            "color": "transparent"
                                          },
                                          "titleColor": "foreground",
                                          "borderWidth": "none",
                                          "description": "A close-up, unfiltered [the device] moment.",
                                          "borderRadius": "none",
                                          "titleEnabled": true,
                                          "titleFontSize": "sm",
                                          "titleAlignment": "left",
                                          "titleFontWeight": "semibold",
                                          "descriptionColor": "mutedForeground",
                                          "descriptionFontSize": "xs",
                                          "descriptionAlignment": "left",
                                          "descriptionFontWeight": "normal"
                                        },
                                        "columnIndex": 0
                                      }
                                    ],
                                    "background": {
                                      "type": "solid",
                                      "color": "transparent"
                                    },
                                    "borderColor": "muted",
                                    "borderWidth": "none",
                                    "borderRadius": "none",
                                    "sectionLayout": "single-column"
                                  },
                                  "columnIndex": 0
                                },
                                {
                                  "id": "v3-ugc-card-2",
                                  "type": "LayoutWidget",
                                  "props": {
                                    "gapSize": "xs",
                                    "padding": 0,
                                    "children": [
                                      {
                                        "id": "v3-ugc-video-2",
                                        "type": "VideoWidget",
                                        "props": {
                                          "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                                          "tag": "UGC",
                                          "date": "",
                                          "loop": false,
                                          "muted": true,
                                          "title": "",
                                          "author": "",
                                          "poster": "https://picsum.photos/seed/img05/1200/1500",
                                          "eyebrow": "REAL ROUTINE 02",
                                          "tagline": "",
                                          "autoplay": false,
                                          "controls": true,
                                          "duration": "",
                                          "displayFit": "cover",
                                          "focusPoint": "center",
                                          "frameColor": "foreground",
                                          "borderColor": "muted",
                                          "borderWidth": "none",
                                          "displayMode": "inline",
                                          "fixedHeight": "400px",
                                          "borderRadius": "lg",
                                          "useCustomUrl": true,
                                          "editorialFrame": false,
                                          "primaryCtaLink": "",
                                          "primaryCtaText": "",
                                          "verticalSizing": "fixed",
                                          "secondaryCtaLink": "",
                                          "secondaryCtaText": "",
                                          "showFullscreenPill": false
                                        },
                                        "columnIndex": 0
                                      },
                                      {
                                        "id": "v3-ugc-caption-2",
                                        "type": "TextWidget",
                                        "props": {
                                          "title": "The ritual I return to",
                                          "padding": 0,
                                          "background": {
                                            "type": "solid",
                                            "color": "transparent"
                                          },
                                          "titleColor": "foreground",
                                          "borderWidth": "none",
                                          "description": "Why consistency beats a perfect routine.",
                                          "borderRadius": "none",
                                          "titleEnabled": true,
                                          "titleFontSize": "sm",
                                          "titleAlignment": "left",
                                          "titleFontWeight": "semibold",
                                          "descriptionColor": "mutedForeground",
                                          "descriptionFontSize": "xs",
                                          "descriptionAlignment": "left",
                                          "descriptionFontWeight": "normal"
                                        },
                                        "columnIndex": 0
                                      }
                                    ],
                                    "background": {
                                      "type": "solid",
                                      "color": "transparent"
                                    },
                                    "borderColor": "muted",
                                    "borderWidth": "none",
                                    "borderRadius": "none",
                                    "sectionLayout": "single-column"
                                  },
                                  "columnIndex": 1
                                },
                                {
                                  "id": "v3-ugc-card-3",
                                  "type": "LayoutWidget",
                                  "props": {
                                    "gapSize": "xs",
                                    "padding": 0,
                                    "children": [
                                      {
                                        "id": "v3-ugc-video-3",
                                        "type": "VideoWidget",
                                        "props": {
                                          "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                                          "tag": "UGC",
                                          "date": "",
                                          "loop": false,
                                          "muted": true,
                                          "title": "",
                                          "author": "",
                                          "poster": "https://picsum.photos/seed/img06/1200/1500",
                                          "eyebrow": "REAL ROUTINE 03",
                                          "tagline": "",
                                          "autoplay": false,
                                          "controls": true,
                                          "duration": "",
                                          "displayFit": "cover",
                                          "focusPoint": "center",
                                          "frameColor": "foreground",
                                          "borderColor": "muted",
                                          "borderWidth": "none",
                                          "displayMode": "inline",
                                          "fixedHeight": "400px",
                                          "borderRadius": "lg",
                                          "useCustomUrl": true,
                                          "editorialFrame": false,
                                          "primaryCtaLink": "",
                                          "primaryCtaText": "",
                                          "verticalSizing": "fixed",
                                          "secondaryCtaLink": "",
                                          "secondaryCtaText": "",
                                          "showFullscreenPill": false
                                        },
                                        "columnIndex": 0
                                      },
                                      {
                                        "id": "v3-ugc-caption-3",
                                        "type": "TextWidget",
                                        "props": {
                                          "title": "Two minutes every morning",
                                          "padding": 0,
                                          "background": {
                                            "type": "solid",
                                            "color": "transparent"
                                          },
                                          "titleColor": "foreground",
                                          "borderWidth": "none",
                                          "description": "A routine that fits real life.",
                                          "borderRadius": "none",
                                          "titleEnabled": true,
                                          "titleFontSize": "sm",
                                          "titleAlignment": "left",
                                          "titleFontWeight": "semibold",
                                          "descriptionColor": "mutedForeground",
                                          "descriptionFontSize": "xs",
                                          "descriptionAlignment": "left",
                                          "descriptionFontWeight": "normal"
                                        },
                                        "columnIndex": 0
                                      }
                                    ],
                                    "background": {
                                      "type": "solid",
                                      "color": "transparent"
                                    },
                                    "borderColor": "muted",
                                    "borderWidth": "none",
                                    "borderRadius": "none",
                                    "sectionLayout": "single-column"
                                  },
                                  "columnIndex": 2
                                }
                              ],
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "borderRadius": "none",
                              "sectionLayout": "3c-equal"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "v3-ugc-group-2",
                            "type": "LayoutWidget",
                            "props": {
                              "gapSize": "sm",
                              "padding": 0,
                              "children": [
                                {
                                  "id": "v3-ugc-card-4",
                                  "type": "LayoutWidget",
                                  "props": {
                                    "gapSize": "xs",
                                    "padding": 0,
                                    "children": [
                                      {
                                        "id": "v3-ugc-video-4",
                                        "type": "VideoWidget",
                                        "props": {
                                          "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                                          "tag": "UGC",
                                          "date": "",
                                          "loop": false,
                                          "muted": true,
                                          "title": "",
                                          "author": "",
                                          "poster": "https://picsum.photos/seed/img07/1200/1500",
                                          "eyebrow": "REAL ROUTINE 04",
                                          "tagline": "",
                                          "autoplay": false,
                                          "controls": true,
                                          "duration": "",
                                          "displayFit": "cover",
                                          "focusPoint": "center",
                                          "frameColor": "foreground",
                                          "borderColor": "muted",
                                          "borderWidth": "none",
                                          "displayMode": "inline",
                                          "fixedHeight": "400px",
                                          "borderRadius": "lg",
                                          "useCustomUrl": true,
                                          "editorialFrame": false,
                                          "primaryCtaLink": "",
                                          "primaryCtaText": "",
                                          "verticalSizing": "fixed",
                                          "secondaryCtaLink": "",
                                          "secondaryCtaText": "",
                                          "showFullscreenPill": false
                                        },
                                        "columnIndex": 0
                                      },
                                      {
                                        "id": "v3-ugc-caption-4",
                                        "type": "TextWidget",
                                        "props": {
                                          "title": "What the clean finish feels like",
                                          "padding": 0,
                                          "background": {
                                            "type": "solid",
                                            "color": "transparent"
                                          },
                                          "titleColor": "foreground",
                                          "borderWidth": "none",
                                          "description": "The product moment people ask about.",
                                          "borderRadius": "none",
                                          "titleEnabled": true,
                                          "titleFontSize": "sm",
                                          "titleAlignment": "left",
                                          "titleFontWeight": "semibold",
                                          "descriptionColor": "mutedForeground",
                                          "descriptionFontSize": "xs",
                                          "descriptionAlignment": "left",
                                          "descriptionFontWeight": "normal"
                                        },
                                        "columnIndex": 0
                                      }
                                    ],
                                    "background": {
                                      "type": "solid",
                                      "color": "transparent"
                                    },
                                    "borderColor": "muted",
                                    "borderWidth": "none",
                                    "borderRadius": "none",
                                    "sectionLayout": "single-column"
                                  },
                                  "columnIndex": 0
                                },
                                {
                                  "id": "v3-ugc-card-5",
                                  "type": "LayoutWidget",
                                  "props": {
                                    "gapSize": "xs",
                                    "padding": 0,
                                    "children": [
                                      {
                                        "id": "v3-ugc-video-5",
                                        "type": "VideoWidget",
                                        "props": {
                                          "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                                          "tag": "UGC",
                                          "date": "",
                                          "loop": false,
                                          "muted": true,
                                          "title": "",
                                          "author": "",
                                          "poster": "https://picsum.photos/seed/img14/1200/1500",
                                          "eyebrow": "REAL ROUTINE 05",
                                          "tagline": "",
                                          "autoplay": false,
                                          "controls": true,
                                          "duration": "",
                                          "displayFit": "cover",
                                          "focusPoint": "center",
                                          "frameColor": "foreground",
                                          "borderColor": "muted",
                                          "borderWidth": "none",
                                          "displayMode": "inline",
                                          "fixedHeight": "400px",
                                          "borderRadius": "lg",
                                          "useCustomUrl": true,
                                          "editorialFrame": false,
                                          "primaryCtaLink": "",
                                          "primaryCtaText": "",
                                          "verticalSizing": "fixed",
                                          "secondaryCtaLink": "",
                                          "secondaryCtaText": "",
                                          "showFullscreenPill": false
                                        },
                                        "columnIndex": 0
                                      },
                                      {
                                        "id": "v3-ugc-caption-5",
                                        "type": "TextWidget",
                                        "props": {
                                          "title": "My no-rush skincare ritual",
                                          "padding": 0,
                                          "background": {
                                            "type": "solid",
                                            "color": "transparent"
                                          },
                                          "titleColor": "foreground",
                                          "borderWidth": "none",
                                          "description": "Slower, simple, completely achievable.",
                                          "borderRadius": "none",
                                          "titleEnabled": true,
                                          "titleFontSize": "sm",
                                          "titleAlignment": "left",
                                          "titleFontWeight": "semibold",
                                          "descriptionColor": "mutedForeground",
                                          "descriptionFontSize": "xs",
                                          "descriptionAlignment": "left",
                                          "descriptionFontWeight": "normal"
                                        },
                                        "columnIndex": 0
                                      }
                                    ],
                                    "background": {
                                      "type": "solid",
                                      "color": "transparent"
                                    },
                                    "borderColor": "muted",
                                    "borderWidth": "none",
                                    "borderRadius": "none",
                                    "sectionLayout": "single-column"
                                  },
                                  "columnIndex": 1
                                },
                                {
                                  "id": "v3-ugc-card-6",
                                  "type": "LayoutWidget",
                                  "props": {
                                    "gapSize": "xs",
                                    "padding": 0,
                                    "children": [
                                      {
                                        "id": "v3-ugc-video-6",
                                        "type": "VideoWidget",
                                        "props": {
                                          "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                                          "tag": "UGC",
                                          "date": "",
                                          "loop": false,
                                          "muted": true,
                                          "title": "",
                                          "author": "",
                                          "poster": "https://picsum.photos/seed/img15/1200/1500",
                                          "eyebrow": "REAL ROUTINE 06",
                                          "tagline": "",
                                          "autoplay": false,
                                          "controls": true,
                                          "duration": "",
                                          "displayFit": "cover",
                                          "focusPoint": "center",
                                          "frameColor": "foreground",
                                          "borderColor": "muted",
                                          "borderWidth": "none",
                                          "displayMode": "inline",
                                          "fixedHeight": "400px",
                                          "borderRadius": "lg",
                                          "useCustomUrl": true,
                                          "editorialFrame": false,
                                          "primaryCtaLink": "",
                                          "primaryCtaText": "",
                                          "verticalSizing": "fixed",
                                          "secondaryCtaLink": "",
                                          "secondaryCtaText": "",
                                          "showFullscreenPill": false
                                        },
                                        "columnIndex": 0
                                      },
                                      {
                                        "id": "v3-ugc-caption-6",
                                        "type": "TextWidget",
                                        "props": {
                                          "title": "What consistency changed",
                                          "padding": 0,
                                          "background": {
                                            "type": "solid",
                                            "color": "transparent"
                                          },
                                          "titleColor": "foreground",
                                          "borderWidth": "none",
                                          "description": "A straightforward story about staying with it.",
                                          "borderRadius": "none",
                                          "titleEnabled": true,
                                          "titleFontSize": "sm",
                                          "titleAlignment": "left",
                                          "titleFontWeight": "semibold",
                                          "descriptionColor": "mutedForeground",
                                          "descriptionFontSize": "xs",
                                          "descriptionAlignment": "left",
                                          "descriptionFontWeight": "normal"
                                        },
                                        "columnIndex": 0
                                      }
                                    ],
                                    "background": {
                                      "type": "solid",
                                      "color": "transparent"
                                    },
                                    "borderColor": "muted",
                                    "borderWidth": "none",
                                    "borderRadius": "none",
                                    "sectionLayout": "single-column"
                                  },
                                  "columnIndex": 2
                                }
                              ],
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "borderRadius": "none",
                              "sectionLayout": "3c-equal"
                            },
                            "columnIndex": 1
                          }
                        ],
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "borderColor": "muted",
                        "borderWidth": "none",
                        "borderRadius": "none",
                        "sectionLayout": "2c-equal"
                      },
                      "columnIndex": 0
                    }
                  ],
                  "background": {
                    "type": "solid",
                    "color": "secondary"
                  },
                  "borderWidth": "none",
                  "borderRadius": "xl",
                  "sectionLayout": "single-column"
                },
                "columnIndex": 0
              }
            ],
            "className": "px-6 sm:px-10 mb-8",
            "background": {
              "type": "solid",
              "color": "transparent"
            },
            "borderWidth": "none",
            "borderRadius": "none",
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        },
        {
          "id": "ListWidget-v3-content-h",
          "type": "TextWidget",
          "props": {
            "title": "Content ready to share",
            "padding": 0,
            "className": "px-6 sm:px-10",
            "background": {
              "type": "solid",
              "color": "transparent"
            },
            "titleColor": "background",
            "borderWidth": "none",
            "description": "Caption it, post it, drop your link.",
            "borderRadius": "none",
            "titleFontSize": "2xl",
            "titleFontWeight": "bold",
            "descriptionColor": "background",
            "descriptionFontSize": "md",
            "descriptionFontWeight": "normal"
          },
          "columnIndex": 0
        },
        {
          "id": "ListWidget-v3-content-grid",
          "type": "ListWidget",
          "props": {
            "gap": "md",
            "items": [
              {
                "id": 1025,
                "kind": "image",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img38/1200/1500",
                "title": "Media item 25",
                "imageUrl": "https://picsum.photos/seed/img38/1200/1500",
                "shareableType": "Medium",
                "shareable_type": "Medium"
              },
              {
                "id": 1026,
                "kind": "image",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img39/1200/1500",
                "title": "Media item 26",
                "imageUrl": "https://picsum.photos/seed/img39/1200/1500",
                "shareableType": "Medium",
                "shareable_type": "Medium"
              },
              {
                "id": 1027,
                "kind": "image",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img40/1200/1500",
                "title": "Media item 27",
                "imageUrl": "https://picsum.photos/seed/img40/1200/1500",
                "shareableType": "Medium",
                "shareable_type": "Medium"
              },
              {
                "id": 1028,
                "kind": "image",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img41/1200/1500",
                "title": "Media item 28",
                "imageUrl": "https://picsum.photos/seed/img41/1200/1500",
                "shareableType": "Medium",
                "shareable_type": "Medium"
              },
              {
                "id": 1029,
                "kind": "image",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img28/1200/1500",
                "title": "Media item 29",
                "imageUrl": "https://picsum.photos/seed/img28/1200/1500",
                "shareableType": "Medium",
                "shareable_type": "Medium"
              },
              {
                "id": 1030,
                "kind": "image",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img42/1200/1500",
                "title": "Media item 30",
                "imageUrl": "https://picsum.photos/seed/img42/1200/1500",
                "shareableType": "Medium",
                "shareable_type": "Medium"
              },
              {
                "id": 1031,
                "kind": "image",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img43/1200/1500",
                "title": "Media item 31",
                "imageUrl": "https://picsum.photos/seed/img43/1200/1500",
                "shareableType": "Medium",
                "shareable_type": "Medium"
              }
            ],
            "title": "List",
            "columns": 4,
            "padding": 2,
            "listType": "unordered",
            "maxItems": 4,
            "className": "px-6 sm:px-10 mb-8",
            "priceSize": "md",
            "showBadge": false,
            "titleSize": "xl",
            "background": {
              "type": "solid",
              "color": "transparent"
            },
            "numberSize": "2xl",
            "priceColor": "foreground",
            "scrollAxis": "vertical",
            "titleColor": "foreground",
            "borderColor": "muted",
            "borderWidth": "none",
            "numberColor": "primary",
            "borderRadius": "md",
            "metaTextSize": "xs",
            "showMetaText": false,
            "titleEnabled": false,
            "itemTitleSize": "sm",
            "metaTextColor": "foreground",
            "itemTitleColor": "background",
            "descriptionSize": "sm",
            "descriptionColor": "foreground",
            "imageAspectRatio": "square",
            "originalPriceColor": "foreground",
            "showFeaturedSection": false,
            "featuredSubtitleSize": "md",
            "featuredSubtitleColor": "background"
          },
          "columnIndex": 0
        },
        {
          "id": "ListWidget-v3-blog-h",
          "type": "TextWidget",
          "props": {
            "title": "From the journal",
            "padding": 0,
            "className": "px-6 sm:px-10",
            "background": {
              "type": "solid",
              "color": "transparent"
            },
            "titleColor": "background",
            "borderWidth": "none",
            "description": "Insights, science, and real-world wellness from the [Brand] team.",
            "borderRadius": "none",
            "titleFontSize": "2xl",
            "titleFontWeight": "bold",
            "descriptionColor": "background",
            "descriptionFontSize": "md",
            "descriptionFontWeight": "normal"
          },
          "columnIndex": 0
        },
        {
          "id": "ListWidget-v3-blog-grid",
          "type": "ListWidget",
          "props": {
            "gap": "md",
            "items": [
              {
                "id": 1032,
                "kind": "image",
                "type": "EnrollmentPack",
                "image": "https://picsum.photos/seed/img28/1200/1500",
                "title": "Media item 32",
                "imageUrl": "https://picsum.photos/seed/img28/1200/1500",
                "share_link": "REPLACE_TARGET_URL",
                "canonical_url": "REPLACE_TARGET_URL",
                "shareableType": "EnrollmentPack",
                "shareable_type": "EnrollmentPack"
              },
              {
                "id": 1033,
                "kind": "image",
                "type": "EnrollmentPack",
                "image": "https://picsum.photos/seed/img29/1200/1500",
                "title": "Media item 33",
                "imageUrl": "https://picsum.photos/seed/img29/1200/1500",
                "share_link": "REPLACE_TARGET_URL",
                "canonical_url": "REPLACE_TARGET_URL",
                "shareableType": "EnrollmentPack",
                "shareable_type": "EnrollmentPack"
              },
              {
                "id": 1034,
                "kind": "image",
                "type": "EnrollmentPack",
                "image": "https://picsum.photos/seed/img11/1200/1500",
                "title": "Media item 34",
                "imageUrl": "https://picsum.photos/seed/img11/1200/1500",
                "share_link": "REPLACE_TARGET_URL",
                "canonical_url": "REPLACE_TARGET_URL",
                "shareableType": "EnrollmentPack",
                "shareable_type": "EnrollmentPack"
              },
              {
                "id": 1035,
                "kind": "image",
                "type": "EnrollmentPack",
                "image": "https://picsum.photos/seed/img30/1200/1500",
                "title": "Media item 35",
                "imageUrl": "https://picsum.photos/seed/img30/1200/1500",
                "share_link": "REPLACE_TARGET_URL",
                "canonical_url": "REPLACE_TARGET_URL",
                "shareableType": "EnrollmentPack",
                "shareable_type": "EnrollmentPack"
              },
              {
                "id": 1036,
                "kind": "image",
                "type": "EnrollmentPack",
                "image": "https://picsum.photos/seed/img03/1200/1500",
                "title": "Media item 36",
                "imageUrl": "https://picsum.photos/seed/img03/1200/1500",
                "share_link": "REPLACE_TARGET_URL",
                "canonical_url": "REPLACE_TARGET_URL",
                "shareableType": "EnrollmentPack",
                "shareable_type": "EnrollmentPack"
              },
              {
                "id": 1037,
                "kind": "image",
                "type": "EnrollmentPack",
                "image": "https://picsum.photos/seed/img44/1200/1500",
                "title": "Media item 37",
                "imageUrl": "https://picsum.photos/seed/img44/1200/1500",
                "share_link": "REPLACE_TARGET_URL",
                "canonical_url": "REPLACE_TARGET_URL",
                "shareableType": "EnrollmentPack",
                "shareable_type": "EnrollmentPack"
              },
              {
                "id": 1038,
                "kind": "image",
                "type": "EnrollmentPack",
                "image": "https://picsum.photos/seed/img45/1200/1500",
                "title": "Media item 38",
                "imageUrl": "https://picsum.photos/seed/img45/1200/1500",
                "share_link": "REPLACE_TARGET_URL",
                "canonical_url": "REPLACE_TARGET_URL",
                "shareableType": "EnrollmentPack",
                "shareable_type": "EnrollmentPack"
              },
              {
                "id": 1039,
                "kind": "image",
                "type": "EnrollmentPack",
                "image": "https://picsum.photos/seed/img46/1200/1500",
                "title": "Media item 39",
                "imageUrl": "https://picsum.photos/seed/img46/1200/1500",
                "share_link": "REPLACE_TARGET_URL",
                "canonical_url": "REPLACE_TARGET_URL",
                "shareableType": "EnrollmentPack",
                "shareable_type": "EnrollmentPack"
              }
            ],
            "columns": 4,
            "padding": 2,
            "listType": "unordered",
            "maxItems": 8,
            "className": "px-6 sm:px-10 mb-8",
            "showBadge": false,
            "background": {
              "type": "solid",
              "color": "transparent"
            },
            "scrollAxis": "vertical",
            "borderWidth": "none",
            "showMetaText": false,
            "titleEnabled": false,
            "itemTitleSize": "sm",
            "itemTitleColor": "background",
            "imageAspectRatio": "landscape"
          },
          "columnIndex": 0
        }
      ],
      "background": {
        "type": "solid",
        "color": "foreground"
      },
      "borderWidth": "none",
      "borderRadius": "none",
      "sectionLayout": "single-column"
    },
    "columnIndex": 0
  }
]
```
