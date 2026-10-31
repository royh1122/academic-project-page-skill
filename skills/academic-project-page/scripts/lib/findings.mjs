// Stable ids for audit findings, so a report can cite one ("defended: blank-band") and runs can be compared.
// Matched against the message text in order; the first pattern that matches names the finding.
// A message no pattern matches falls back to its check's name (page, interaction, typography).
export const FINDINGS = [
  // Page audit: structure and content
  ['placeholder', /^Template placeholder remains/],
  ['duplicate-id', /^Duplicate ids/],
  ['h1-count', /^Page needs exactly one h1/],
  ['heading-skip', /^Heading level skipped/],
  ['img-alt', /^Image without alt/],
  ['icon-font', /^Icon draws nothing/],
  ['control-name', /^Control without an accessible name/],
  ['iframe-title', /^Iframe without a title/],
  ['nav-dangling', /^Navigation link to missing section/],
  ['citation-hidden', /^Citation exists but is hidden/],
  ['method-hidden', /^Method\/architecture figure hidden/],
  // Page audit: type and colour
  ['synthesized-bold', /synthesized bold/],
  ['contrast', /^Contrast /],
  ['text-small', /^Text below 12px/],
  // Page audit: layout
  ['image-repeat', /^Same image shown more than once/],
  ['corner-radii', /^Media use different corner radii/],
  ['left-edges', /left edges:/],
  ['numeric-align', /numbers are left-aligned/],
  ['overflow', /^Horizontal overflow/],
  ['title-break', /^Title breaks inside/],
  ['title-orphan', /^Title ends with a single word/],
  ['teaser-letterbox', /^Teaser media letterboxed/],
  ['teaser-heights', /^Teaser media differ in height/],
  ['image-upscaled', /^Images stretched beyond natural size/],
  ['text-covered', /^Text covered:/],
  ['anchor-covered', /^Jump to #/],
  ['text-clipped', /^Text cut off:/],
  ['blank-band', /^Blank band/],
  ['margin-uneven', /^Uneven side margins/],
  ['target-small', /^Targets under 24/],
  // Page audit: media, motion, serving
  ['video-playsinline', /without playsinline/],
  ['video-poster', /^Video without a poster/],
  ['poster-blank', /^Video poster is a blank/],
  ['video-size', /^Video without width\/height/],
  ['resource-missing', /^Missing local resource/],
  ['root-relative', /^Root-relative paths/],
  ['range-requests', /ignores Range/],
  ['motion-video', /^Videos keep playing under prefers-reduced-motion/],
  ['motion-carousel', /carousel keeps advancing under prefers-reduced-motion/],
  ['motion-endless', /endless CSS animation/],
  ['hidden-reduced-motion', /^Text hidden under reduced motion/],
  ['dev-server', /^Dev server markup/],
  ['malformed-source', /^Malformed page source/],
  ['wrong-base', /^Served at \//],
  // Interaction check
  ['focus-covered', /^Keyboard pass: focus lands under|^Focus can land under/],
  ['focus-indicator', /^Keyboard pass: .*show no focus indicator/],
  ['focus-trap', /^Keyboard pass: focus (is trapped|loops back)/],
  ['focus-hidden', /^Keyboard pass: focus lands on .*(invisible|visually hidden)/],
  ['focus-skipped', /^Keyboard pass: Tab (skipped|never moved)/],
  ['contents-menu', /^Contents (menu|button)|^The contents button/],
  ['more-works', /^More Works/],
  ['copy-button', /copy status|data-copy-target|sets no status/],
  ['figure-viewer', /figure viewer|the viewer |enlarged|zoom button|\+ key does not zoom|cannot be opened with/],
  ['carousel', /slide|carousel did not initialise|the last dot/],
  ['check-stopped', /the check itself stopped/],
  // Typography check
  ['typography-baseline', /^Missing (baseline|font-inspection) element/],
];

export function findingId(message, fallback) {
  for (const [id, pattern] of FINDINGS) if (pattern.test(message)) return id;
  return fallback;
}
