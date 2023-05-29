> Me: Could we get AI?
> Mom: We have AI at home.
> AI at home:

# HAI

Home AI is a simple chatGPT integration for Home Assistant. It serves only one purpose and that is to generate natural language text. Built as a personal experiment and not polished for general use.

```
                                ┌────────────────────────┐  ┌───────────────────────────┐
                                │                        │  │                           │
                                │  OpenWeatherMap        │  │  Google Calendar          │
                                │                        │  │                           │
                                │                        │  │                           │
                                └───────────┬────────────┘  └─────────────┬─────────────┘
                                            │                             │
                                            │                             │
                                            ▼                             ▼
┌────────────────────────────┐  ┌────────────────────────┐  ┌───────────────────────────┐
│                            │  │                        │  │                           │
│  System Prompt             │  │  Weather               │  │  Calendar events          │
│                            │  │                        │  │                           │
│                            │  │                        │  │                           │
└──────────────┬─────────────┘  └───────────┬────────────┘  └─────────────┬─────────────┘
               │                            │                             │
               │                            ▼                             │
               │                ┌────────────────────────┐                │
               │                │                        │                │
               │                │  HAI                   │                │
               └───────────────►│                        │◄───────────────┘
                                │                        │
               ┌───────────────►│                        │
               │                │                        │
               │                └───────────┬────────────┘
┌──────────────┴────────────┐               │
│                           │               │
│  Prompt                   │               │
│                           │               │
│                           │               ▼
└───────────────────────────┘   ┌────────────────────────┐
                                │                        │
                                │                        │
                                │   Generated text       │
                                │                        │
                                │                        │
                                └────────────────────────┘
```

## Usage

### Requirements:

* OpenWeatherMap integration
* Google Calendar integration

### Automations

1. Create an automation which adds a calendar event with an offset like 15h using `hai_service.add_calendar_event`. (Because Google Calendar integration sucks and does not allow reading all events for a day)
1. Create an automation which clears the calendar events for new updates using `hai_service.clear_calendar_events`
1. Create an automation which generates the text using a prompt. For example a daily status in the morning.
1. Create an automation which sends the generated text as notification or reads it aloud using TTS. Generated text is found on `full_text` attribute under `hai_service.result`

