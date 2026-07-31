# `component_tree` — Today — Partner dashboard

Post this as the screen's `component_tree` on the PUT, exactly as written —
it is already the array form the endpoint expects. Do not add another
wrapping array, and do not lift the single top-level LayoutWidget out of it:
that node is the page wrapper the live portal needs.
Placeholders are listed in the skill body; replace them before publishing.

```json
[
  {
    "id": "nst3-page",
    "type": "LayoutWidget",
    "props": {
      "gapSize": "lg",
      "padding": 6,
      "children": [
        {
          "id": "nst3-hero",
          "type": "CarouselWidget",
          "props": {
            "align": {
              "vertical": "center",
              "horizontal": "left"
            },
            "slides": [
              {
                "id": "nst3-hero-slide",
                "title": "One thoughtful move is enough.",
                "content": {
                  "type": "ImageWidget",
                  "props": {
                    "alt": "One thoughtful move is enough",
                    "src": "https://picsum.photos/seed/img01/1200/1500",
                    "altText": "One thoughtful move is enough",
                    "useCustomUrl": true
                  }
                },
                "eyebrow": "YOUR DAY  \u00b7  START HERE",
                "buttonLink": "/friend-share",
                "buttonText": "Start with one person",
                "description": "Follow up with someone. Share what worked. Then get on with your day.",
                "buttonEnabled": true,
                "accessibilityLabel": "One thoughtful move is enough"
              }
            ],
            "padding": 0,
            "textSize": "sm",
            "textColor": "background",
            "textWidth": "560px",
            "buttonSize": "md",
            "frameColor": "foreground",
            "headerSize": "2xl",
            "showButton": true,
            "borderWidth": "none",
            "buttonColor": "accent",
            "headerColor": "background",
            "overlayType": "gradient",
            "borderRadius": "lg",
            "carouselHeight": "380px",
            "editorialFrame": false,
            "overlayEnabled": true,
            "enableAutoScroll": false,
            "overlayIntensity": 50
          },
          "columnIndex": 0
        },
        {
          "id": "nst3-advice-card",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "sm",
            "padding": 4,
            "children": [
              {
                "id": "nst3-advice-stories",
                "type": "droplet.advice.drp_e5grnigflrffisqhuvqorhagdld9hw8j.Stories",
                "props": {
                  "dri": "YOUR_DRI_TOKEN",
                  "title": "Fresh advice",
                  "border": false,
                  "shadow": false,
                  "bgColor": "#F1F0F4",
                  "eyebrow": "A USEFUL NUDGE",
                  "openUrl": "",
                  "ringColor": "#081D27",
                  "textColor": "#081D27",
                  "apiBaseUrl": "https://advice-feed.vercel.app",
                  "fontFamily": "theme",
                  "accentColor": "#81B1E2",
                  "borderColor": "#F1F0F4",
                  "cornerRadius": "theme"
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
            "borderRadius": "md",
            "sectionLayout": "single-column"
          },
          "columnIndex": 0
        },
        {
          "id": "nstg-growth-grid",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "lg",
            "padding": 3,
            "children": [
              {
                "id": "nstg-left-stack",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "md",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nst3-move-card",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "md",
                        "padding": 5,
                        "children": [
                          {
                            "id": "nst10-move-header",
                            "type": "LayoutWidget",
                            "props": {
                              "gapSize": "sm",
                              "padding": 0,
                              "children": [
                                {
                                  "id": "nst3-move-label",
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
                                    "description": "TODAY / 12-MINUTE FOCUS",
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
                                  "id": "nst3-move-title",
                                  "type": "TextWidget",
                                  "props": {
                                    "title": "Make the next conversation useful.",
                                    "padding": 0,
                                    "background": {
                                      "type": "solid",
                                      "color": "transparent"
                                    },
                                    "titleColor": "background",
                                    "borderColor": "transparent",
                                    "borderWidth": "none",
                                    "description": "One person. One honest answer. One clear next step.",
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
                              "borderColor": "transparent",
                              "borderWidth": "none",
                              "borderRadius": "none",
                              "sectionLayout": "single-column"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nst10-focus-rail",
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
                              "description": "ONE PERSON   \u00b7   ONE STORY   \u00b7   ONE NEXT STEP",
                              "borderRadius": "md",
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
                            "id": "nst3-move-next-1",
                            "type": "LinkWidget",
                            "props": {
                              "href": "",
                              "size": "lg",
                              "text": "Share the [the device] routine  \u2192",
                              "padding": 0,
                              "variant": "secondary",
                              "fontSize": "sm",
                              "linkType": "screen",
                              "shareUrl": "",
                              "alignment": "left",
                              "fullWidth": false,
                              "underline": false,
                              "screenSlug": "screen-019efb90-67ec-7ec8-a743-b7b92ce28f3f",
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
                          },
                          {
                            "id": "nstg-todo",
                            "type": "LayoutWidget",
                            "props": {
                              "gapSize": "xs",
                              "padding": 0,
                              "children": [
                                {
                                  "id": "nstg-todo-title",
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
                                    "description": "FINISH WITH CARE",
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
                                  "id": "nstg-todo-followup",
                                  "type": "TextWidget",
                                  "props": {
                                    "title": "01  \u00b7  READY NOW",
                                    "padding": 3,
                                    "background": {
                                      "type": "solid",
                                      "color": "accent"
                                    },
                                    "titleColor": "foreground",
                                    "borderColor": "transparent",
                                    "borderWidth": "none",
                                    "description": "Send the [the device] follow-up  \u00b7  before 2:00 PM",
                                    "borderRadius": "md",
                                    "titleEnabled": true,
                                    "titleFontSize": "xs",
                                    "titleAlignment": "left",
                                    "titleFontWeight": "bold",
                                    "descriptionColor": "foreground",
                                    "descriptionFontSize": "sm",
                                    "descriptionAlignment": "left",
                                    "descriptionFontWeight": "bold"
                                  },
                                  "columnIndex": 0
                                },
                                {
                                  "id": "nstg-todo-story",
                                  "type": "TextWidget",
                                  "props": {
                                    "title": "02  \u00b7  FIVE HONEST MINUTES",
                                    "padding": 3,
                                    "background": {
                                      "type": "solid",
                                      "color": "transparent"
                                    },
                                    "titleColor": "accent",
                                    "borderColor": "muted",
                                    "borderWidth": "thin",
                                    "description": "Share one honest product story  \u00b7  5 minutes",
                                    "borderRadius": "md",
                                    "titleEnabled": true,
                                    "titleFontSize": "xs",
                                    "titleAlignment": "left",
                                    "titleFontWeight": "bold",
                                    "descriptionColor": "background",
                                    "descriptionFontSize": "sm",
                                    "descriptionAlignment": "left",
                                    "descriptionFontWeight": "bold"
                                  },
                                  "columnIndex": 0
                                },
                                {
                                  "id": "nstg-todo-demo",
                                  "type": "TextWidget",
                                  "props": {
                                    "title": "03  \u00b7  CLOSE THE LOOP",
                                    "padding": 3,
                                    "background": {
                                      "type": "solid",
                                      "color": "transparent"
                                    },
                                    "titleColor": "accent",
                                    "borderColor": "muted",
                                    "borderWidth": "thin",
                                    "description": "Confirm Thursday's product demo  \u00b7  today",
                                    "borderRadius": "md",
                                    "titleEnabled": true,
                                    "titleFontSize": "xs",
                                    "titleAlignment": "left",
                                    "titleFontWeight": "bold",
                                    "descriptionColor": "background",
                                    "descriptionFontSize": "sm",
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
                            "id": "nstg-todo-footnote",
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
                              "description": "3 MOVES  \u00b7  12 MINUTES  \u00b7  THEN STOP",
                              "borderRadius": "none",
                              "titleEnabled": false,
                              "titleFontSize": "xs",
                              "titleAlignment": "left",
                              "titleFontWeight": "bold",
                              "descriptionColor": "background",
                              "descriptionFontSize": "xs",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
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
                    },
                    {
                      "id": "nst3-calendar-card",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "sm",
                        "padding": 4,
                        "children": [
                          {
                            "id": "nst3-calendar-label",
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
                              "description": "PLAN THE DAY",
                              "borderRadius": "none",
                              "titleEnabled": false,
                              "titleFontSize": "xs",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "xs",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nst3-calendar",
                            "type": "CalendarWidget",
                            "props": {
                              "padding": 0,
                              "textColor": "foreground",
                              "titleText": "Calendar",
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "weekendDim": true,
                              "accentColor": "primary",
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "borderRadius": "none",
                              "titleEnabled": true,
                              "titleFontSize": "md",
                              "showTodayButton": true,
                              "showYearEyebrow": false,
                              "showEventDensity": true
                            },
                            "columnIndex": 0
                          }
                        ],
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
                      "id": "nst9-calendar-video",
                      "type": "VideoWidget",
                      "props": {
                        "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                        "tag": "HOW-TO",
                        "date": "",
                        "loop": false,
                        "muted": true,
                        "title": "The two-minute ritual, clearly explained",
                        "author": "",
                        "poster": "https://picsum.photos/seed/img02/1200/1500",
                        "eyebrow": "TODAY'S 3-MINUTE WATCH",
                        "tagline": "A clean demonstration to watch before your next customer conversation.",
                        "autoplay": false,
                        "controls": true,
                        "duration": "",
                        "displayFit": "cover",
                        "focusPoint": "center",
                        "frameColor": "foreground",
                        "borderColor": "muted",
                        "borderWidth": "none",
                        "displayMode": "card",
                        "fixedHeight": "240px",
                        "borderRadius": "md",
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
                "id": "nst8-middle-stack",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "md",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nst8-quick-share",
                      "type": "QuickShareWidget",
                      "props": {
                        "padding": 4,
                        "minHeight": "250px",
                        "textColor": "background",
                        "titleText": "Share today's [the device] routine",
                        "background": {
                          "type": "solid",
                          "color": "secondary"
                        },
                        "titleColor": "background",
                        "accentColor": "background",
                        "borderColor": "muted",
                        "borderWidth": "thin",
                        "overlayType": "gradient",
                        "borderRadius": "md",
                        "titleEnabled": true,
                        "buyButtonLink": "REPLACE_TARGET_URL",
                        "buyButtonText": "View Product",
                        "showBuyButton": false,
                        "titleFontSize": "lg",
                        "overlayEnabled": true,
                        "overlayIntensity": 65,
                        "showDomainPrefix": true,
                        "showResourceType": true,
                        "showShareActions": true,
                        "shareableResource": {
                          "id": 76695,
                          "title": "The Starter Kit",
                          "images": [
                            {
                              "alt": "Refer a friend",
                              "url": "https://picsum.photos/seed/img03/1200/1500"
                            }
                          ],
                          "status": "active",
                          "imageUrl": "https://picsum.photos/seed/img03/1200/1500",
                          "image_url": "https://picsum.photos/seed/img03/1200/1500",
                          "shareLink": "https://yourstore.fluid.app/s/11b50c",
                          "created_at": "Jun 23, 2026",
                          "share_link": "https://yourstore.fluid.app/s/11b50c",
                          "description": "<p>The BREAKTHROUGH Stack includes three natural peptides that help flip the switch on strength, metabolism, and deep sleep.</p><p></p><p>Break the cycle with:</p><p>FIT for strength &amp; performance</p><p>LEAN for cravings &amp; body composition</p><p>RESTORED for deep sleep &amp; real recovery.</p><p></p><p>Better performance. Better sleep. Better days. It\u2019s time to shift.</p><p></p><p>First-time purchasers will receive a complimentary [Brand]-branded water bottle and collection box on their first order.</p>",
                          "retailPrice": null,
                          "wholesaleCv": null,
                          "wholesaleQv": null,
                          "retail_price": null,
                          "wholesale_cv": 0,
                          "wholesale_qv": 0,
                          "shareableType": "Product",
                          "shareable_type": "Product",
                          "wholesalePrice": null,
                          "wholesale_price": null
                        }
                      },
                      "columnIndex": 0
                    },
                    {
                      "id": "nstg-table-panel",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "md",
                        "padding": 4,
                        "children": [
                          {
                            "id": "nstg-table-label",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "accent",
                              "borderWidth": "none",
                              "description": "CONVERSATION PIPELINE",
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
                            "id": "nstg-table-title",
                            "type": "TextWidget",
                            "props": {
                              "title": "Where momentum is building.",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "Scan the signal, make the next useful move, and keep the relationship human.",
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
                          },
                          {
                            "id": "nstg-table-signals",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 3,
                              "background": {
                                "type": "solid",
                                "color": "secondary"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "4 ready now   \u00b7   3 follow-ups   \u00b7   2 demos booked",
                              "borderRadius": "md",
                              "titleEnabled": false,
                              "titleFontSize": "sm",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "foreground",
                              "descriptionFontSize": "sm",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nstg-conversation-table",
                            "type": "TableWidget",
                            "props": {
                              "data": [
                                {
                                  "id": 1,
                                  "signal": "Ready",
                                  "next_move": "Send product page",
                                  "conversation": "[the device] routine"
                                },
                                {
                                  "id": 2,
                                  "signal": "Warm",
                                  "next_move": "Share comparison",
                                  "conversation": "Brightening serum"
                                },
                                {
                                  "id": 3,
                                  "signal": "New",
                                  "next_move": "Follow up Thursday",
                                  "conversation": "[supplement]"
                                },
                                {
                                  "id": 4,
                                  "signal": "Booked",
                                  "next_move": "Confirm 3:00 PM",
                                  "conversation": "PRYSM scan"
                                },
                                {
                                  "id": 5,
                                  "signal": "Customer",
                                  "next_move": "Check in Friday",
                                  "conversation": "Subscription"
                                },
                                {
                                  "id": 6,
                                  "signal": "Curious",
                                  "next_move": "Answer ingredient question",
                                  "conversation": "[supplement]"
                                },
                                {
                                  "id": 7,
                                  "signal": "Viewed",
                                  "next_move": "Send demo clip",
                                  "conversation": "Rose Gold iO"
                                },
                                {
                                  "id": 8,
                                  "signal": "Returning",
                                  "next_move": "Review routine",
                                  "conversation": "Meta bundle"
                                },
                                {
                                  "id": 9,
                                  "signal": "Interested",
                                  "next_move": "Share ingredient guide",
                                  "conversation": "Tru Face line"
                                },
                                {
                                  "id": 10,
                                  "signal": "Warm",
                                  "next_move": "Book a 10-minute call",
                                  "conversation": "Wellness reset"
                                },
                                {
                                  "id": 11,
                                  "signal": "Reorder",
                                  "next_move": "Send restock link",
                                  "conversation": "Body Bar"
                                },
                                {
                                  "id": 12,
                                  "signal": "New",
                                  "next_move": "Share simple regimen",
                                  "conversation": "Clear Action"
                                },
                                {
                                  "id": 13,
                                  "signal": "Referred",
                                  "next_move": "Thank referrer",
                                  "conversation": "Epoch care"
                                }
                              ],
                              "columns": [
                                {
                                  "key": "conversation",
                                  "label": "Conversation",
                                  "sortable": true
                                },
                                {
                                  "key": "signal",
                                  "label": "Signal",
                                  "sortable": true
                                },
                                {
                                  "key": "next_move",
                                  "label": "Next move",
                                  "sortable": false
                                }
                              ],
                              "padding": 0,
                              "textColor": "foreground",
                              "titleText": "Today's conversations",
                              "background": {
                                "type": "solid",
                                "color": "background"
                              },
                              "titleColor": "foreground",
                              "borderColor": "muted",
                              "borderWidth": "none",
                              "borderRadius": "none",
                              "titleEnabled": false,
                              "filterEnabled": false,
                              "titleFontSize": "md",
                              "maxRowsPerPage": 13,
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
                          "color": "background"
                        },
                        "borderColor": "muted",
                        "borderWidth": "thin",
                        "borderRadius": "md",
                        "sectionLayout": "single-column"
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
                "columnIndex": 1
              },
              {
                "id": "nstg-right-stack",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "md",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nstg-points",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "md",
                        "padding": 5,
                        "children": [
                          {
                            "id": "nstg-points-label",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "accent",
                              "borderWidth": "none",
                              "description": "GROWTH POINTS \u00b7 JULY",
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
                            "id": "nstg-points-title",
                            "type": "TextWidget",
                            "props": {
                              "title": "1,240 points",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "background",
                              "borderWidth": "none",
                              "description": "760 points to the next milestone. Every credited share, order, and follow-up keeps the path visible.",
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
                          },
                          {
                            "id": "nstg-points-signals",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 3,
                              "background": {
                                "type": "solid",
                                "color": "accent"
                              },
                              "titleColor": "primary",
                              "borderWidth": "none",
                              "description": "+320 this month   \u00b7   8 shares credited   \u00b7   4 orders influenced",
                              "borderRadius": "md",
                              "titleEnabled": false,
                              "titleFontSize": "sm",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "primary",
                              "descriptionFontSize": "sm",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nstg-points-link",
                            "type": "LinkWidget",
                            "props": {
                              "size": "md",
                              "text": "View points history  \u2192",
                              "variant": "secondary",
                              "linkType": "screen",
                              "alignment": "center",
                              "fullWidth": true,
                              "screenSlug": "profile"
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
                    },
                    {
                      "id": "nstg-ugc-nested",
                      "type": "NestedWidget",
                      "props": {
                        "gap": "sm",
                        "padding": 4,
                        "resource": {
                          "id": 1001,
                          "alt": "The device inside my routine",
                          "kind": "video",
                          "type": "Medium",
                          "image": "https://picsum.photos/seed/img04/1200/1500",
                          "title": "Media item 1",
                          "altText": "The device inside my routine",
                          "imageUrl": "https://picsum.photos/seed/img04/1200/1500",
                          "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                          "description": ""
                        },
                        "titleText": "UGC people are watching",
                        "background": {
                          "type": "solid",
                          "color": "background"
                        },
                        "shareables": [
                          {
                            "id": 1002,
                            "alt": "The ritual I keep coming back to",
                            "kind": "video",
                            "type": "Medium",
                            "image": "https://picsum.photos/seed/img05/1200/1500",
                            "title": "Media item 2",
                            "altText": "The ritual I keep coming back to",
                            "imageUrl": "https://picsum.photos/seed/img05/1200/1500",
                            "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                            "description": ""
                          },
                          {
                            "id": 1003,
                            "alt": "Two minutes in my morning",
                            "kind": "video",
                            "type": "Medium",
                            "image": "https://picsum.photos/seed/img06/1200/1500",
                            "title": "Media item 3",
                            "altText": "Two minutes in my morning",
                            "imageUrl": "https://picsum.photos/seed/img06/1200/1500",
                            "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                            "description": ""
                          },
                          {
                            "id": 1004,
                            "alt": "What the clean finish feels like",
                            "kind": "video",
                            "type": "Medium",
                            "image": "https://picsum.photos/seed/img07/1200/1500",
                            "title": "Media item 4",
                            "altText": "What the clean finish feels like",
                            "imageUrl": "https://picsum.photos/seed/img07/1200/1500",
                            "videoUrl": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                            "description": ""
                          }
                        ],
                        "titleColor": "background",
                        "borderColor": "muted",
                        "borderWidth": "thin",
                        "overlayType": "gradient",
                        "borderRadius": "md",
                        "titleEnabled": true,
                        "titleFontSize": "lg",
                        "overlayEnabled": true,
                        "titleAlignment": {
                          "vertical": "bottom",
                          "horizontal": "left"
                        },
                        "nestedTextColor": "foreground",
                        "overlayIntensity": 52,
                        "primaryMediaHeight": "760px"
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
              "color": "secondary"
            },
            "borderColor": "muted",
            "borderWidth": "thin",
            "borderRadius": "md",
            "sectionLayout": "3c-equal"
          },
          "columnIndex": 0
        },
        {
          "id": "nstg-top-sellers",
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
                "title": "Featured Product 1",
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
                "title": "Featured Product 2",
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
                "title": "Featured Product 3",
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
                "title": "Featured Product 4",
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
                "title": "Featured Product 5",
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
            "title": "Top sellers",
            "columns": 5,
            "padding": 5,
            "listType": "unordered",
            "maxItems": 5,
            "priceSize": "md",
            "showBadge": true,
            "titleSize": "xl",
            "background": {
              "type": "solid",
              "color": "secondary"
            },
            "priceColor": "foreground",
            "scrollAxis": "vertical",
            "titleColor": "foreground",
            "borderColor": "muted",
            "borderWidth": "thin",
            "borderRadius": "md",
            "metaTextSize": "xs",
            "showMetaText": false,
            "titleEnabled": true,
            "itemTitleSize": "sm",
            "metaTextColor": "muted",
            "itemTitleColor": "foreground",
            "descriptionSize": "xs",
            "descriptionColor": "foreground",
            "imageAspectRatio": "square",
            "originalPriceColor": "muted"
          },
          "columnIndex": 0
        },
        {
          "id": "nst3-proof-banner",
          "type": "CarouselWidget",
          "props": {
            "align": {
              "vertical": "center",
              "horizontal": "center"
            },
            "slides": [
              {
                "id": "nst3-proof-banner-slide",
                "title": "Small, clear, human. That is enough to build on.",
                "content": {
                  "type": "ImageWidget",
                  "props": {
                    "alt": "Small, clear, human. That is enough to build on",
                    "src": "https://picsum.photos/seed/img12/1200/1500",
                    "altText": "Small, clear, human. That is enough to build on",
                    "useCustomUrl": true
                  }
                },
                "eyebrow": "THE DAILY RHYTHM",
                "buttonLink": "/friend-share",
                "buttonText": "",
                "description": "The best partner experience leaves room for a life beyond the dashboard.",
                "buttonEnabled": false,
                "accessibilityLabel": "Small, clear, human. That is enough to build on"
              }
            ],
            "padding": 0,
            "textSize": "sm",
            "textColor": "background",
            "textWidth": "700px",
            "buttonSize": "md",
            "frameColor": "foreground",
            "headerSize": "xl",
            "showButton": false,
            "borderWidth": "none",
            "buttonColor": "background",
            "headerColor": "background",
            "overlayType": "solid",
            "borderRadius": "lg",
            "carouselHeight": "280px",
            "editorialFrame": false,
            "overlayEnabled": true,
            "enableAutoScroll": false,
            "overlayIntensity": 46
          },
          "columnIndex": 0
        },
        {
          "id": "nst7-product-videos",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "lg",
            "padding": 5,
            "children": [
              {
                "id": "nst7-product-video-intro",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "sm",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nst7-product-video-label",
                      "type": "TextWidget",
                      "props": {
                        "title": "",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "accent",
                        "borderWidth": "none",
                        "description": "PRODUCT STORIES \u00b7 READY TO LEARN OR SHARE",
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
                      "id": "nst7-product-video-title",
                      "type": "TextWidget",
                      "props": {
                        "title": "Three product stories. Three ways in.",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "foreground",
                        "borderWidth": "none",
                        "description": "See the device, understand the two-minute ritual, and hear the customer language that makes the benefit easy to share.",
                        "borderRadius": "none",
                        "titleEnabled": true,
                        "titleFontSize": "2xl",
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
                "id": "nst7-product-video-grid",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "md",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nst7-video-lumispa",
                      "type": "VideoWidget",
                      "props": {
                        "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                        "tag": "DEMO",
                        "date": "",
                        "loop": false,
                        "muted": true,
                        "title": "[the device] iO in a real routine",
                        "author": "",
                        "poster": "https://picsum.photos/seed/img04/1200/1500",
                        "eyebrow": "01 / SHOW THE DEVICE",
                        "tagline": "See how the device moves and how naturally it fits into daily care.",
                        "autoplay": false,
                        "controls": true,
                        "duration": "",
                        "displayFit": "cover",
                        "focusPoint": "center",
                        "frameColor": "foreground",
                        "borderColor": "muted",
                        "borderWidth": "none",
                        "displayMode": "card",
                        "fixedHeight": "320px",
                        "borderRadius": "md",
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
                      "id": "nst7-video-collagen",
                      "type": "VideoWidget",
                      "props": {
                        "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                        "tag": "HOW-TO",
                        "date": "",
                        "loop": false,
                        "muted": true,
                        "title": "The two-minute ritual",
                        "author": "",
                        "poster": "https://picsum.photos/seed/img06/1200/1500",
                        "eyebrow": "02 / EXPLAIN THE RITUAL",
                        "tagline": "A concise explanation customers can understand and remember.",
                        "autoplay": false,
                        "controls": true,
                        "duration": "",
                        "displayFit": "cover",
                        "focusPoint": "center",
                        "frameColor": "foreground",
                        "borderColor": "muted",
                        "borderWidth": "none",
                        "displayMode": "card",
                        "fixedHeight": "320px",
                        "borderRadius": "md",
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
                      "id": "nst7-video-prysm",
                      "type": "VideoWidget",
                      "props": {
                        "src": "https://REPLACE-WITH-YOUR-CDN/video.mp4",
                        "tag": "ANSWER THIS",
                        "date": "",
                        "loop": false,
                        "muted": true,
                        "title": "What clean skin feels like",
                        "author": "",
                        "poster": "https://picsum.photos/seed/img07/1200/1500",
                        "eyebrow": "03 / SHARE THE FINISH",
                        "tagline": "A real product moment that answers the comfort and finish question.",
                        "autoplay": false,
                        "controls": true,
                        "duration": "",
                        "displayFit": "cover",
                        "focusPoint": "center",
                        "frameColor": "foreground",
                        "borderColor": "muted",
                        "borderWidth": "none",
                        "displayMode": "card",
                        "fixedHeight": "320px",
                        "borderRadius": "md",
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
          "id": "nst3-closing",
          "type": "LayoutWidget",
          "props": {
            "gapSize": "lg",
            "padding": 6,
            "children": [
              {
                "id": "nst3-closing-intro",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "sm",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nst3-closing-label",
                      "type": "TextWidget",
                      "props": {
                        "title": "",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "accent",
                        "borderWidth": "none",
                        "description": "CLOSE THE DAY WITH INTENTION",
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
                      "id": "nst3-closing-title",
                      "type": "TextWidget",
                      "props": {
                        "title": "That's enough for today.",
                        "padding": 0,
                        "background": {
                          "type": "solid",
                          "color": "transparent"
                        },
                        "titleColor": "background",
                        "borderWidth": "none",
                        "description": "A good partner day is not measured by how much stayed open. It is measured by the few things you finished with care.",
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
                "id": "nst3-closing-grid",
                "type": "LayoutWidget",
                "props": {
                  "gapSize": "md",
                  "padding": 0,
                  "children": [
                    {
                      "id": "nst3-close-1",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "sm",
                        "padding": 5,
                        "children": [
                          {
                            "id": "nst3-close-1-icon",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "accent",
                              "borderWidth": "none",
                              "description": "\u2197",
                              "borderRadius": "none",
                              "titleEnabled": false,
                              "titleFontSize": "2xl",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "accent",
                              "descriptionFontSize": "2xl",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nst3-close-1-label",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "accent",
                              "borderWidth": "none",
                              "description": "01 / CLOSE THE LOOP",
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
                            "id": "nst3-close-1-copy",
                            "type": "TextWidget",
                            "props": {
                              "title": "Send the useful follow-up.",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "Answer the question while the context is still warm\u2014and stop before it becomes a pitch.",
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
                      "id": "nst3-close-2",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "sm",
                        "padding": 5,
                        "children": [
                          {
                            "id": "nst3-close-2-icon",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "accent",
                              "borderWidth": "none",
                              "description": "\u25c9",
                              "borderRadius": "none",
                              "titleEnabled": false,
                              "titleFontSize": "2xl",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "accent",
                              "descriptionFontSize": "2xl",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nst3-close-2-label",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "accent",
                              "borderWidth": "none",
                              "description": "02 / SHARE SOMETHING REAL",
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
                            "id": "nst3-close-2-copy",
                            "type": "TextWidget",
                            "props": {
                              "title": "Choose the honest story.",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "One unpolished routine earns more attention than another perfect piece of content.",
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
                        "background": {
                          "type": "solid",
                          "color": "background"
                        },
                        "borderColor": "muted",
                        "borderWidth": "none",
                        "borderRadius": "md",
                        "sectionLayout": "single-column"
                      },
                      "columnIndex": 1
                    },
                    {
                      "id": "nst3-close-3",
                      "type": "LayoutWidget",
                      "props": {
                        "gapSize": "sm",
                        "padding": 5,
                        "children": [
                          {
                            "id": "nst3-close-3-icon",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "accent",
                              "borderWidth": "none",
                              "description": "\u263e",
                              "borderRadius": "none",
                              "titleEnabled": false,
                              "titleFontSize": "2xl",
                              "titleAlignment": "left",
                              "titleFontWeight": "normal",
                              "descriptionColor": "accent",
                              "descriptionFontSize": "2xl",
                              "descriptionAlignment": "left",
                              "descriptionFontWeight": "bold"
                            },
                            "columnIndex": 0
                          },
                          {
                            "id": "nst3-close-3-label",
                            "type": "TextWidget",
                            "props": {
                              "title": "",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "accent",
                              "borderWidth": "none",
                              "description": "03 / LEAVE ROOM",
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
                            "id": "nst3-close-3-copy",
                            "type": "TextWidget",
                            "props": {
                              "title": "Let tomorrow stay tomorrow.",
                              "padding": 0,
                              "background": {
                                "type": "solid",
                                "color": "transparent"
                              },
                              "titleColor": "foreground",
                              "borderWidth": "none",
                              "description": "Save what can wait, close the dashboard, and make room for the life this work supports.",
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
                        "background": {
                          "type": "solid",
                          "color": "background"
                        },
                        "borderColor": "muted",
                        "borderWidth": "none",
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
              },
              {
                "id": "nst3-closing-footnote",
                "type": "TextWidget",
                "props": {
                  "title": "",
                  "padding": 0,
                  "background": {
                    "type": "solid",
                    "color": "transparent"
                  },
                  "titleColor": "background",
                  "borderWidth": "none",
                  "description": "Tomorrow starts lighter when today ends clearly.",
                  "borderRadius": "none",
                  "titleEnabled": false,
                  "titleFontSize": "sm",
                  "titleAlignment": "left",
                  "titleFontWeight": "normal",
                  "descriptionColor": "background",
                  "descriptionFontSize": "sm",
                  "descriptionAlignment": "left",
                  "descriptionFontWeight": "bold"
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
