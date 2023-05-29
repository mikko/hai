from __future__ import annotations
import json

import logging
import openai
from datetime import datetime

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.typing import ConfigType

DOMAIN = "hai_service"
_LOGGER = logging.getLogger(__name__)

CONF_ORG_ID = "organization_id"
CONF_API_KEY = "api_key"
CONF_SYSTEM_PROMPT = "system_prompt"

CALL_PROP_PROMPT = "prompt"
CALL_PROP_TIME = "time"
CALL_PROP_TITLE = "title"

TEXTS = {
    "schedule_header": "Events today:",
    "prompt_header": "Prompt:",
    "weather_header": "Weather today:",
    "time_header": "Current date:"
}

STATE_RESULT = f"{DOMAIN}.result"
STATE_CALENDAR = f"{DOMAIN}.calendar"
STATE_ATTR_FULL_TEXT = "full_text"
STATE_ATTR_EVENTS = "events"

def get_configuration(config: ConfigType):
    return {
        "organization_id": str(config[DOMAIN][CONF_ORG_ID]),
        "api_key": str(config[DOMAIN][CONF_API_KEY]),
        "system_prompt": str(config[DOMAIN][CONF_SYSTEM_PROMPT])
    }

def get_weather_context(hass: HomeAssistant):
    weather_service = 'weather.openweathermap'
    weather_attribute = 'forecast'

    weather_state = hass.states.get(weather_service)
    if weather_state is None:
        return "Weather data unavailable"

    print(weather_state)
    rain_unit = "mm"

    weather_forecast = weather_state.attributes[weather_attribute]
    #weather_forecast = json.loads(forecast_json)
    weather_text = ""
    for f_it in weather_forecast:
        # time = #.strftime("%H:%M")
        f_datetime = datetime.fromisoformat(f_it['datetime']) # 2023-04-28T21:00:00+00:00
        # Only take forecast items for today
        if f_datetime.date() == datetime.today().date():
            condition = f_it['condition']
            temperature = f_it['temperature']
            rain_prop = f_it['precipitation_probability']
            rain_amount = f_it['precipitation']
            weather_text += f"{f_datetime.strftime('%H:%M')}: {condition} temperature {temperature} degrees Celcius with {rain_prop} percent propability of {rain_amount}{rain_unit} rain\n"
    return weather_text

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    configuration = get_configuration(config)
    openai.api_key = configuration[CONF_API_KEY]
    hass.states.async_set(STATE_RESULT, "")
    """Set up the an async service example component."""
    @callback
    async def prompt(call: ServiceCall) -> None:
        _LOGGER.info('Running the HAI service')

        def run_completion():
            cal_state = hass.states.get(STATE_CALENDAR)
            calendar_events = cal_state.attributes[STATE_ATTR_EVENTS] if cal_state is not None else ""

            weather = get_weather_context(hass)

            time_now = datetime.now().strftime("%A %d.%m.%Y")
            prompt = call.data.get(CALL_PROP_PROMPT)
            full_prompt = f"{TEXTS['time_header']} {time_now}\n{TEXTS['schedule_header']} {calendar_events}\n{TEXTS['weather_header']} {weather}\n{TEXTS['prompt_header']} {prompt}"
            print(full_prompt)
            return openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                        {"role": "system", "content": configuration[CONF_SYSTEM_PROMPT]},
                        {"role": "user", "content": full_prompt},
                ]
            )
        response = await hass.async_add_executor_job(run_completion)

        result = ''
        for choice in response.choices:
            result += choice.message.content


        print(result)
        time_now = datetime.now().strftime("%d.%m.%Y %H:%M") # %m/%d/%Y

        hass.states.async_set(STATE_RESULT, time_now, { STATE_ATTR_FULL_TEXT: result })

    async def add_calendar_event(call: ServiceCall) -> None:
        time = call.data.get(CALL_PROP_TIME)
        title = call.data.get(CALL_PROP_TITLE)

        new_event = f"{time} {title}"
        cal_state = hass.states.get(STATE_CALENDAR)
        previous_events = cal_state.attributes[STATE_ATTR_EVENTS] if cal_state is not None else ""
        updated_events = f"{previous_events}\n{new_event}"
        hass.states.async_set(STATE_CALENDAR, "", { STATE_ATTR_EVENTS: updated_events })

    async def clear_calendar_events(call: ServiceCall) -> None:
        hass.states.async_set(STATE_CALENDAR, "", { STATE_ATTR_EVENTS: "" })


    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, 'prompt', prompt)
    hass.services.async_register(DOMAIN, 'add_calendar_event', add_calendar_event)
    hass.services.async_register(DOMAIN, 'clear_calendar_events', clear_calendar_events)

    # Return boolean to indicate that initialization was successfully.
    return True
