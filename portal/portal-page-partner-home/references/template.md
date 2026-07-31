# `component_tree` — Home — Daily driver

Post this as the screen's `component_tree` on the PUT, exactly as written —
it is already the array form the endpoint expects. Do not add another
wrapping array, and do not lift the single top-level LayoutWidget out of it:
that node is the page wrapper the live portal needs.
Placeholders are listed in the skill body; replace them before publishing.

```json
[
  {
    "id": "nsh1-page",
    "type": "LayoutWidget",
    "props": {
      "gapSize": "xl",
      "padding": 4,
      "children": [
        {
          "id": "nsh1-hero",
          "type": "CarouselWidget",
          "props": {
            "align": {
              "vertical": "center",
              "horizontal": "left"
            },
            "slides": [
              {
                "id": "nsh1-hero-s1",
                "title": "Welcome back. Let's make today count.",
                "content": {
                  "type": "ImageWidget",
                  "props": {
                    "src": "https://picsum.photos/seed/img32/1200/1500",
                    "useCustomUrl": true
                  }
                },
                "eyebrow": "YOUR DAILY HOME",
                "buttonLink": "/the-hub",
                "buttonText": "Open my share kit",
                "description": "One share, one follow-up, one thing learned \u2014 that's a great day. Everything you need is on this page.",
                "buttonEnabled": true,
                "secondaryButtonLink": "/the-hub",
                "secondaryButtonText": "This week's call"
              },
              {
                "id": "nsh1-hero-s2",
                "title": "The Rose Gold Edition is moving fast.",
                "content": {
                  "type": "ImageWidget",
                  "props": {
                    "src": "https://picsum.photos/seed/img20/1200/1500",
                    "useCustomUrl": true
                  }
                },
                "eyebrow": "JUST DROPPED \u00b7 LIMITED",
                "buttonLink": "/share/products",
                "buttonText": "Share the Rose Gold",
                "description": "[Product Name] \u2014 the product your feed wants to see. Share it while it's news.",
                "buttonEnabled": true
              },
              {
                "id": "nsh1-hero-s3",
                "title": "[Your Event] \u2014 seats are open.",
                "content": {
                  "type": "ImageWidget",
                  "props": {
                    "src": "https://picsum.photos/seed/img33/1200/1500",
                    "useCustomUrl": true
                  }
                },
                "eyebrow": "EVENT \u00b7 REGISTRATION OPEN",
                "buttonLink": "/the-hub",
                "buttonText": "Save my seat",
                "description": "Three days with the leaders who've done it. Teams that go, grow.",
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
          "id": "nsh1-st",
          "type": "droplet.advice.drp_e5grnigflrffisqhuvqorhagdld9hw8j.Stories",
          "props": {
            "dri": "YOUR_DRI_TOKEN",
            "title": "Fresh advice from the team",
            "border": false,
            "shadow": false,
            "bgColor": "#ffffff",
            "eyebrow": "JUST DROPPED",
            "openUrl": "",
            "ringColor": "",
            "textColor": "#000000",
            "apiBaseUrl": "https://advice-feed.vercel.app",
            "fontFamily": "theme",
            "accentColor": "",
            "borderColor": "",
            "cornerRadius": "theme"
          },
          "columnIndex": 0
        },
        {
          "id": "nsh1-h1",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "xs",
            "padding": 0,
            "children": [
              {
                "id": "nsh1-h1-e",
                "type": "TextWidget",
                "props": {
                  "title": "YOUR TOOLKIT",
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
                "id": "nsh1-h1-h",
                "type": "TextWidget",
                "props": {
                  "title": "One link. Everything follows.",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "Your share link, your tools, your rewards \u2014 the daily essentials.",
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
          "id": "nsh1-share",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "lg",
            "padding": 0,
            "children": [
              {
                "id": "nsh1-qs",
                "type": "QuickShareWidget",
                "props": {
                  "padding": 5,
                  "titleText": "Share the Ageless Kit \u2014 your link",
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
                    "name": "Featured Product 12",
                    "slug": "US-kit-beauty-focus-collagen-plus-ageloc-youth-ageloc-meta-nu-biome-subscription-kit-US",
                    "type": "Product",
                    "price": "$00.00",
                    "title": "Featured Product 12",
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
                "id": "nsh1-h3",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "xs",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nsh1-h3-e",
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
                      "id": "nsh1-h3-h",
                      "type": "TextWidget",
                      "props": {
                        "title": "For their wellness.",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "description": "[nutrition line] nutrition that works from within.",
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
                "id": "nsh1-well",
                "type": "ListWidget",
                "props": {
                  "gap": "sm",
                  "items": [
                    {
                      "id": "REPLACE_PRODUCT_ID",
                      "type": "Product",
                      "title": "Featured Product 13",
                      "status": "active",
                      "imageUrl": "https://picsum.photos/seed/img10/1200/1500",
                      "description": "One-line product description goes here.",
                      "display_price": "$00.00"
                    },
                    {
                      "id": "REPLACE_PRODUCT_ID",
                      "type": "Product",
                      "title": "Featured Product 14",
                      "status": "active",
                      "imageUrl": "https://picsum.photos/seed/img11/1200/1500",
                      "description": "One-line product description goes here.",
                      "display_price": "$00.00"
                    },
                    {
                      "id": "REPLACE_PRODUCT_ID",
                      "type": "Product",
                      "title": "Featured Product 15",
                      "status": "active",
                      "imageUrl": "https://picsum.photos/seed/img34/1200/1500",
                      "description": "One-line product description goes here.",
                      "display_price": "$00.00"
                    }
                  ],
                  "title": "",
                  "columns": 3,
                  "padding": 0,
                  "listType": "unordered",
                  "maxItems": 6,
                  "priceSize": "sm",
                  "showBadge": false,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "priceColor": "background",
                  "scrollAxis": "vertical",
                  "borderWidth": "none",
                  "showMetaText": false,
                  "titleEnabled": false,
                  "itemTitleSize": "xs",
                  "itemTitleColor": "background",
                  "descriptionSize": "xs",
                  "descriptionColor": "background",
                  "imageAspectRatio": "square"
                },
                "columnIndex": 0
              },
              {
                "id": "nsh1-shopall",
                "type": "LinkWidget",
                "props": {
                  "size": "md",
                  "text": "Open the full catalog \u2192",
                  "variant": "link",
                  "linkType": "screen",
                  "alignment": "left",
                  "fullWidth": false,
                  "screenSlug": "share/products"
                },
                "columnIndex": 0
              },
              {
                "id": "nsh1-tkcol",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "md",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nsh1-tk",
                      "type": "QuickLinksWidget",
                      "props": {
                        "title": "Partner toolkit",
                        "layout": "list",
                        "padding": 0,
                        "link1Url": "my-product-pages",
                        "link2Url": "friend-share",
                        "link3Url": "the-hub",
                        "link4Url": "share/products",
                        "link5Url": "#",
                        "link6Url": "#",
                        "link7Url": "#",
                        "link8Url": "#",
                        "link1Icon": "Globe",
                        "link2Icon": "Gift",
                        "link3Icon": "Bookmark",
                        "link4Icon": "ShoppingBag",
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
                        "link1Label": "My product pages",
                        "link2Color": "primary",
                        "link2Label": "Friend Share",
                        "link3Color": "primary",
                        "link3Label": "The Hub \u2014 calls & training",
                        "link4Color": "primary",
                        "link4Label": "Full catalog",
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
                      "id": "nsh1-pts",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "sm",
                        "padding": 4,
                        "children": [
                          {
                            "id": "nsh1-pts-label",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "background",
                              "borderColor": "transparent",
                              "borderWidth": "none",
                              "description": "REWARDS \u00b7 JULY",
                              "borderRadius": "none",
                              "titleEnabled": false,
                              "titleFontSize": "xl",
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
                            "id": "nsh1-pts-balance",
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
                              "description": "760 points to your next milestone. Your credited shares and orders update here.",
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
                            "id": "nsh1-pts-progress",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 2,
                              "background": {
                                "type": "solid",
                                "color": "accent"
                              },
                              "titleColor": "background",
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
                            "id": "nsh1-pts-link",
                            "type": "LinkWidget",
                            "props": {
                              "size": "sm",
                              "text": "View rewards activity  \u2192",
                              "variant": "secondary",
                              "linkType": "screen",
                              "alignment": "left",
                              "fullWidth": false,
                              "screenSlug": "profile",
                              "borderWidth": "none",
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
                      "columnIndex": 0
                    }
                  ],
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "borderWidth": "none",
                  "borderRadius": "xl",
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
          "id": "nsh1-h5",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "xs",
            "padding": 0,
            "children": [
              {
                "id": "nsh1-h5-e",
                "type": "TextWidget",
                "props": {
                  "title": "CONTENT",
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
                "id": "nsh1-h5-h",
                "type": "TextWidget",
                "props": {
                  "title": "Tonight's post, done.",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "foreground",
                  "borderWidth": "none",
                  "description": "Ready-to-share content \u2014 captioned, branded, yours.",
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
          "id": "nsh1-media",
          "type": "ListWidget",
          "props": {
            "gap": "md",
            "items": [
              {
                "id": 1016,
                "kind": "video",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img04/1200/1500",
                "title": "Media item 16",
                "imageUrl": "https://picsum.photos/seed/img04/1200/1500",
                "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                "description": ""
              },
              {
                "id": 1017,
                "kind": "video",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img05/1200/1500",
                "title": "Media item 17",
                "imageUrl": "https://picsum.photos/seed/img05/1200/1500",
                "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                "description": ""
              },
              {
                "id": 1018,
                "kind": "video",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img06/1200/1500",
                "title": "Media item 18",
                "imageUrl": "https://picsum.photos/seed/img06/1200/1500",
                "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                "description": ""
              },
              {
                "id": 1019,
                "kind": "video",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img07/1200/1500",
                "title": "Media item 19",
                "imageUrl": "https://picsum.photos/seed/img07/1200/1500",
                "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                "description": ""
              },
              {
                "id": 1020,
                "kind": "video",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img14/1200/1500",
                "title": "Media item 20",
                "imageUrl": "https://picsum.photos/seed/img14/1200/1500",
                "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                "description": ""
              },
              {
                "id": 1021,
                "kind": "video",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img15/1200/1500",
                "title": "Media item 21",
                "imageUrl": "https://picsum.photos/seed/img15/1200/1500",
                "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                "description": ""
              }
            ],
            "columns": 3,
            "padding": 2,
            "listType": "unordered",
            "maxItems": 7,
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
            "imageAspectRatio": "square"
          },
          "columnIndex": 0
        },
        {
          "id": "nsh1-ugc-row",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "lg",
            "padding": 0,
            "children": [
              {
                "id": "nsh1-ugc",
                "type": "droplet.ugc.drp_fuwamfg3licz1l4yocpkjos12t9vhcrh.MakeAVideoCta",
                "props": {
                  "sub": "Pick a prompt, hit record, talk like you would to a friend. 60 seconds is plenty.",
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
                  "eyebrow": "TONIGHT'S POST",
                  "padding": "lg",
                  "showSub": true,
                  "ctaLabel": "Make a video",
                  "headline": "Your story sells better than any ad.",
                  "metaText": "No script \u00b7 no editing \u00b7 just you",
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
                "id": "nsh1-ugc-x1",
                "type": "VideoWidget",
                "props": {
                  "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                  "tag": "UGC",
                  "title": "A flight attendant's travel ritual",
                  "poster": "https://picsum.photos/seed/img35/1200/1500",
                  "eyebrow": "REAL EXAMPLE",
                  "tagline": "Glow at 30,000 feet \u2014 real example.",
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
                "id": "nsh1-ugc-x2",
                "type": "VideoWidget",
                "props": {
                  "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                  "tag": "UGC",
                  "title": "My secret 2-minute facial hack",
                  "poster": "https://picsum.photos/seed/img36/1200/1500",
                  "eyebrow": "REAL EXAMPLE",
                  "tagline": "Zero effort, all glow.",
                  "frameColor": "foreground",
                  "displayMode": "card",
                  "borderRadius": "xl",
                  "useCustomUrl": true,
                  "editorialFrame": true,
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
          "id": "nsh1-h6",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "xs",
            "padding": 0,
            "children": [
              {
                "id": "nsh1-h6-e",
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
                "id": "nsh1-h6-h",
                "type": "TextWidget",
                "props": {
                  "title": "Proof in the wild.",
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
          "id": "nsh1-spots",
          "type": "ListWidget",
          "props": {
            "gap": "md",
            "items": [
              {
                "id": 1022,
                "kind": "video",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img23/1200/1500",
                "title": "Media item 22",
                "imageUrl": "https://picsum.photos/seed/img23/1200/1500",
                "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                "description": "Short caption."
              },
              {
                "id": 1023,
                "kind": "video",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img24/1200/1500",
                "title": "Media item 23",
                "imageUrl": "https://picsum.photos/seed/img24/1200/1500",
                "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                "description": "Short caption."
              },
              {
                "id": 1024,
                "kind": "video",
                "type": "Medium",
                "image": "https://picsum.photos/seed/img25/1200/1500",
                "title": "Media item 24",
                "imageUrl": "https://picsum.photos/seed/img25/1200/1500",
                "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                "description": "Short caption."
              }
            ],
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
          "id": "nsh1-path",
          "type": "CarouselWidget",
          "props": {
            "align": {
              "vertical": "bottom",
              "horizontal": "left"
            },
            "slides": [
              {
                "id": "nsh1-path-s",
                "title": "Affiliate. Builder. Coach. Director.",
                "content": {
                  "type": "ImageWidget",
                  "props": {
                    "src": "https://picsum.photos/seed/img33/1200/1500",
                    "useCustomUrl": true
                  }
                },
                "eyebrow": "THE PATH",
                "buttonLink": "/the-hub",
                "buttonText": "See how growth works",
                "description": "Every Director you'll meet at [Your Event] started with one honest share. The next rank is closer than it looks.",
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
