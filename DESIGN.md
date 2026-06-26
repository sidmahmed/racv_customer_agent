---
version: alpha
name: RACV Modern
description: A confident, service-oriented system with bright blue brand surfaces and a high-visibility yellow accent.
colors:
  primary: "#0067F6"
  secondary: "#001657"
  tertiary: "#F8DB00"
  neutral: "#FFFFFF"
  surface: "#F6F5F1"
  on-surface: "#121212"
  error: "#D92D20"
  border: "#D9DDE5"
  muted: "#667085"
  card: "#FFFFFF"
typography:
  headline-display:
    fontFamily: Poppins
    fontSize: 40px
    fontWeight: 400
    lineHeight: 1.1
    letterSpacing: 0px
  headline-lg:
    fontFamily: Poppins
    fontSize: 28px
    fontWeight: 400
    lineHeight: 40px
    letterSpacing: 0px
  headline-md:
    fontFamily: Poppins
    fontSize: 24px
    fontWeight: 400
    lineHeight: 36px
    letterSpacing: 0px
  headline-sm:
    fontFamily: Poppins
    fontSize: 21px
    fontWeight: 400
    lineHeight: 28px
    letterSpacing: 0px
  body-lg:
    fontFamily: "Suisse Intl"
    fontSize: 18px
    fontWeight: 400
    lineHeight: 30px
    letterSpacing: 0.25px
  body-md:
    fontFamily: "Suisse Intl"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 30px
    letterSpacing: 0.25px
  body-sm:
    fontFamily: "Suisse Intl"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 22px
    letterSpacing: 0.2px
  label-lg:
    fontFamily: Poppins
    fontSize: 16px
    fontWeight: 500
    lineHeight: 24px
    letterSpacing: 0px
  label-md:
    fontFamily: Poppins
    fontSize: 14px
    fontWeight: 500
    lineHeight: 20px
    letterSpacing: 0px
  label-sm:
    fontFamily: Poppins
    fontSize: 12px
    fontWeight: 500
    lineHeight: 16px
    letterSpacing: 0.04em
  nav-link:
    fontFamily: "Suisse Intl"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 20px
    letterSpacing: 0px
  button-text:
    fontFamily: Poppins
    fontSize: 16px
    fontWeight: 500
    lineHeight: 20px
    letterSpacing: 0px
rounded:
  none: 0px
  sm: 4px
  md: 8px
  lg: 16px
  xl: 24px
  full: 9999px
spacing:
  xs: 8px
  sm: 16px
  md: 30px
  lg: 40px
  xl: 104px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.secondary}"
    typography: "{typography.button-text}"
    rounded: "{rounded.full}"
    padding: "14px 22px"
    size: "44px"
  button-primary-hover:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.secondary}"
    rounded: "{rounded.full}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.secondary}"
    typography: "{typography.button-text}"
    rounded: "{rounded.sm}"
    padding: "14px 22px"
    size: "44px"
  button-link:
    backgroundColor: "transparent"
    textColor: "{colors.primary}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.none}"
    padding: "0px"
  card:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.secondary}"
    rounded: "{rounded.md}"
    padding: "16px"
  input:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.sm}"
    padding: "14px 16px"
  chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.secondary}"
    rounded: "{rounded.full}"
    padding: "8px 12px"
---

# RACV Modern

## Overview
RACV presents as a trusted, practical membership brand with a bright, optimistic tone. The interface balances professionalism and approachability: large blue hero surfaces, clear navigation, and prominent yellow calls to action make the experience feel helpful and confident rather than flashy. The layout is spacious and service-led, with strong wayfinding for users who want to complete tasks quickly.

