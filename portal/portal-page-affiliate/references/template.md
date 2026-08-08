# `component_tree` — Affiliate Page

Post this as the screen's `component_tree` on the PUT, exactly as written —
it is already the array form the endpoint expects. Do not add another
wrapping array, and do not lift the single top-level LayoutWidget out of it:
that node is the page wrapper the live portal needs.
Placeholders are listed in the skill body; replace them before publishing.

```json
[
  {
    "id": "nsa-page",
    "type": "LayoutWidget",
    "props": {
      "gapSize": "lg",
      "padding": 6,
      "children": [
        {
          "id": "nsa2-hero",
          "type": "CarouselWidget",
          "props": {
            "align": {
              "vertical": "center",
              "horizontal": "left"
            },
            "slides": [
              {
                "id": "nsa2-hero-slide",
                "title": "One clear next move.",
                "content": {
                  "type": "ImageWidget",
                  "props": {
                    "alt": "A [Brand] partner sharing skincare products with friends",
                    "src": "https://picsum.photos/seed/img13/1200/1500",
                    "altText": "A [Brand] partner sharing skincare products with friends",
                    "useCustomUrl": true
                  }
                },
                "eyebrow": "YOUR AFFILIATE DESK",
                "buttonLink": "/profile",
                "buttonText": "Review your growth path",
                "description": "Share a useful story, review your path, or follow up with someone already in motion.",
                "buttonEnabled": true,
                "accessibilityLabel": "A [Brand] partner sharing skincare products with friends"
              }
            ],
            "padding": 0,
            "textSize": "sm",
            "textColor": "background",
            "textWidth": "560px",
            "buttonSize": "lg",
            "frameColor": "foreground",
            "headerSize": "2xl",
            "showButton": true,
            "borderWidth": "none",
            "buttonColor": "accent",
            "headerColor": "background",
            "overlayType": "gradient",
            "borderRadius": "lg",
            "carouselHeight": "300px",
            "editorialFrame": false,
            "overlayEnabled": true,
            "enableAutoScroll": false,
            "overlayIntensity": 52
          },
          "columnIndex": 0
        },
        {
          "id": "nsa8-content-library",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "sm",
            "padding": 4,
            "children": [
              {
                "id": "nsa14-video-row-6",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "sm",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nsa13-video-row-1",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "sm",
                        "padding": 0,
                        "children": [
                          {
                            "id": "nsa13-story-video-1",
                            "type": "VideoWidget",
                            "props": {
                              "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                              "tag": "UGC",
                              "date": "",
                              "loop": false,
                              "muted": true,
                              "title": "The device inside my routine",
                              "author": "",
                              "poster": "https://picsum.photos/seed/img04/1200/1500",
                              "eyebrow": "REAL ROUTINE 01",
                              "tagline": "A close, candid look at the [the device] iO in use.",
                              "autoplay": false,
                              "controls": true,
                              "duration": "",
                              "displayFit": "cover",
                              "focusPoint": "center",
                              "frameColor": "foreground",
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "displayMode": "inline",
                              "fixedHeight": "440px",
                              "borderRadius": "md",
                              "useCustomUrl": true,
                              "editorialFrame": false,
                              "primaryCtaLink": "",
                              "primaryCtaText": "",
                              "verticalSizing": "fixed",
                              "secondaryCtaLink": "",
                              "secondaryCtaText": "",
                              "showFullscreenPill": true
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa13-story-video-2",
                            "type": "VideoWidget",
                            "props": {
                              "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                              "tag": "UGC",
                              "date": "",
                              "loop": false,
                              "muted": true,
                              "title": "The ritual I keep coming back to",
                              "author": "",
                              "poster": "https://picsum.photos/seed/img05/1200/1500",
                              "eyebrow": "REAL ROUTINE 02",
                              "tagline": "Why consistency matters more than a perfect routine.",
                              "autoplay": false,
                              "controls": true,
                              "duration": "",
                              "displayFit": "cover",
                              "focusPoint": "center",
                              "frameColor": "foreground",
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "displayMode": "inline",
                              "fixedHeight": "440px",
                              "borderRadius": "md",
                              "useCustomUrl": true,
                              "editorialFrame": false,
                              "primaryCtaLink": "",
                              "primaryCtaText": "",
                              "verticalSizing": "fixed",
                              "secondaryCtaLink": "",
                              "secondaryCtaText": "",
                              "showFullscreenPill": true
                            },
                            "columnIndex": 1
                          },
                          {
                            "id": "nsa13-story-video-3",
                            "type": "VideoWidget",
                            "props": {
                              "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                              "tag": "UGC",
                              "date": "",
                              "loop": false,
                              "muted": true,
                              "title": "Two minutes in my morning",
                              "author": "",
                              "poster": "https://picsum.photos/seed/img06/1200/1500",
                              "eyebrow": "REAL ROUTINE 03",
                              "tagline": "A real morning routine customers can picture themselves doing.",
                              "autoplay": false,
                              "controls": true,
                              "duration": "",
                              "displayFit": "cover",
                              "focusPoint": "center",
                              "frameColor": "foreground",
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "displayMode": "inline",
                              "fixedHeight": "440px",
                              "borderRadius": "md",
                              "useCustomUrl": true,
                              "editorialFrame": false,
                              "primaryCtaLink": "",
                              "primaryCtaText": "",
                              "verticalSizing": "fixed",
                              "secondaryCtaLink": "",
                              "secondaryCtaText": "",
                              "showFullscreenPill": true
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
                      "id": "nsa13-video-row-2",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "sm",
                        "padding": 0,
                        "children": [
                          {
                            "id": "nsa13-story-video-4",
                            "type": "VideoWidget",
                            "props": {
                              "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                              "tag": "UGC",
                              "date": "",
                              "loop": false,
                              "muted": true,
                              "title": "What the clean finish feels like",
                              "author": "",
                              "poster": "https://picsum.photos/seed/img07/1200/1500",
                              "eyebrow": "REAL ROUTINE 04",
                              "tagline": "The product moment that answers the comfort question.",
                              "autoplay": false,
                              "controls": true,
                              "duration": "",
                              "displayFit": "cover",
                              "focusPoint": "center",
                              "frameColor": "foreground",
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "displayMode": "inline",
                              "fixedHeight": "440px",
                              "borderRadius": "md",
                              "useCustomUrl": true,
                              "editorialFrame": false,
                              "primaryCtaLink": "",
                              "primaryCtaText": "",
                              "verticalSizing": "fixed",
                              "secondaryCtaLink": "",
                              "secondaryCtaText": "",
                              "showFullscreenPill": true
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa13-story-video-5",
                            "type": "VideoWidget",
                            "props": {
                              "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                              "tag": "UGC",
                              "date": "",
                              "loop": false,
                              "muted": true,
                              "title": "My no-rush skincare ritual",
                              "author": "",
                              "poster": "https://picsum.photos/seed/img14/1200/1500",
                              "eyebrow": "REAL ROUTINE 05",
                              "tagline": "A slower routine that still feels completely achievable.",
                              "autoplay": false,
                              "controls": true,
                              "duration": "",
                              "displayFit": "cover",
                              "focusPoint": "center",
                              "frameColor": "foreground",
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "displayMode": "inline",
                              "fixedHeight": "440px",
                              "borderRadius": "md",
                              "useCustomUrl": true,
                              "editorialFrame": false,
                              "primaryCtaLink": "",
                              "primaryCtaText": "",
                              "verticalSizing": "fixed",
                              "secondaryCtaLink": "",
                              "secondaryCtaText": "",
                              "showFullscreenPill": true
                            },
                            "columnIndex": 1
                          },
                          {
                            "id": "nsa13-story-video-6",
                            "type": "VideoWidget",
                            "props": {
                              "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                              "tag": "UGC",
                              "date": "",
                              "loop": false,
                              "muted": true,
                              "title": "What consistency changed for me",
                              "author": "",
                              "poster": "https://picsum.photos/seed/img15/1200/1500",
                              "eyebrow": "REAL ROUTINE 06",
                              "tagline": "A straightforward customer story about staying with it.",
                              "autoplay": false,
                              "controls": true,
                              "duration": "",
                              "displayFit": "cover",
                              "focusPoint": "center",
                              "frameColor": "foreground",
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "displayMode": "inline",
                              "fixedHeight": "440px",
                              "borderRadius": "md",
                              "useCustomUrl": true,
                              "editorialFrame": false,
                              "primaryCtaLink": "",
                              "primaryCtaText": "",
                              "verticalSizing": "fixed",
                              "secondaryCtaLink": "",
                              "secondaryCtaText": "",
                              "showFullscreenPill": true
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
              "color": "background"
            },
            "borderColor": "muted",
            "borderWidth": "none",
            "borderRadius": "md",
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        },
        {
          "id": "nsa9-command-center",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "lg",
            "padding": 6,
            "children": [
              {
                "id": "nsa9-command-intro",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "sm",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nsa9-command-intro-label",
                      "type": "TextWidget",
                      "props": {
                        "title": "",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "description": "PARTNER COMMAND CENTER",
                        "borderRadius": "none",
                        "titleEnabled": false,
                        "titleFontSize": "xs",
                        "titleAlignment": "left",
                        "titleFontWeight": "normal",
                        "descriptionColor": "accent",
                        "descriptionFontSize": "xs",
                        "descriptionAlignment": "left",
                        "descriptionFontWeight": "bold"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsa9-command-intro-copy",
                      "type": "TextWidget",
                      "props": {
                        "title": "Everything useful, one move away.",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "background",
                        "borderWidth": "none",
                        "description": "Capture the next follow-up, then jump directly into the tool the moment needs.",
                        "borderRadius": "none",
                        "titleEnabled": true,
                        "titleFontSize": "xl",
                        "titleAlignment": "left",
                        "titleFontWeight": "normal",
                        "descriptionColor": "background",
                        "descriptionFontSize": "sm",
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
                "id": "nsa9-action-grid",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "md",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nsa9-quick-share",
                      "type": "QuickShareWidget",
                      "props": {
                        "padding": 4,
                        "minHeight": "300px",
                        "textColor": "background",
                        "titleText": "Share this week: The Starter Kit",
                        "background": {
                          "type": "solid",
                          "color": "foreground"
                        },
                        "titleColor": "background",
                        "accentColor": "background",
                        "borderColor": "muted",
                        "borderWidth": "none",
                        "overlayType": "gradient",
                        "borderRadius": "md",
                        "titleEnabled": true,
                        "buyButtonLink": "REPLACE_TARGET_URL",
                        "buyButtonText": "View Product",
                        "showBuyButton": false,
                        "titleFontSize": "lg",
                        "overlayEnabled": true,
                        "overlayIntensity": 58,
                        "showDomainPrefix": false,
                        "showResourceType": true,
                        "showShareActions": true,
                        "shareableResource": {
                          "id": "REPLACE_PRODUCT_ID",
                          "name": "Featured Product 6",
                          "slug": "US-kit-beauty-focus-collagen-plus-ageloc-youth-ageloc-meta-nu-biome-subscription-kit-US",
                          "type": "Product",
                          "price": "$00.00",
                          "title": "Featured Product 6",
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
                      "id": "nsa3-ugc-carousel",
                      "type": "CarouselWidget",
                      "props": {
                        "align": {
                          "vertical": "bottom",
                          "horizontal": "left"
                        },
                        "slides": [
                          {
                            "id": "nsa3-ugc-slide-1",
                            "title": "A first look, in her own words.",
                            "content": {
                              "type": "ImageWidget",
                              "props": {
                                "alt": "A first look, in her own words",
                                "src": "https://picsum.photos/seed/img16/1200/1500",
                                "altText": "A first look, in her own words",
                                "useCustomUrl": true
                              }
                            },
                            "eyebrow": "REAL ROUTINE  \u00b7  01",
                            "buttonLink": "/new-screen-13",
                            "buttonText": "Open story",
                            "description": "A first look at [the device] iO, told in her own words.",
                            "buttonEnabled": true,
                            "accessibilityLabel": "A first look, in her own words"
                          },
                          {
                            "id": "nsa3-ugc-slide-2",
                            "title": "Curiosity, captured in the room.",
                            "content": {
                              "type": "ImageWidget",
                              "props": {
                                "alt": "Curiosity, captured in the room",
                                "src": "https://picsum.photos/seed/img17/1200/1500",
                                "altText": "Curiosity, captured in the room",
                                "useCustomUrl": true
                              }
                            },
                            "eyebrow": "LIVE DEMO  \u00b7  02",
                            "buttonLink": "/new-screen-13",
                            "buttonText": "Open story",
                            "description": "A product table seen from inside the conversation.",
                            "buttonEnabled": true,
                            "accessibilityLabel": "Curiosity, captured in the room"
                          },
                          {
                            "id": "nsa3-ugc-slide-3",
                            "title": "The routine inside a real day.",
                            "content": {
                              "type": "ImageWidget",
                              "props": {
                                "alt": "The routine inside a real day",
                                "src": "https://picsum.photos/seed/img18/1200/1500",
                                "altText": "The routine inside a real day",
                                "useCustomUrl": true
                              }
                            },
                            "eyebrow": "IN HER DAY  \u00b7  03",
                            "buttonLink": "/new-screen-13",
                            "buttonText": "Open story",
                            "description": "No studio. No script. Just the product in her day.",
                            "buttonEnabled": true,
                            "accessibilityLabel": "The routine inside a real day"
                          }
                        ],
                        "padding": 0,
                        "textSize": "xs",
                        "textColor": "background",
                        "textWidth": "340px",
                        "buttonSize": "sm",
                        "frameColor": "foreground",
                        "headerSize": "lg",
                        "showButton": true,
                        "borderWidth": "none",
                        "buttonColor": "background",
                        "headerColor": "background",
                        "overlayType": "gradient",
                        "borderRadius": "md",
                        "carouselHeight": "340px",
                        "editorialFrame": false,
                        "overlayEnabled": true,
                        "enableAutoScroll": true,
                        "overlayIntensity": 56
                      },
                      "columnIndex": 1
                    },
                    {
                      "id": "nsa9-calendar",
                      "type": "CalendarWidget",
                      "props": {
                        "padding": 4,
                        "textColor": "foreground",
                        "titleText": "Calendar",
                        "background": {
                          "type": "solid",
                          "color": "background"
                        },
                        "titleColor": "foreground",
                        "weekendDim": true,
                        "accentColor": "accent",
                        "borderColor": "muted",
                        "borderWidth": "thin",
                        "borderRadius": "md",
                        "titleEnabled": true,
                        "titleFontSize": "md",
                        "showTodayButton": true,
                        "showYearEyebrow": false,
                        "showEventDensity": true
                      },
                      "columnIndex": 1
                    },
                    {
                      "id": "nsa9-todo",
                      "type": "ToDoWidget",
                      "props": {
                        "padding": 4,
                        "maxItems": 4,
                        "textColor": "foreground",
                        "titleText": "Next actions",
                        "background": {
                          "type": "solid",
                          "color": "background"
                        },
                        "titleColor": "foreground",
                        "accentColor": "accent",
                        "borderColor": "muted",
                        "borderWidth": "thin",
                        "borderRadius": "md",
                        "titleEnabled": true,
                        "titleFontSize": "md"
                      },
                      "columnIndex": 2
                    },
                    {
                      "id": "nsa9-links-share",
                      "type": "QuickLinksWidget",
                      "props": {
                        "title": "Share",
                        "layout": "list",
                        "padding": 4,
                        "link1Url": "/new-screen-13",
                        "link2Url": "/friend-share",
                        "link3Url": "/my-product-pages",
                        "link4Url": "#",
                        "link5Url": "#",
                        "link6Url": "#",
                        "link7Url": "#",
                        "link8Url": "#",
                        "link1Icon": "Video",
                        "link2Icon": "Gift",
                        "link3Icon": "Globe",
                        "link4Icon": "Link",
                        "link5Icon": "Link",
                        "link6Icon": "Link",
                        "link7Icon": "Link",
                        "link8Icon": "Link",
                        "textColor": "foreground",
                        "background": {
                          "type": "solid",
                          "color": "background"
                        },
                        "iconRadius": "md",
                        "link1Color": "accent",
                        "link1Label": "Create a product story",
                        "link2Color": "accent",
                        "link2Label": "Send Friend Share",
                        "link3Color": "accent",
                        "link3Label": "Open My Product Pages",
                        "link4Color": "accent",
                        "link4Label": "",
                        "link5Color": "accent",
                        "link5Label": "",
                        "link6Color": "accent",
                        "link6Label": "",
                        "link7Color": "accent",
                        "link7Label": "",
                        "link8Color": "accent",
                        "link8Label": "",
                        "titleColor": "foreground",
                        "borderColor": "muted",
                        "borderWidth": "thin",
                        "showChevron": true,
                        "borderRadius": "md",
                        "link1Enabled": true,
                        "link2Enabled": true,
                        "link3Enabled": true,
                        "link4Enabled": false,
                        "link5Enabled": false,
                        "link6Enabled": false,
                        "link7Enabled": false,
                        "link8Enabled": false,
                        "openInNewTab": false,
                        "titleEnabled": true,
                        "titleFontSize": "lg"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsa12-signals-card",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "sm",
                        "padding": 4,
                        "children": [
                          {
                            "id": "nsa12-signals-title",
                            "type": "TextWidget",
                            "props": {
                              "title": "Attribution signals",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderColor": "transparent",
                              "borderWidth": "none",
                              "description": "The activity your sharing set in motion.",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "xl",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "xs",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "normal"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa12-signal-clicks",
                            "type": "TextWidget",
                            "props": {
                              "title": "\u2197  CLICKS  \u00b7  \uff0b16%",
                              "padding": 3,
                              "background": {
                                "type": "solid",
                                "color": "accent"
                              },
                              "titleColor": "foreground",
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "description": "1,248",
                              "borderRadius": "md",
                              "titleEnabled": true,
                              "titleFontSize": "xs",
                              "titleAlignment": "left",
                              "titleFontWeight": "bold",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "lg",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa12-signal-views",
                            "type": "TextWidget",
                            "props": {
                              "title": "\u25c9  PAGE VIEWS  \u00b7  \uff0b21%",
                              "padding": 3,
                              "background": {
                                "type": "solid",
                                "color": "secondary"
                              },
                              "titleColor": "foreground",
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "description": "3,782",
                              "borderRadius": "md",
                              "titleEnabled": true,
                              "titleFontSize": "xs",
                              "titleAlignment": "left",
                              "titleFontWeight": "bold",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "lg",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa12-signal-repeat",
                            "type": "TextWidget",
                            "props": {
                              "title": "\u21bb  REPEAT CUSTOMERS  \u00b7  \uff0b12%",
                              "padding": 3,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderColor": "muted",
                              "borderWidth": "thin",
                              "description": "42",
                              "borderRadius": "md",
                              "titleEnabled": true,
                              "titleFontSize": "xs",
                              "titleAlignment": "left",
                              "titleFontWeight": "bold",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "lg",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa12-signal-delayed",
                            "type": "TextWidget",
                            "props": {
                              "title": "\u25f7  DELAYED CREDIT  \u00b7  THIS MONTH",
                              "padding": 3,
                              "background": {
                                "type": "solid",
                                "color": "primary"
                              },
                              "titleColor": "background",
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "description": "11",
                              "borderRadius": "md",
                              "titleEnabled": true,
                              "titleFontSize": "xs",
                              "titleAlignment": "left",
                              "titleFontWeight": "bold",
                              "descriptionColor": "background",
                              "descriptionFontSize": "lg",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          }
                        ],
                        "background": {
                          "type": "solid",
                          "color": "background"
                        },
                        "borderColor": "transparent",
                        "borderWidth": "none",
                        "borderRadius": "md",
                        "sectionLayout": "single-column"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsa12-center-card",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "sm",
                        "padding": 4,
                        "children": [
                          {
                            "id": "nsa12-center-label",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderColor": "transparent",
                              "borderWidth": "none",
                              "description": "YOUR CENTER",
                              "borderRadius": "none",
                              "titleEnabled": false,
                              "titleFontSize": "xs",
                              "titleAlignment": "left",
                              "titleFontWeight": "bold",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "xs",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa12-center-orbit",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderColor": "transparent",
                              "borderWidth": "none",
                              "description": "\u25ce",
                              "borderRadius": "none",
                              "titleEnabled": false,
                              "titleFontSize": "xs",
                              "titleAlignment": "center",
                              "titleFontWeight": "bold",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "3xl",
                              "descriptionAlignment": "center",
                              "descriptionFontWeight": "normal"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa12-center-total",
                            "type": "TextWidget",
                            "props": {
                              "title": "1,023",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderColor": "transparent",
                              "borderWidth": "none",
                              "description": "people in your active ripple",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "3xl",
                              "titleAlignment": "center",
                              "titleFontWeight": "bold",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "sm",
                              "descriptionAlignment": "center",
                              "descriptionFontWeight": "normal"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa12-center-growth",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 3,
                              "background": {
                                "type": "solid",
                                "color": "primary"
                              },
                              "titleColor": "foreground",
                              "borderColor": "transparent",
                              "borderWidth": "none",
                              "description": "\uff0b86 NEW RELATIONSHIPS THIS MONTH",
                              "borderRadius": "md",
                              "titleEnabled": false,
                              "titleFontSize": "xs",
                              "titleAlignment": "center",
                              "titleFontWeight": "bold",
                              "descriptionColor": "background",
                              "descriptionFontSize": "xs",
                              "descriptionAlignment": "center",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa12-center-direct",
                            "type": "TextWidget",
                            "props": {
                              "title": "82%  \u00b7  DIRECTLY ATTRIBUTED",
                              "padding": 3,
                              "background": {
                                "type": "solid",
                                "color": "background"
                              },
                              "titleColor": "foreground",
                              "borderColor": "transparent",
                              "borderWidth": "none",
                              "description": "Link and page activity matched in the same journey.",
                              "borderRadius": "md",
                              "titleEnabled": true,
                              "titleFontSize": "xs",
                              "titleAlignment": "left",
                              "titleFontWeight": "bold",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "xs",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa12-center-delayed",
                            "type": "TextWidget",
                            "props": {
                              "title": "18%  \u00b7  DELAYED ATTRIBUTION",
                              "padding": 3,
                              "background": {
                                "type": "solid",
                                "color": "primary"
                              },
                              "titleColor": "accent",
                              "borderColor": "transparent",
                              "borderWidth": "none",
                              "description": "They returned later. Your relationship still received credit.",
                              "borderRadius": "md",
                              "titleEnabled": true,
                              "titleFontSize": "xs",
                              "titleAlignment": "left",
                              "titleFontWeight": "bold",
                              "descriptionColor": "background",
                              "descriptionFontSize": "xs",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa12-center-note",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderColor": "transparent",
                              "borderWidth": "none",
                              "description": "Your strongest growth is coming from people returning after an honest product story.",
                              "borderRadius": "none",
                              "titleEnabled": false,
                              "titleFontSize": "xs",
                              "titleAlignment": "left",
                              "titleFontWeight": "bold",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "sm",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "normal"
                            },
                            "columnIndex": 0
                          }
                        ],
                        "background": {
                          "type": "solid",
                          "color": "accent"
                        },
                        "borderColor": "transparent",
                        "borderWidth": "none",
                        "borderRadius": "md",
                        "sectionLayout": "single-column"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsa9-activity",
                      "type": "RecentActivityWidget",
                      "props": {
                        "padding": 4,
                        "textColor": "foreground",
                        "titleText": "Recent activity",
                        "background": {
                          "type": "solid",
                          "color": "secondary"
                        },
                        "titleColor": "foreground",
                        "accentColor": "accent",
                        "borderColor": "muted",
                        "borderWidth": "thin",
                        "showEyebrow": true,
                        "borderRadius": "md",
                        "showTimeline": true,
                        "titleEnabled": true,
                        "showCountChip": true,
                        "titleFontSize": "md",
                        "maxItemsToShow": 3,
                        "showRelativeTime": true
                      },
                      "columnIndex": 1
                    },
                    {
                      "id": "nsa10-command-followup-rhythm",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "lg",
                        "padding": 4,
                        "children": [
                          {
                            "id": "nsa10-command-followup-rhythm-label",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "FOLLOW-THROUGH",
                              "borderRadius": "none",
                              "titleEnabled": false,
                              "titleFontSize": "xs",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "accent",
                              "descriptionFontSize": "xs",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa10-command-followup-step-1",
                            "type": "TextWidget",
                            "props": {
                              "title": "Close the loop while it is warm.",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "Answer the open question, capture what mattered, then schedule the next honest touchpoint.",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "md",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "sm",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "normal"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa10-command-followup-step-2",
                            "type": "TextWidget",
                            "props": {
                              "title": "Keep the list deliberately short.",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "A small number of clear follow-ups is easier to finish\u2014and easier to trust.",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "md",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "sm",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "normal"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa10-command-followup-step-3",
                            "type": "TextWidget",
                            "props": {
                              "title": "End with a date, not a maybe.",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "Put the next touchpoint on the calendar while the context is still clear.",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "md",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "sm",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "normal"
                            },
                            "columnIndex": 0
                          }
                        ],
                        "background": {
                          "type": "solid",
                          "color": "secondary"
                        },
                        "borderColor": "muted",
                        "borderWidth": "thin",
                        "borderRadius": "md",
                        "sectionLayout": "single-column"
                      },
                      "columnIndex": 2
                    },
                    {
                      "id": "nsa10-command-calendar-rhythm",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "md",
                        "padding": 4,
                        "children": [
                          {
                            "id": "nsa10-command-calendar-rhythm-label",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "THIS WEEK",
                              "borderRadius": "none",
                              "titleEnabled": false,
                              "titleFontSize": "xs",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "accent",
                              "descriptionFontSize": "xs",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa10-command-calendar-rhythm-copy",
                            "type": "TextWidget",
                            "props": {
                              "title": "Protect time for one meaningful move.",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "One demo. One follow-up. One hour to learn. Put the rhythm on the calendar before the week fills itself.",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "md",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "sm",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "normal"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa10-command-calendar-rhythm-link",
                            "type": "LinkWidget",
                            "props": {
                              "size": "md",
                              "text": "Open calls & training  \u2192",
                              "variant": "default",
                              "linkType": "screen",
                              "alignment": "left",
                              "fullWidth": false,
                              "screenSlug": "the-hub"
                            },
                            "columnIndex": 0
                          }
                        ],
                        "background": {
                          "type": "solid",
                          "color": "secondary"
                        },
                        "borderColor": "muted",
                        "borderWidth": "thin",
                        "borderRadius": "md",
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
              }
            ],
            "background": {
              "type": "solid",
              "color": "primary"
            },
            "borderColor": "muted",
            "borderWidth": "none",
            "borderRadius": "lg",
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        },
        {
          "id": "nsa11-ripple",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "lg",
            "padding": 6,
            "children": [
              {
                "id": "nsa12-ripple-intro",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "sm",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nsa12-ripple-eyebrow",
                      "type": "TextWidget",
                      "props": {
                        "title": "",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderColor": "transparent",
                        "borderWidth": "none",
                        "description": "ATTRIBUTION / LAST 30 DAYS",
                        "borderRadius": "none",
                        "titleEnabled": false,
                        "titleFontSize": "xs",
                        "titleAlignment": "left",
                        "titleFontWeight": "bold",
                        "descriptionColor": "accent",
                        "descriptionFontSize": "xs",
                        "descriptionAlignment": "left",
                        "descriptionFontWeight": "bold"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsa12-ripple-title",
                      "type": "TextWidget",
                      "props": {
                        "title": "Your ripple, in motion.",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "background",
                        "borderColor": "transparent",
                        "borderWidth": "none",
                        "description": "One honest share keeps moving\u2014through clicks, returns, conversations, and orders you may never see happen live.",
                        "borderRadius": "none",
                        "titleEnabled": true,
                        "titleFontSize": "3xl",
                        "titleAlignment": "left",
                        "titleFontWeight": "normal",
                        "descriptionColor": "background",
                        "descriptionFontSize": "sm",
                        "descriptionAlignment": "left",
                        "descriptionFontWeight": "normal"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsa12-ripple-trust",
                      "type": "TextWidget",
                      "props": {
                        "title": "",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderColor": "transparent",
                        "borderWidth": "none",
                        "description": "\u25c7  VERIFIED ATTRIBUTION   \u00b7   30-DAY LOOKBACK   \u00b7   CROSS-DEVICE MATCHING",
                        "borderRadius": "none",
                        "titleEnabled": false,
                        "titleFontSize": "xs",
                        "titleAlignment": "left",
                        "titleFontWeight": "bold",
                        "descriptionColor": "accent",
                        "descriptionFontSize": "xs",
                        "descriptionAlignment": "left",
                        "descriptionFontWeight": "bold"
                      },
                      "columnIndex": 0
                    }
                  ],
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "borderColor": "transparent",
                  "borderWidth": "none",
                  "borderRadius": "none",
                  "sectionLayout": "single-column"
                },
                "columnIndex": 0
              },
              {
                "id": "nsa12-ripple-flow",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "md",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nsa12-flow-share",
                      "type": "TextWidget",
                      "props": {
                        "title": "01 / SHARE",
                        "padding": 4,
                        "background": {
                          "type": "solid",
                          "color": "primary"
                        },
                        "titleColor": "accent",
                        "borderColor": "transparent",
                        "borderWidth": "none",
                        "description": "One honest routine",
                        "borderRadius": "md",
                        "titleEnabled": true,
                        "titleFontSize": "xs",
                        "titleAlignment": "left",
                        "titleFontWeight": "bold",
                        "descriptionColor": "background",
                        "descriptionFontSize": "lg",
                        "descriptionAlignment": "left",
                        "descriptionFontWeight": "bold"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsa12-flow-return",
                      "type": "TextWidget",
                      "props": {
                        "title": "02 / RETURN",
                        "padding": 4,
                        "background": {
                          "type": "solid",
                          "color": "primary"
                        },
                        "titleColor": "accent",
                        "borderColor": "transparent",
                        "borderWidth": "none",
                        "description": "1,248 clicks  \u2192  3,782 views",
                        "borderRadius": "md",
                        "titleEnabled": true,
                        "titleFontSize": "xs",
                        "titleAlignment": "left",
                        "titleFontWeight": "bold",
                        "descriptionColor": "background",
                        "descriptionFontSize": "lg",
                        "descriptionAlignment": "left",
                        "descriptionFontWeight": "bold"
                      },
                      "columnIndex": 1
                    },
                    {
                      "id": "nsa12-flow-compound",
                      "type": "TextWidget",
                      "props": {
                        "title": "03 / COMPOUND",
                        "padding": 4,
                        "background": {
                          "type": "solid",
                          "color": "accent"
                        },
                        "titleColor": "foreground",
                        "borderColor": "transparent",
                        "borderWidth": "none",
                        "description": "42 repeat  +  11 delayed",
                        "borderRadius": "md",
                        "titleEnabled": true,
                        "titleFontSize": "xs",
                        "titleAlignment": "left",
                        "titleFontWeight": "bold",
                        "descriptionColor": "foreground",
                        "descriptionFontSize": "lg",
                        "descriptionAlignment": "left",
                        "descriptionFontWeight": "bold"
                      },
                      "columnIndex": 2
                    }
                  ],
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "borderColor": "transparent",
                  "borderWidth": "none",
                  "borderRadius": "none",
                  "sectionLayout": "3c-equal"
                },
                "columnIndex": 0
              },
              {
                "id": "nsa12-ripple-evidence",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "sm",
                  "padding": 4,
                  "children": [
                    {
                      "id": "nsa12-evidence-eyebrow",
                      "type": "TextWidget",
                      "props": {
                        "title": "",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderColor": "transparent",
                        "borderWidth": "none",
                        "description": "WHERE ATTENTION IS COMPOUNDING",
                        "borderRadius": "none",
                        "titleEnabled": false,
                        "titleFontSize": "xs",
                        "titleAlignment": "left",
                        "titleFontWeight": "bold",
                        "descriptionColor": "accent",
                        "descriptionFontSize": "xs",
                        "descriptionAlignment": "left",
                        "descriptionFontWeight": "bold"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsa11-most-viewed",
                      "type": "TableWidget",
                      "props": {
                        "data": [
                          {
                            "id": 1,
                            "page": "[Product Name]",
                            "rank": "01",
                            "views": "1,084",
                            "change": "+24%",
                            "orders": "18"
                          },
                          {
                            "id": 2,
                            "page": "[Product Name]",
                            "rank": "02",
                            "views": "826",
                            "change": "+18%",
                            "orders": "12"
                          },
                          {
                            "id": 3,
                            "page": "[skincare line] [supplement] routine",
                            "rank": "03",
                            "views": "641",
                            "change": "+11%",
                            "orders": "9"
                          },
                          {
                            "id": 4,
                            "page": "[Product Name]",
                            "rank": "04",
                            "views": "522",
                            "change": "+9%",
                            "orders": "7"
                          },
                          {
                            "id": 5,
                            "page": "My two-minute [the device] routine",
                            "rank": "05",
                            "views": "417",
                            "change": "+31%",
                            "orders": "6"
                          }
                        ],
                        "columns": [
                          {
                            "key": "rank",
                            "label": "Rank",
                            "sortable": true
                          },
                          {
                            "key": "page",
                            "label": "Page",
                            "sortable": true
                          },
                          {
                            "key": "views",
                            "label": "Views",
                            "sortable": true
                          },
                          {
                            "key": "change",
                            "label": "Change",
                            "sortable": true
                          },
                          {
                            "key": "orders",
                            "label": "Attributed orders",
                            "sortable": true
                          }
                        ],
                        "padding": 4,
                        "textColor": "foreground",
                        "titleText": "Pages carrying the ripple farther",
                        "background": {
                          "type": "solid",
                          "color": "background"
                        },
                        "titleColor": "foreground",
                        "borderColor": "muted",
                        "borderWidth": "none",
                        "borderRadius": "md",
                        "titleEnabled": true,
                        "filterEnabled": false,
                        "titleFontSize": "xl",
                        "maxRowsPerPage": 5,
                        "sortingEnabled": true,
                        "headerTextColor": "background",
                        "paginationEnabled": false,
                        "headerBackgroundColor": "primary",
                        "alternatingColorEnabled": true
                      },
                      "columnIndex": 0
                    }
                  ],
                  "background": {
                    "type": "solid",
                    "color": "secondary"
                  },
                  "borderColor": "transparent",
                  "borderWidth": "none",
                  "borderRadius": "lg",
                  "sectionLayout": "single-column"
                },
                "columnIndex": 0
              }
            ],
            "background": {
              "type": "solid",
              "color": "primary"
            },
            "borderColor": "transparent",
            "borderWidth": "none",
            "borderRadius": "lg",
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        },
        {
          "id": "nsa9-shop-section",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "lg",
            "padding": 6,
            "children": [
              {
                "id": "nsa9-shop-intro",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "sm",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nsa9-shop-intro-label",
                      "type": "TextWidget",
                      "props": {
                        "title": "",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "description": "ORDERED PRODUCT EDIT",
                        "borderRadius": "none",
                        "titleEnabled": false,
                        "titleFontSize": "xs",
                        "titleAlignment": "left",
                        "titleFontWeight": "normal",
                        "descriptionColor": "accent",
                        "descriptionFontSize": "xs",
                        "descriptionAlignment": "left",
                        "descriptionFontWeight": "bold"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsa9-shop-intro-copy",
                      "type": "TextWidget",
                      "props": {
                        "title": "Products ready for the next conversation.",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "description": "A numbered shortlist keeps the recommendation clear, comparable, and easy to open.",
                        "borderRadius": "none",
                        "titleEnabled": true,
                        "titleFontSize": "xl",
                        "titleAlignment": "left",
                        "titleFontWeight": "normal",
                        "descriptionColor": "foreground",
                        "descriptionFontSize": "sm",
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
                "id": "nsa10-ordered-products",
                "type": "ListWidget",
                "props": {
                  "gap": "lg",
                  "items": [
                    {
                      "id": "REPLACE_PRODUCT_ID",
                      "alt": "[Product Name]",
                      "slug": "ageloc-rose-gold-lumispa-io",
                      "type": "Product",
                      "image": "https://picsum.photos/seed/img03/1200/1500",
                      "price": "$00.00",
                      "title": "Featured Product 7",
                      "status": "active",
                      "imageUrl": "https://picsum.photos/seed/img03/1200/1500",
                      "image_url": "https://picsum.photos/seed/img03/1200/1500",
                      "shareLink": "REPLACE_TARGET_URL",
                      "productUrl": "REPLACE_TARGET_URL",
                      "share_link": "REPLACE_TARGET_URL",
                      "description": "One-line product description goes here.",
                      "product_url": "REPLACE_TARGET_URL",
                      "display_price": "$00.00",
                      "shareableType": "Product"
                    },
                    {
                      "id": "REPLACE_PRODUCT_ID",
                      "alt": "[Product Name]",
                      "slug": "ageloc-boost-activating-serum",
                      "type": "Product",
                      "image": "https://picsum.photos/seed/img08/1200/1500",
                      "price": "$00.00",
                      "title": "Featured Product 8",
                      "status": "active",
                      "imageUrl": "https://picsum.photos/seed/img08/1200/1500",
                      "image_url": "https://picsum.photos/seed/img08/1200/1500",
                      "shareLink": "REPLACE_TARGET_URL",
                      "productUrl": "REPLACE_TARGET_URL",
                      "share_link": "REPLACE_TARGET_URL",
                      "description": "One-line product description goes here.",
                      "product_url": "REPLACE_TARGET_URL",
                      "display_price": "$00.00",
                      "shareableType": "Product"
                    },
                    {
                      "id": "REPLACE_PRODUCT_ID",
                      "alt": "[skincare line] [supplement] + [the device] Cleanser",
                      "slug": "beauty-focus-collagen-lumispa-acne-subscription-US",
                      "type": "Product",
                      "image": "https://picsum.photos/seed/img09/1200/1500",
                      "price": "$00.00",
                      "title": "Featured Product 9",
                      "status": "active",
                      "imageUrl": "https://picsum.photos/seed/img09/1200/1500",
                      "image_url": "https://picsum.photos/seed/img09/1200/1500",
                      "shareLink": "REPLACE_TARGET_URL",
                      "productUrl": "REPLACE_TARGET_URL",
                      "share_link": "REPLACE_TARGET_URL",
                      "description": "One-line product description goes here.",
                      "product_url": "REPLACE_TARGET_URL",
                      "display_price": "$00.00",
                      "shareableType": "Product"
                    },
                    {
                      "id": "REPLACE_PRODUCT_ID",
                      "alt": "[Product Name]",
                      "slug": "ageloc-meta-nu-biome-bundle",
                      "type": "Product",
                      "image": "https://picsum.photos/seed/img10/1200/1500",
                      "price": "$00.00",
                      "title": "Featured Product 10",
                      "status": "active",
                      "imageUrl": "https://picsum.photos/seed/img10/1200/1500",
                      "image_url": "https://picsum.photos/seed/img10/1200/1500",
                      "shareLink": "REPLACE_TARGET_URL",
                      "productUrl": "REPLACE_TARGET_URL",
                      "share_link": "REPLACE_TARGET_URL",
                      "description": "One-line product description goes here.",
                      "product_url": "REPLACE_TARGET_URL",
                      "display_price": "$00.00",
                      "shareableType": "Product"
                    },
                    {
                      "id": "REPLACE_PRODUCT_ID",
                      "alt": "[Product Name] Bundle",
                      "slug": "collagen-nu-biome-bundle",
                      "type": "Product",
                      "image": "https://picsum.photos/seed/img11/1200/1500",
                      "price": "$00.00",
                      "title": "Featured Product 11",
                      "status": "active",
                      "imageUrl": "https://picsum.photos/seed/img11/1200/1500",
                      "image_url": "https://picsum.photos/seed/img11/1200/1500",
                      "shareLink": "REPLACE_TARGET_URL",
                      "productUrl": "REPLACE_TARGET_URL",
                      "share_link": "REPLACE_TARGET_URL",
                      "description": "One-line product description goes here.",
                      "product_url": "REPLACE_TARGET_URL",
                      "display_price": "$00.00",
                      "shareableType": "Product"
                    }
                  ],
                  "title": "The partner product edit",
                  "padding": 5,
                  "listType": "ordered",
                  "maxItems": 5,
                  "priceSize": "md",
                  "showBadge": false,
                  "titleSize": "lg",
                  "background": {
                    "type": "solid",
                    "color": "background"
                  },
                  "numberSize": "2xl",
                  "priceColor": "foreground",
                  "scrollAxis": "horizontal",
                  "titleColor": "foreground",
                  "borderColor": "muted",
                  "borderWidth": "thin",
                  "numberColor": "accent",
                  "borderRadius": "md",
                  "metaTextSize": "xs",
                  "showMetaText": false,
                  "titleEnabled": true,
                  "itemTitleSize": "sm",
                  "metaTextColor": "muted",
                  "itemTitleColor": "foreground",
                  "descriptionSize": "xs",
                  "descriptionColor": "foreground",
                  "originalPriceColor": "muted"
                },
                "columnIndex": 0
              }
            ],
            "background": {
              "type": "solid",
              "color": "secondary"
            },
            "borderColor": "muted",
            "borderWidth": "none",
            "borderRadius": "lg",
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        },
        {
          "id": "nsa10-partner-promise",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "lg",
            "padding": 6,
            "children": [
              {
                "id": "nsa10-promise-intro",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "sm",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nsa10-promise-intro-label",
                      "type": "TextWidget",
                      "props": {
                        "title": "",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "description": "THE PARTNER PROMISE",
                        "borderRadius": "none",
                        "titleEnabled": false,
                        "titleFontSize": "xs",
                        "titleAlignment": "left",
                        "titleFontWeight": "normal",
                        "descriptionColor": "accent",
                        "descriptionFontSize": "xs",
                        "descriptionAlignment": "left",
                        "descriptionFontWeight": "bold"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsa10-promise-intro-copy",
                      "type": "TextWidget",
                      "props": {
                        "title": "Designed to protect the way trust is built.",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "background",
                        "borderWidth": "none",
                        "description": "Your voice, the right guardrails, and clear attribution stay together from story to sale.",
                        "borderRadius": "none",
                        "titleEnabled": true,
                        "titleFontSize": "xl",
                        "titleAlignment": "left",
                        "titleFontWeight": "normal",
                        "descriptionColor": "background",
                        "descriptionFontSize": "sm",
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
                "id": "nsa10-promise-grid",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "md",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nsa10-promise-voice",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "lg",
                        "padding": 5,
                        "children": [
                          {
                            "id": "nsa10-promise-voice-icon",
                            "type": "TextWidget",
                            "props": {
                              "title": "\u2726",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "accent",
                              "borderWidth": "none",
                              "description": "01 / YOUR VOICE",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "2xl",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "accent",
                              "descriptionFontSize": "xs",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa10-promise-voice-copy",
                            "type": "TextWidget",
                            "props": {
                              "title": "Sound like yourself.",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "Your real experience stays at the center of every recommendation.",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "lg",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "sm",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "normal"
                            },
                            "columnIndex": 0
                          }
                        ],
                        "minHeight": "190px",
                        "background": {
                          "type": "solid",
                          "color": "background"
                        },
                        "borderColor": "muted",
                        "borderWidth": "thin",
                        "borderRadius": "md",
                        "sectionLayout": "single-column"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsa10-promise-safe",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "lg",
                        "padding": 5,
                        "children": [
                          {
                            "id": "nsa10-promise-safe-icon",
                            "type": "TextWidget",
                            "props": {
                              "title": "\u2713",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "accent",
                              "borderWidth": "none",
                              "description": "02 / BUILT-IN GUARDRAILS",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "2xl",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "accent",
                              "descriptionFontSize": "xs",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa10-promise-safe-copy",
                            "type": "TextWidget",
                            "props": {
                              "title": "Share with confidence.",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "Approved claims and review stay inside the path instead of slowing it down.",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "lg",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "sm",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "normal"
                            },
                            "columnIndex": 0
                          }
                        ],
                        "minHeight": "190px",
                        "background": {
                          "type": "solid",
                          "color": "background"
                        },
                        "borderColor": "muted",
                        "borderWidth": "thin",
                        "borderRadius": "md",
                        "sectionLayout": "single-column"
                      },
                      "columnIndex": 1
                    },
                    {
                      "id": "nsa10-promise-credit",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "lg",
                        "padding": 5,
                        "children": [
                          {
                            "id": "nsa10-promise-credit-icon",
                            "type": "TextWidget",
                            "props": {
                              "title": "\u2197",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "accent",
                              "borderWidth": "none",
                              "description": "03 / CLEAR ATTRIBUTION",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "2xl",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "accent",
                              "descriptionFontSize": "xs",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nsa10-promise-credit-copy",
                            "type": "TextWidget",
                            "props": {
                              "title": "Keep the relationship.",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "Your link carries the partner relationship through the final purchase.",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "lg",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "sm",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "normal"
                            },
                            "columnIndex": 0
                          }
                        ],
                        "minHeight": "190px",
                        "background": {
                          "type": "solid",
                          "color": "background"
                        },
                        "borderColor": "muted",
                        "borderWidth": "thin",
                        "borderRadius": "md",
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
              }
            ],
            "background": {
              "type": "solid",
              "color": "primary"
            },
            "borderColor": "muted",
            "borderWidth": "none",
            "borderRadius": "lg",
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        }
      ],
      "background": {
        "type": "solid",
        "color": "background"
      },
      "borderWidth": "none",
      "borderRadius": "none",
      "sectionLayout": "single-column"
    },
    "columnIndex": 0
  }
]
```
