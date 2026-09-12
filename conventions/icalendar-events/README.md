# iCalendar Events Conventions

This conventions file provides guidelines for accurately converting event information into iCalendar (.ics) format files.
You can paste random unstructured text or even images/PDFs of events and
itineraries and turn them into iCalendar files suitable for importing
into your calendar tool.

The best approach is to save your event info to a file and run aider like:


```bash
aider output.ics --read-only my-events.txt --read-only CONVENTIONS.md

# or

aider output.ics --read-only my-events.pdf --read-only CONVENTIONS.md
```

You can ask aider to proofread the generated iCalendar file.
But you should personally proofread the results in your Calendar app,
as mistakes can still happen.
Proofreading is usually much easier than tediously creating calendar
entries for a long itinerary.

## Purpose

These conventions ensure that:
- Events are correctly formatted according to iCalendar standards
- Dates, times, and timezones are properly specified
- Multi-day events are handled appropriately
- All necessary event details are captured accurately

## Use Cases

This convention is ideal for:
- Creating calendar files from travel itineraries
- Converting event lists to shareable calendar formats
- Generating conference or meeting schedules
- Planning multi-day events and stays

## Usage

Save your event information to a file, then run aider like:

```bash
aider output.ics --read-only my-events.txt --read-only CONVENTIONS.md

# or

aider output.ics --read-only my-events.pdf --read-only CONVENTIONS.md
```

Or you can simply paste your event info into the chat.

The AI will:
- Request any missing critical information
- Create a text list of events for your approval
- Generate the proper iCalendar (.ics) file once approved
