# PLE-mate v8

This build improves the mystical companion and dashboard.

## Main changes
- Hikari starts each new day tired/dusty, then visually shifts toward bright/clean as Care actions are used.
- 5 life stages use the supplied generated evolution artwork; care state is layered with visual treatment until new tired/dirty artwork can be generated.
- Study progress is the primary source of XP/evolution. Pomodoro gives bonus rewards only.
- Feed, Pet and Shower now change Energy, Mood/Cleanliness and messages.
- Pomodoro supports 25, 45, or 100 minute sessions with a circular progress ring that changes color near completion.
- Subject icons are shown in the tracker.
- Subject cards and floating detail windows remain functional.
- Only the chat is scrollable within the dashboard rail; other cards are sized to fit their content.
- Calendar embed URL can be saved locally in Settings; the supplied Asia/Manila Google Calendar URL is preloaded.
- The right rail is a fixed-width column containing Hikari above the PLE-mate chat.

## Important artwork note
The current package uses the five previously generated Hikari evolution images. The requested separate tired/dirty and clean/happy artwork for every life stage requires new image-generation capacity; while that is unavailable, the app uses visual state treatments so Hikari still becomes visibly tired/dusty and clean/glowing through the day.

## GitHub Pages
Upload ALL files in this folder to the repository root: index.html, styles.css, app.js, hikari.png, evolution_1.png, evolution_2.png, evolution_3.png, evolution_4.png, evolution_5.png, aoi.png, README.md.

Do not upload passwords, API keys, or OAuth secrets.
