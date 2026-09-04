# Authentication UI Design Reference

Penpot tooling was unavailable in this environment; this document records the intended design reference for implementation alignment.

## Direction

A restrained enterprise intelligence surface: clean application background, one focused authentication card, quiet utility controls, semantic shadcn-style components, and no decorative patterns.

## Layout

- Desktop: two balanced columns, with product context on the left and a 420px authentication surface on the right.
- Mobile: stacked context and form, with the utility control kept in the top row.
- Card radius: 6px; borders use the shared `--line` token; shadow is subtle and directional.
- Spacing rhythm: 8px base unit, 24px card padding, 32px section gaps.

## Type Hierarchy

- Product title: 40-52px desktop, 30px mobile, compact line-height.
- Page title: 26px desktop, 23px mobile.
- Supporting copy: 13px with restrained contrast.
- Labels: 12px semibold; controls: 14px.
- Utility metadata: 11px mono uppercase.

## States

- Inputs use the shared surface and border tokens, with accent focus rings.
- Primary actions use the accent token; secondary links remain quiet.
- Error and success states are compact, inline, and never full-page.
- The theme control is a 28px square Lucide icon button with an accessible label.

## Route Coverage

The same layout and card treatment applies to Login, Forgot Password, Reset Password, Access Request, Session Expired, and Unauthorized. Only the page-specific form content changes.
