---
description: Write a short, plain-words note explaining a problem and how we solved it, so it can be repeated to teammates out loud.
---

Write a note that lets the user explain a fix to a teammate without needing to understand the code.

The reader is a person who knows the product but not the codebase: support, ops, a PM, a clinician. The user will often read this note out loud or paste it into Slack, so it has to survive being said in a normal voice.

## Steps

1. Work out what to write about.
   - If $ARGUMENTS names a ticket (like ENG-1234) or a URL, read it from Linear for the problem statement and the reporter's words.
   - Otherwise use the current session: what we investigated, what we found, what we changed. Prefer the branch's commits and diff over memory when the session is long.
   - If $ARGUMENTS is free text, treat it as the framing and fill in the rest from the session.
2. Before writing, be clear in your own head about three things: what the person hitting this actually saw, why it happened, and what is different now. If you cannot state the cause, say plainly in the note that the cause is still open, and do not invent one.
3. Write the note (see Rules) and save it to `~/post-its/`.
   - File name: `YYYY-MM-DD-<ticket-or-slug>.md` using today's date.
   - If that file already exists, replace it only if it covers the same fix, otherwise add `-2` and so on.
4. Print the whole note in the chat as well, so the user can read it without opening the file.
5. If something important cannot be said in plain words within three paragraphs, leave it out of the note and mention it to the user in chat instead, below the note. Do not bolt it onto the note.

## Rules for the note itself

- A short title line, then **no more than three paragraphs**. Fewer is fine. Nothing else: no headings, no bullet lists, no sections.
- One idea per paragraph. The natural order is: what people were running into, why it was happening, what changed and what they should expect now.
- **Really plain words.** Short sentences. If a term would make a non-engineer pause, replace it with what it means. No file names, function names, table names, class names, error codes, or code of any kind. No brand names of libraries or tools.
- **No examples.** No "for instance", no walkthroughs, no sample cases, no hypothetical users.
- Friendly but not childish. Write like a calm colleague explaining something at a desk. No exclamation marks, no emoji, no cheerleading, no jokes, no talking down to the reader.
- Plain declarative sentences. No em dashes. Use periods, commas, or parentheses. Skip filler like "worth noting", "it's important to", "seamless", "robust".
- Say what is true. If the fix only covers part of the problem, or something is still being watched, say so in one plain sentence rather than implying it is all done.
- Mention the ticket ID once, in the title line, if there is one. Keep it out of the body.

## Input

$ARGUMENTS — optional. A ticket ID, a URL, or a sentence framing the problem. With no arguments, wrap up whatever we have been working on in this session.
