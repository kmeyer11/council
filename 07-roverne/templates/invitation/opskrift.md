# Opskrift: invitation

The recipe the agent follows when the user says "lav en invitation" (or similar). The agent asks for the content, drafts the text, renders, and goes back and forth until the user is happy. Every field it fills is described in `example.yaml`. Talk to the user in Danish.

## 0. Before asking

Read what the user already said. Only ask for what is still missing. If they wrote "hike i Rold Skov 7.-8. nov", don't ask for the title or the dates again.

## 1. First round: the facts

Ask these together in one message. If the assistant has a question tool (e.g. Conductor's `AskUserQuestion`), use it. These are facts: never guess them.

1. **Hvad er det?** What is the event? It becomes the `title` (short: 2–4 words fit best).
2. **Hvornår?** Start date and time, and the end if it runs over several hours or days → `starts` / `ends`.
3. **Hvor?** The place, plus an exact meeting point if there is one → `where` / `where_detail`.
4. **Facebook-begivenhed?** The link to the event and an answer deadline, if there is one → `facebook.link` / `facebook.deadline`. If the event doesn't exist yet, leave `link: null` and say so in the hand-over: the QR code is missing until the link is added.

## 2. Second round: the content

Again in one message:

1. **Hvad skal teksten fortælle?** Ask for keywords (stikord): what you'll do, who it's for, food, sleeping, price, anything practical. Offer to write the text from them.
2. **Skal de medbringe noget?** List or no → `bring` (4–6 short items fit).
3. **Billede:** the forest background (default) or one of their own photos? List them with `photos` if they want their own → `photo`.
4. **Formater:** options `post` (Instagram/Facebook), `story`, `a5` (flyer), `a4` (poster). Multiple choice. Default `[post, a5]`.

Don't ask about `subtitle` or `kicker`. Write a subtitle suggestion yourself. Keep `kicker: Invitation` unless the event is clearly something else (e.g. "Klanmøde", "Save the date").

## 3. Write the draft

- `new invitation --slug {short-name}`, then fill in `source.yaml`. Remove every example value the user didn't give.
- Write `text` from their keywords: Danish, `du` form, short sentences, warm with a bit of humour (Røverne doesn't take itself too seriously). 1–2 short paragraphs, max ~80 words, so it fits the `post` format.
- Every fact in `text` (times, price, distance, who's driving, food) must come from the user. If something is missing, ask. Don't fill it in.
- Don't write weekdays or month names in `text`. The template computes them from `starts` / `ends`.

## 4. Render and show

1. `render "{path}/source.yaml"`.
2. Look at every PNG (and the PDF if they're printing). A warning that content is cut off: shorten `text` or `bring` first, and only then suggest dropping `post`.
3. Show the user the images, plus a short list of what you made up yourself (the subtitle, the wording in `text`), so they can change it.

## 5. Changes

Edit `source.yaml` and render again, until the user is happy. The yaml is the single source of truth for that piece, so don't edit the PNG or the PDF.

## 6. Hand-over

Give the path to the folder in iCloud and the files in it. Remind them of the human check in `../../CONTEXT.md`: check the date against the plan, scan the QR code with a phone, and get consent for every photo with people in it.
