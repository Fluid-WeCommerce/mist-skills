# `component_tree` — Customer Home

Post this as the screen's `component_tree` on the PUT, exactly as written —
it is already the array form the endpoint expects. Do not add another
wrapping array, and do not lift the single top-level LayoutWidget out of it:
that node is the page wrapper the live portal needs.
Placeholders are listed in the skill body; replace them before publishing.

```json
[
  {
    "id": "nsc-page",
    "type": "LayoutWidget",
    "props": {
      "gapSize": "xl",
      "padding": 4,
      "children": [
        {
          "id": "nsc-hero",
          "type": "CarouselWidget",
          "props": {
            "align": {
              "vertical": "center",
              "horizontal": "left"
            },
            "slides": [
              {
                "id": "nsc-hero-s1",
                "title": "Beautiful skin is a ritual, not a chance.",
                "content": {
                  "type": "ImageWidget",
                  "props": {
                    "src": "https://picsum.photos/seed/img19/1200/1500",
                    "useCustomUrl": true
                  }
                },
                "eyebrow": "WELCOME BACK",
                "buttonLink": "/share/products",
                "buttonText": "Shop your routine",
                "description": "Your routine, rewards, and the latest [science] science \u2014 curated for you, all in one place.",
                "buttonEnabled": true,
                "secondaryButtonLink": "/home",
                "secondaryButtonText": "Retake the skin quiz"
              },
              {
                "id": "nsc-hero-s2",
                "title": "The Rose Gold Edition has arrived.",
                "content": {
                  "type": "ImageWidget",
                  "props": {
                    "src": "https://picsum.photos/seed/img20/1200/1500",
                    "useCustomUrl": true
                  }
                },
                "eyebrow": "JUST DROPPED \u00b7 LIMITED",
                "buttonLink": "/share/products",
                "buttonText": "Meet the Rose Gold",
                "description": "Meet [Product Name] \u2014 the icon, reimagined. Members shop it first.",
                "buttonEnabled": true
              }
            ],
            "padding": 0,
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
            "carouselHeight": "440px",
            "editorialFrame": false,
            "overlayEnabled": true,
            "enableAutoScroll": true,
            "overlayIntensity": 66,
            "autoScrollInterval": 6500
          },
          "columnIndex": 0
        },
        {
          "id": "nsc-h1",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "xs",
            "padding": 0,
            "children": [
              {
                "id": "nsc-h1-e",
                "type": "TextWidget",
                "props": {
                  "title": "MY [BRAND]",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "",
                  "borderRadius": "none",
                  "titleEnabled": true,
                  "titleFontSize": "xs",
                  "titleAlignment": "left",
                  "titleFontWeight": "bold",
                  "descriptionColor": "foreground",
                  "descriptionFontSize": "sm",
                  "descriptionAlignment": "left",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 0
              },
              {
                "id": "nsc-h1-h",
                "type": "TextWidget",
                "props": {
                  "title": "Welcome back.",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "Your rewards, orders, and routine \u2014 at a glance.",
                  "borderRadius": "none",
                  "titleEnabled": true,
                  "titleFontSize": "4xl",
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
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        },
        {
          "id": "nsc-glance",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "md",
            "padding": 0,
            "children": [
              {
                "id": "nsc-quick",
                "type": "QuickLinksWidget",
                "props": {
                  "title": "Your account",
                  "layout": "list",
                  "padding": 0,
                  "link1Url": "share/orders",
                  "link2Url": "subscribe-save-orders",
                  "link3Url": "subscription-discounts",
                  "link4Url": "friend-share",
                  "link5Url": "#",
                  "link6Url": "#",
                  "link7Url": "#",
                  "link8Url": "#",
                  "link1Icon": "Package",
                  "link2Icon": "RefreshCw",
                  "link3Icon": "BadgePercent",
                  "link4Icon": "Gift",
                  "link5Icon": "Link",
                  "link6Icon": "Link",
                  "link7Icon": "Link",
                  "link8Icon": "Link",
                  "textColor": "primary",
                  "background": {
                    "type": "color",
                    "color": "transparent"
                  },
                  "iconRadius": "lg",
                  "link1Color": "primary",
                  "link1Label": "Track my orders",
                  "link2Color": "primary",
                  "link2Label": "Manage my subscriptions",
                  "link3Color": "primary",
                  "link3Label": "Subscription discounts",
                  "link4Color": "primary",
                  "link4Label": "Refer a friend \u2014 give $25",
                  "link5Color": "primary",
                  "link5Label": "",
                  "link6Color": "primary",
                  "link6Label": "",
                  "link7Color": "primary",
                  "link7Label": "",
                  "link8Color": "primary",
                  "link8Label": "",
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "showChevron": true,
                  "borderRadius": "none",
                  "link1Enabled": true,
                  "link2Enabled": true,
                  "link3Enabled": true,
                  "link4Enabled": true,
                  "link5Enabled": false,
                  "link6Enabled": false,
                  "link7Enabled": false,
                  "link8Enabled": false,
                  "openInNewTab": false,
                  "titleEnabled": true,
                  "titleFontSize": "xl"
                },
                "columnIndex": 0
              },
              {
                "id": "nsc-points",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "sm",
                  "padding": 5,
                  "children": [
                    {
                      "id": "nsc-points-label",
                      "type": "TextWidget",
                      "props": {
                        "title": "",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "accent",
                        "borderColor": "transparent",
                        "borderWidth": "none",
                        "description": "REWARDS BALANCE \u00b7 JULY",
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
                      "id": "nsc-points-balance",
                      "type": "TextWidget",
                      "props": {
                        "title": "1,240 points",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "background",
                        "borderColor": "transparent",
                        "borderWidth": "none",
                        "description": "760 points to your next milestone. Qualifying orders and referrals update automatically.",
                        "borderRadius": "none",
                        "titleEnabled": true,
                        "titleFontSize": "2xl",
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
                      "id": "nsc-points-progress",
                      "type": "TextWidget",
                      "props": {
                        "title": "",
                        "padding": 2,
                        "background": {
                          "type": "solid",
                          "color": "accent"
                        },
                        "titleColor": "primary",
                        "borderColor": "transparent",
                        "borderWidth": "none",
                        "description": "+320 THIS MONTH  \u00b7  4 ORDERS CREDITED",
                        "borderRadius": "md",
                        "titleEnabled": false,
                        "titleFontSize": "xl",
                        "titleAlignment": "left",
                        "titleFontWeight": "normal",
                        "descriptionColor": "primary",
                        "descriptionFontSize": "xs",
                        "descriptionAlignment": "left",
                        "descriptionFontWeight": "bold"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsc-points-link",
                      "type": "LinkWidget",
                      "props": {
                        "href": "",
                        "size": "lg",
                        "text": "View rewards activity  \u2192",
                        "padding": 0,
                        "variant": "secondary",
                        "fontSize": "sm",
                        "linkType": "screen",
                        "shareUrl": "",
                        "alignment": "left",
                        "fullWidth": false,
                        "underline": false,
                        "screenSlug": "profile",
                        "borderColor": "muted",
                        "borderWidth": "none",
                        "shareSource": "resource",
                        "openInNewTab": true,
                        "borderRadiusBL": "md",
                        "borderRadiusBR": "md",
                        "borderRadiusTL": "md",
                        "borderRadiusTR": "md"
                      },
                      "columnIndex": 0
                    }
                  ],
                  "background": {
                    "type": "solid",
                    "color": "primary"
                  },
                  "borderColor": "primary",
                  "borderWidth": "none",
                  "borderRadius": "lg",
                  "sectionLayout": "single-column"
                },
                "columnIndex": 1
              }
            ],
            "background": {
              "type": "solid",
              "color": "transparent"
            },
            "borderWidth": "none",
            "borderRadius": "xl",
            "sectionLayout": "2c-left-wider"
          },
          "columnIndex": 0
        },
        {
          "id": "nsc-h2",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "xs",
            "padding": 0,
            "children": [
              {
                "id": "nsc-h2-e",
                "type": "TextWidget",
                "props": {
                  "title": "LEARN",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "",
                  "borderRadius": "none",
                  "titleEnabled": true,
                  "titleFontSize": "xs",
                  "titleAlignment": "left",
                  "titleFontWeight": "bold",
                  "descriptionColor": "foreground",
                  "descriptionFontSize": "sm",
                  "descriptionAlignment": "left",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 0
              },
              {
                "id": "nsc-h2-h",
                "type": "TextWidget",
                "props": {
                  "title": "Master your ritual.",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "Two minutes, twice a day. Here's how the pros do it.",
                  "borderRadius": "none",
                  "titleEnabled": true,
                  "titleFontSize": "4xl",
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
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        },
        {
          "id": "nsc-ritual",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "lg",
            "padding": 0,
            "children": [
              {
                "id": "nsc-vid1",
                "type": "VideoWidget",
                "props": {
                  "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                  "tag": "HOW-TO",
                  "date": "",
                  "loop": false,
                  "muted": true,
                  "title": "The 2-minute ritual",
                  "author": "",
                  "poster": "https://picsum.photos/seed/img02/1200/1500",
                  "eyebrow": "YOUR ROUTINE",
                  "tagline": "Master your [the device] \u2014 morning and night.",
                  "autoplay": false,
                  "controls": true,
                  "duration": "",
                  "displayFit": "cover",
                  "focusPoint": "center",
                  "frameColor": "foreground",
                  "borderColor": "muted",
                  "borderWidth": "none",
                  "displayMode": "card",
                  "fixedHeight": "200px",
                  "borderRadius": "xl",
                  "useCustomUrl": true,
                  "editorialFrame": true,
                  "primaryCtaLink": "",
                  "primaryCtaText": "",
                  "verticalSizing": "auto",
                  "secondaryCtaLink": "",
                  "secondaryCtaText": "",
                  "showFullscreenPill": true
                },
                "columnIndex": 0
              },
              {
                "id": "nsc-vid2",
                "type": "VideoWidget",
                "props": {
                  "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                  "tag": "3 MIN",
                  "date": "",
                  "loop": false,
                  "muted": true,
                  "title": "Layer it right",
                  "author": "",
                  "poster": "https://picsum.photos/seed/img21/1200/1500",
                  "eyebrow": "YOUR ROUTINE",
                  "tagline": "The order your products want to be applied in.",
                  "autoplay": false,
                  "controls": true,
                  "duration": "",
                  "displayFit": "cover",
                  "focusPoint": "center",
                  "frameColor": "foreground",
                  "borderColor": "muted",
                  "borderWidth": "none",
                  "displayMode": "card",
                  "fixedHeight": "200px",
                  "borderRadius": "xl",
                  "useCustomUrl": true,
                  "editorialFrame": true,
                  "primaryCtaLink": "",
                  "primaryCtaText": "",
                  "verticalSizing": "auto",
                  "secondaryCtaLink": "",
                  "secondaryCtaText": "",
                  "showFullscreenPill": true
                },
                "columnIndex": 1
              },
              {
                "id": "nsc-ritual-v3",
                "type": "VideoWidget",
                "props": {
                  "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                  "tag": "FILM",
                  "date": "",
                  "loop": false,
                  "muted": true,
                  "title": "The story behind the science",
                  "author": "",
                  "poster": "https://picsum.photos/seed/img19/1200/1500",
                  "eyebrow": "THE BRAND",
                  "tagline": "Forty years of research, in one film.",
                  "autoplay": false,
                  "controls": true,
                  "duration": "",
                  "displayFit": "cover",
                  "focusPoint": "center",
                  "frameColor": "foreground",
                  "borderColor": "muted",
                  "borderWidth": "none",
                  "displayMode": "card",
                  "fixedHeight": "200px",
                  "borderRadius": "xl",
                  "useCustomUrl": true,
                  "editorialFrame": true,
                  "primaryCtaLink": "",
                  "primaryCtaText": "",
                  "verticalSizing": "auto",
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
            "borderWidth": "none",
            "borderRadius": "xl",
            "sectionLayout": "3c-equal"
          },
          "columnIndex": 0
        },
        {
          "id": "nsc-h3",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "xs",
            "padding": 0,
            "children": [
              {
                "id": "nsc-h3-e",
                "type": "TextWidget",
                "props": {
                  "title": "MEMBER PERKS",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "",
                  "borderRadius": "none",
                  "titleEnabled": true,
                  "titleFontSize": "xs",
                  "titleAlignment": "left",
                  "titleFontWeight": "bold",
                  "descriptionColor": "foreground",
                  "descriptionFontSize": "sm",
                  "descriptionAlignment": "left",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 0
              },
              {
                "id": "nsc-h3-h",
                "type": "TextWidget",
                "props": {
                  "title": "Being a member pays.",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "",
                  "borderRadius": "none",
                  "titleEnabled": true,
                  "titleFontSize": "4xl",
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
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        },
        {
          "id": "nsc-perks",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "lg",
            "padding": 0,
            "children": [
              {
                "id": "nsc-p1",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "sm",
                  "padding": 6,
                  "children": [
                    {
                      "id": "nsc-p1-q",
                      "type": "QuickLinksWidget",
                      "props": {
                        "title": "",
                        "layout": "list",
                        "padding": 0,
                        "link1Url": "subscribe-save-orders",
                        "link2Url": "#",
                        "link3Url": "#",
                        "link4Url": "#",
                        "link5Url": "#",
                        "link6Url": "#",
                        "link7Url": "#",
                        "link8Url": "#",
                        "link1Icon": "Truck",
                        "link2Icon": "Link",
                        "link3Icon": "Link",
                        "link4Icon": "Link",
                        "link5Icon": "Link",
                        "link6Icon": "Link",
                        "link7Icon": "Link",
                        "link8Icon": "Link",
                        "textColor": "primary",
                        "background": {
                          "type": "color",
                          "color": "transparent"
                        },
                        "iconRadius": "lg",
                        "link1Color": "primary",
                        "link1Label": "Free shipping",
                        "link2Color": "primary",
                        "link2Label": "",
                        "link3Color": "primary",
                        "link3Label": "",
                        "link4Color": "primary",
                        "link4Label": "",
                        "link5Color": "primary",
                        "link5Label": "",
                        "link6Color": "primary",
                        "link6Label": "",
                        "link7Color": "primary",
                        "link7Label": "",
                        "link8Color": "primary",
                        "link8Label": "",
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "showChevron": true,
                        "borderRadius": "none",
                        "link1Enabled": true,
                        "link2Enabled": false,
                        "link3Enabled": false,
                        "link4Enabled": false,
                        "link5Enabled": false,
                        "link6Enabled": false,
                        "link7Enabled": false,
                        "link8Enabled": false,
                        "openInNewTab": false,
                        "titleEnabled": false,
                        "titleFontSize": "xl"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsc-p1-d",
                      "type": "TextWidget",
                      "props": {
                        "title": "Complimentary shipping on every Subscribe & Save order.",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "description": "",
                        "borderRadius": "none",
                        "titleEnabled": true,
                        "titleFontSize": "sm",
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
                  "borderWidth": "none",
                  "borderRadius": "xl",
                  "sectionLayout": "single-column"
                },
                "columnIndex": 0
              },
              {
                "id": "nsc-p2",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "sm",
                  "padding": 6,
                  "children": [
                    {
                      "id": "nsc-p2-q",
                      "type": "QuickLinksWidget",
                      "props": {
                        "title": "",
                        "layout": "list",
                        "padding": 0,
                        "link1Url": "subscription-discounts",
                        "link2Url": "#",
                        "link3Url": "#",
                        "link4Url": "#",
                        "link5Url": "#",
                        "link6Url": "#",
                        "link7Url": "#",
                        "link8Url": "#",
                        "link1Icon": "BadgePercent",
                        "link2Icon": "Link",
                        "link3Icon": "Link",
                        "link4Icon": "Link",
                        "link5Icon": "Link",
                        "link6Icon": "Link",
                        "link7Icon": "Link",
                        "link8Icon": "Link",
                        "textColor": "primary",
                        "background": {
                          "type": "color",
                          "color": "transparent"
                        },
                        "iconRadius": "lg",
                        "link1Color": "primary",
                        "link1Label": "Best-price lock",
                        "link2Color": "primary",
                        "link2Label": "",
                        "link3Color": "primary",
                        "link3Label": "",
                        "link4Color": "primary",
                        "link4Label": "",
                        "link5Color": "primary",
                        "link5Label": "",
                        "link6Color": "primary",
                        "link6Label": "",
                        "link7Color": "primary",
                        "link7Label": "",
                        "link8Color": "primary",
                        "link8Label": "",
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "showChevron": true,
                        "borderRadius": "none",
                        "link1Enabled": true,
                        "link2Enabled": false,
                        "link3Enabled": false,
                        "link4Enabled": false,
                        "link5Enabled": false,
                        "link6Enabled": false,
                        "link7Enabled": false,
                        "link8Enabled": false,
                        "openInNewTab": false,
                        "titleEnabled": false,
                        "titleFontSize": "xl"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsc-p2-d",
                      "type": "TextWidget",
                      "props": {
                        "title": "Lock in your lowest price when you subscribe to your routine.",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "description": "",
                        "borderRadius": "none",
                        "titleEnabled": true,
                        "titleFontSize": "sm",
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
                  "borderWidth": "none",
                  "borderRadius": "xl",
                  "sectionLayout": "single-column"
                },
                "columnIndex": 1
              },
              {
                "id": "nsc-p3",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "sm",
                  "padding": 6,
                  "children": [
                    {
                      "id": "nsc-p3-q",
                      "type": "QuickLinksWidget",
                      "props": {
                        "title": "",
                        "layout": "list",
                        "padding": 0,
                        "link1Url": "share/products",
                        "link2Url": "#",
                        "link3Url": "#",
                        "link4Url": "#",
                        "link5Url": "#",
                        "link6Url": "#",
                        "link7Url": "#",
                        "link8Url": "#",
                        "link1Icon": "Sparkles",
                        "link2Icon": "Link",
                        "link3Icon": "Link",
                        "link4Icon": "Link",
                        "link5Icon": "Link",
                        "link6Icon": "Link",
                        "link7Icon": "Link",
                        "link8Icon": "Link",
                        "textColor": "primary",
                        "background": {
                          "type": "color",
                          "color": "transparent"
                        },
                        "iconRadius": "lg",
                        "link1Color": "primary",
                        "link1Label": "First access",
                        "link2Color": "primary",
                        "link2Label": "",
                        "link3Color": "primary",
                        "link3Label": "",
                        "link4Color": "primary",
                        "link4Label": "",
                        "link5Color": "primary",
                        "link5Label": "",
                        "link6Color": "primary",
                        "link6Label": "",
                        "link7Color": "primary",
                        "link7Label": "",
                        "link8Color": "primary",
                        "link8Label": "",
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "showChevron": true,
                        "borderRadius": "none",
                        "link1Enabled": true,
                        "link2Enabled": false,
                        "link3Enabled": false,
                        "link4Enabled": false,
                        "link5Enabled": false,
                        "link6Enabled": false,
                        "link7Enabled": false,
                        "link8Enabled": false,
                        "openInNewTab": false,
                        "titleEnabled": false,
                        "titleFontSize": "xl"
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nsc-p3-d",
                      "type": "TextWidget",
                      "props": {
                        "title": "Shop new drops and limited editions before anyone else.",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "description": "",
                        "borderRadius": "none",
                        "titleEnabled": true,
                        "titleFontSize": "sm",
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
                  "borderWidth": "none",
                  "borderRadius": "xl",
                  "sectionLayout": "single-column"
                },
                "columnIndex": 2
              }
            ],
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
          "id": "nsc-h4",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "xs",
            "padding": 0,
            "children": [
              {
                "id": "nsc-h4-e",
                "type": "TextWidget",
                "props": {
                  "title": "THE COLLECTION",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "",
                  "borderRadius": "none",
                  "titleEnabled": true,
                  "titleFontSize": "xs",
                  "titleAlignment": "left",
                  "titleFontWeight": "bold",
                  "descriptionColor": "foreground",
                  "descriptionFontSize": "sm",
                  "descriptionAlignment": "left",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 0
              },
              {
                "id": "nsc-h4-h",
                "type": "TextWidget",
                "props": {
                  "title": "Loved by members.",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "The proven essentials to build your routine around.",
                  "borderRadius": "none",
                  "titleEnabled": true,
                  "titleFontSize": "4xl",
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
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        },
        {
          "id": "nsc-shop",
          "type": "ListWidget",
          "props": {
            "gap": "md",
            "items": [
              {
                "id": 1005,
                "kind": "image",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img22/1200/1500",
                "title": "Media item 5",
                "status": "active",
                "imageUrl": "https://picsum.photos/seed/img22/1200/1500",
                "metaText": "$229.00",
                "description": "Short caption.",
                "display_price": "$229.00"
              },
              {
                "id": 1006,
                "kind": "image",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img09/1200/1500",
                "title": "Media item 6",
                "status": "active",
                "imageUrl": "https://picsum.photos/seed/img09/1200/1500",
                "metaText": "$166.00",
                "description": "Short caption.",
                "display_price": "$166.00"
              },
              {
                "id": 1007,
                "kind": "image",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img08/1200/1500",
                "title": "Media item 7",
                "status": "active",
                "imageUrl": "https://picsum.photos/seed/img08/1200/1500",
                "metaText": "$72.00",
                "description": "Short caption.",
                "display_price": "$72.00"
              },
              {
                "id": 1008,
                "kind": "image",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img03/1200/1500",
                "title": "Media item 8",
                "status": "active",
                "imageUrl": "https://picsum.photos/seed/img03/1200/1500",
                "metaText": "$229.00",
                "description": "Short caption.",
                "display_price": "$229.00"
              }
            ],
            "title": "",
            "columns": 4,
            "padding": 4,
            "listType": "unordered",
            "maxItems": 4,
            "priceSize": "md",
            "showBadge": false,
            "titleSize": "xl",
            "background": {
              "type": "solid",
              "color": "transparent"
            },
            "numberSize": "2xl",
            "priceColor": "foreground",
            "scrollAxis": "horizontal",
            "titleColor": "foreground",
            "borderColor": "muted",
            "borderWidth": "none",
            "numberColor": "primary",
            "borderRadius": "md",
            "metaTextSize": "xs",
            "showMetaText": true,
            "titleEnabled": false,
            "itemTitleSize": "sm",
            "metaTextColor": "foreground",
            "itemTitleColor": "foreground",
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
          "id": "nsc-shopall",
          "type": "LinkWidget",
          "props": {
            "size": "md",
            "text": "Shop all products \u2192",
            "variant": "link",
            "linkType": "screen",
            "alignment": "left",
            "fullWidth": false,
            "screenSlug": "share/products"
          },
          "columnIndex": 0
        },
        {
          "id": "nsc-h6",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "xs",
            "padding": 0,
            "children": [
              {
                "id": "nsc-h6-e",
                "type": "TextWidget",
                "props": {
                  "title": "COMMUNITY",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "",
                  "borderRadius": "none",
                  "titleEnabled": true,
                  "titleFontSize": "xs",
                  "titleAlignment": "left",
                  "titleFontWeight": "bold",
                  "descriptionColor": "foreground",
                  "descriptionFontSize": "sm",
                  "descriptionAlignment": "left",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 0
              },
              {
                "id": "nsc-h6-h",
                "type": "TextWidget",
                "props": {
                  "title": "#MyBrand",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "",
                  "borderRadius": "none",
                  "titleEnabled": true,
                  "titleFontSize": "4xl",
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
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        },
        {
          "id": "nsc-comm",
          "type": "ListWidget",
          "props": {
            "gap": "md",
            "items": [
              {
                "id": 1009,
                "kind": "video",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img23/1200/1500",
                "title": "Media item 9",
                "imageUrl": "https://picsum.photos/seed/img23/1200/1500",
                "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                "description": "Short caption."
              },
              {
                "id": 1010,
                "kind": "video",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img24/1200/1500",
                "title": "Media item 10",
                "imageUrl": "https://picsum.photos/seed/img24/1200/1500",
                "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                "description": "Short caption."
              },
              {
                "id": 1011,
                "kind": "video",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img25/1200/1500",
                "title": "Media item 11",
                "imageUrl": "https://picsum.photos/seed/img25/1200/1500",
                "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                "description": "Short caption."
              }
            ],
            "title": "",
            "columns": 3,
            "padding": 0,
            "listType": "unordered",
            "maxItems": 4,
            "showBadge": false,
            "background": {
              "type": "solid",
              "color": "transparent"
            },
            "scrollAxis": "vertical",
            "borderWidth": "none",
            "borderRadius": "none",
            "showMetaText": false,
            "titleEnabled": false,
            "itemTitleSize": "sm",
            "itemTitleColor": "foreground",
            "descriptionSize": "xs",
            "descriptionColor": "foreground",
            "imageAspectRatio": "portrait"
          },
          "columnIndex": 0
        },
        {
          "id": "nsc-ugc-row",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "md",
            "padding": 0,
            "children": [
              {
                "id": "nsc-ugc",
                "type": "droplet.ugc.drp_fuwamfg3licz1l4yocpkjos12t9vhcrh.MakeAVideoCta",
                "props": {
                  "sub": "Tell us what worked, what surprised you, or what you wish you knew sooner. Your honest experience can make the next person\u2019s choice clearer.",
                  "align": "left",
                  "bgColor": "foreground",
                  "bgImage": {
                    "id": "0",
                    "title": "tiktokreview",
                    "imageUrl": "https://picsum.photos/seed/img26/1200/1500",
                    "image_url": "https://picsum.photos/seed/img26/1200/1500",
                    "shareableType": "Asset (Image)"
                  },
                  "bgStyle": "gradient",
                  "eyebrow": "JOIN THE CONVERSATION",
                  "padding": "lg",
                  "showSub": true,
                  "ctaLabel": "Share your feedback",
                  "headline": "Your feedback helps someone else begin.",
                  "metaText": "A quick note or video \u00b7 no perfect script needed",
                  "showMeta": true,
                  "ctaVariant": "filled",
                  "openScreen": "screen-019efb31-be7d-7780-b74e-08a40ef22202",
                  "showEyebrow": true,
                  "buttonRadius": "pill",
                  "cornerRadius": "xl",
                  "showEyebrowIcon": true
                },
                "columnIndex": 0
              },
              {
                "id": "nsc-ugc-x1",
                "type": "VideoWidget",
                "props": {
                  "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                  "tag": "UGC",
                  "date": "",
                  "loop": false,
                  "muted": true,
                  "title": "Experience your best skin ever",
                  "author": "",
                  "poster": "https://picsum.photos/seed/img27/1200/1500",
                  "eyebrow": "REAL EXAMPLE",
                  "tagline": "From the community.",
                  "autoplay": false,
                  "controls": true,
                  "duration": "",
                  "displayFit": "cover",
                  "focusPoint": "center",
                  "frameColor": "foreground",
                  "borderColor": "muted",
                  "borderWidth": "none",
                  "displayMode": "inline",
                  "fixedHeight": "320px",
                  "borderRadius": "xl",
                  "useCustomUrl": true,
                  "editorialFrame": false,
                  "primaryCtaLink": "",
                  "primaryCtaText": "",
                  "verticalSizing": "fixed",
                  "secondaryCtaLink": "",
                  "secondaryCtaText": "",
                  "showFullscreenPill": false
                },
                "columnIndex": 1
              },
              {
                "id": "nsc-ugc-x2",
                "type": "VideoWidget",
                "props": {
                  "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                  "tag": "UGC",
                  "date": "",
                  "loop": false,
                  "muted": true,
                  "title": "Just 2 minutes a day",
                  "author": "",
                  "poster": "https://picsum.photos/seed/img15/1200/1500",
                  "eyebrow": "REAL EXAMPLE",
                  "tagline": "A fresh glow, daily.",
                  "autoplay": false,
                  "controls": true,
                  "duration": "",
                  "displayFit": "cover",
                  "focusPoint": "center",
                  "frameColor": "foreground",
                  "borderColor": "muted",
                  "borderWidth": "none",
                  "displayMode": "inline",
                  "fixedHeight": "320px",
                  "borderRadius": "xl",
                  "useCustomUrl": true,
                  "editorialFrame": false,
                  "primaryCtaLink": "",
                  "primaryCtaText": "",
                  "verticalSizing": "fixed",
                  "secondaryCtaLink": "",
                  "secondaryCtaText": "",
                  "showFullscreenPill": false
                },
                "columnIndex": 2
              }
            ],
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
          "id": "nsc-h7",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "xs",
            "padding": 0,
            "children": [
              {
                "id": "nsc-h7-e",
                "type": "TextWidget",
                "props": {
                  "title": "THE JOURNAL",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "",
                  "borderRadius": "none",
                  "titleEnabled": true,
                  "titleFontSize": "xs",
                  "titleAlignment": "left",
                  "titleFontWeight": "bold",
                  "descriptionColor": "foreground",
                  "descriptionFontSize": "sm",
                  "descriptionAlignment": "left",
                  "descriptionFontWeight": "normal"
                },
                "columnIndex": 0
              },
              {
                "id": "nsc-h7-h",
                "type": "TextWidget",
                "props": {
                  "title": "Skin science, decoded.",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "Insights and research from the [Brand] team.",
                  "borderRadius": "none",
                  "titleEnabled": true,
                  "titleFontSize": "4xl",
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
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        },
        {
          "id": "nsc-journal",
          "type": "ListWidget",
          "props": {
            "gap": "md",
            "items": [
              {
                "id": 1012,
                "kind": "image",
                "type": "EnrollmentPack",
                "image": "https://picsum.photos/seed/img28/1200/1500",
                "title": "Media item 12",
                "imageUrl": "https://picsum.photos/seed/img28/1200/1500",
                "share_link": "REPLACE_TARGET_URL",
                "canonical_url": "REPLACE_TARGET_URL",
                "shareableType": "EnrollmentPack",
                "shareable_type": "EnrollmentPack"
              },
              {
                "id": 1013,
                "kind": "image",
                "type": "EnrollmentPack",
                "image": "https://picsum.photos/seed/img29/1200/1500",
                "title": "Media item 13",
                "imageUrl": "https://picsum.photos/seed/img29/1200/1500",
                "share_link": "REPLACE_TARGET_URL",
                "canonical_url": "REPLACE_TARGET_URL",
                "shareableType": "EnrollmentPack",
                "shareable_type": "EnrollmentPack"
              },
              {
                "id": 1014,
                "kind": "image",
                "type": "EnrollmentPack",
                "image": "https://picsum.photos/seed/img11/1200/1500",
                "title": "Media item 14",
                "imageUrl": "https://picsum.photos/seed/img11/1200/1500",
                "share_link": "REPLACE_TARGET_URL",
                "canonical_url": "REPLACE_TARGET_URL",
                "shareableType": "EnrollmentPack",
                "shareable_type": "EnrollmentPack"
              },
              {
                "id": 1015,
                "kind": "image",
                "type": "EnrollmentPack",
                "image": "https://picsum.photos/seed/img30/1200/1500",
                "title": "Media item 15",
                "imageUrl": "https://picsum.photos/seed/img30/1200/1500",
                "share_link": "REPLACE_TARGET_URL",
                "canonical_url": "REPLACE_TARGET_URL",
                "shareableType": "EnrollmentPack",
                "shareable_type": "EnrollmentPack"
              }
            ],
            "title": "",
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
            "itemTitleColor": "foreground",
            "imageAspectRatio": "landscape"
          },
          "columnIndex": 0
        },
        {
          "id": "nsc-refer",
          "type": "CarouselWidget",
          "props": {
            "align": {
              "vertical": "bottom",
              "horizontal": "left"
            },
            "slides": [
              {
                "id": "nsc-refer-s",
                "title": "Good skin is better shared.",
                "content": {
                  "type": "ImageWidget",
                  "props": {
                    "src": "https://picsum.photos/seed/img31/1200/1500",
                    "useCustomUrl": true
                  }
                },
                "eyebrow": "FRIEND SHARE",
                "buttonLink": "/friend-share",
                "buttonText": "Refer a friend",
                "description": "Give a friend $25 off their first routine \u2014 and earn rewards toward yours. Everyone glows.",
                "buttonEnabled": true
              }
            ],
            "padding": 6,
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
            "borderRadius": "xl",
            "carouselHeight": "320px",
            "editorialFrame": false,
            "overlayEnabled": true,
            "enableAutoScroll": false,
            "overlayIntensity": 58
          },
          "columnIndex": 0
        }
      ],
      "background": {
        "type": "solid",
        "color": "transparent"
      },
      "sectionLayout": "single-column"
    }
  }
]
```