## Colors
- **Primary (#0067F6):** RACV’s signature blue, used for links, icons, navigation accents, and major brand emphasis. It reads as energetic and reliable.
- **Secondary (#001657):** A deep navy used for prominent text and strong contrast against white or light surfaces. It gives the system its authority.
- **Tertiary (#F8DB00):** A vivid yellow accent used for the main CTA and brand highlight moments. It should feel optimistic, high-visibility, and action-oriented.
- **Neutral (#FFFFFF):** Clean white for surfaces, cards, and negative space. It keeps the interface open and legible.
- **Surface (#F6F5F1):** A soft off-white used for section backgrounds to separate content without heavy contrast.
- **On-surface (#121212):** Near-black body text for maximum readability on light surfaces.
- **Error (#D92D20):** Reserved for validation and destructive states; use sparingly so it does not compete with the brand accents.
- **Border (#D9DDE5):** A subtle divider color for cards, inputs, and low-emphasis separation.

## Typography
Headlines use Poppins, set in light-to-medium weights, giving the brand a rounded but composed voice. The largest headings are generous without becoming heavy, which matches the clean, service-first tone of the layout. Body copy uses Suisse Intl for a more editorial, highly readable feel, especially at 16px with a 30px line height.

Labels and navigation rely on Poppins or Suisse Intl depending on the context, but always stay clear and restrained. Uppercase styling is not a dominant pattern; instead, the system favors sentence case and straightforward phrasing. Letter spacing is minimal overall, with only subtle tracking used for small labels where needed.

## Layout & Spacing
The page uses a wide, fluid desktop layout with a strong central container and generous side margins. Hero content is split between copy on the left and imagery on the right, with large, decisive spacing between clusters. Sections are stacked with clear vertical rhythm, using the spacing scale from 8px through 104px to create calm separation between navigation, hero, shortcuts, and content grids.

Cards and utility panels use comfortable internal padding rather than dense packing. Grouped links and service tiles are organized into evenly spaced columns, with thin dividers and consistent alignment to keep scanning easy. The overall rhythm favors medium-to-large gaps, reinforcing a confident, uncluttered service experience.

## Elevation & Depth
Depth is subtle and mostly achieved through contrast, white cards on blue or light surfaces, and fine borders rather than dramatic shadows. The utility card in the hero section feels lifted because of its white fill, rounded corners, and separation from the saturated blue background. Shadows are minimal to none, so hierarchy comes from color layering and spacing instead of material-style elevation.

## Shapes
The shape language is soft and functional. Buttons lean into full pill geometry, while cards and panels use modest 8px rounded corners for a stable, dependable feel. The system avoids aggressive angular forms, which helps the experience stay friendly and accessible.

## Components
Buttons are the most distinctive interaction pattern. `button-primary` is a yellow pill with dark navy text, medium-weight Poppins, and strong padding for a clear tap target; it should be used for the main conversion action only. Secondary buttons are quieter, typically transparent with navy text and a smaller corner radius, while link buttons stay plain, blue, and underlined for inline navigation.

Cards use a white background, subtle border, and `rounded.md` to define grouped content without visual noise. They should remain simple and content-forward, with enough padding to support icons, short labels, and stacked task shortcuts. Inputs should be similarly restrained: white fill, light border, modest rounding, and clear text contrast.

Chips and pills should feel light and utility-oriented, often using the soft surface tone with full rounding. Navigation links and service lists should stay compact, legible, and blue, with simple arrow affordances rather than decorative treatments. Iconography is thin-stroked and mostly blue, reinforcing clarity over ornament.

## Do's and Don'ts
- Do use the yellow primary CTA sparingly for the single most important action on a page.
- Do keep headlines in Poppins and body copy in Suisse Intl to preserve the brand’s visual hierarchy.
- Do maintain generous whitespace and medium-to-large section gaps for easy scanning.
- Do prefer clean cards, subtle borders, and color contrast over heavy shadows.
- Don't introduce highly decorative gradients, glass effects, or busy backgrounds.
- Don't use too many accent colors; keep blue, yellow, white, and navy as the core system.
- Don't over-round secondary surfaces; reserve pill shapes for primary actions and compact utility chips.
- Don't make links look like buttons unless they are true calls to action.