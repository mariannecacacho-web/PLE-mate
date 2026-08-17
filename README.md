# PLE-mate Adaptive v2

PLE-mate can now safely adapt its dashboard from natural-language chat.

Examples:
- "Make the tracker more compact." -> compact layout
- "Put my weakest subjects at the top." -> weakest-first sorting
- "Add a weekly study-hours graph." -> weekly graph widget
- "Remove the pinboard." -> hides pinboard
- "Bring back the pinboard." -> restores pinboard
- "Hide the countdown." -> hides countdown
- "Show hours remaining for every subject." -> enables hours
- "I studied Surgery for 3 hours." -> logs time and updates remaining hours

The AI cannot write arbitrary code. It can only request predefined safe dashboard actions.

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="YOUR_KEY"
python server.py
```

Open http://localhost:3000.

## Deployment

Use a Python web host and set OPENAI_API_KEY and OPENAI_MODEL=gpt-5.6 as server environment variables. Never expose the API key in index.html.
