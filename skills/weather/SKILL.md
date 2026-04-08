---
name: weather
description: "Get current weather and forecasts via wttr.in or Open-Meteo. Use when: user asks about weather, temperature, or forecasts for any location. NOT for: historical weather data, severe weather alerts, or detailed meteorological analysis. No API key needed."
homepage: https://wttr.in/:help
metadata: { "openclaw": { "emoji": "🌤️", "requires": { "bins": ["curl"] } } }
---

# Weather Skill

Get current weather conditions and forecasts.

## When to Use

✅ **USE this skill when:**

- "What's the weather?"
- "Will it rain today/tomorrow?"
- "Temperature in [city]"
- "Weather forecast for the week"
- Travel planning weather checks

## When NOT to Use

❌ **DON'T use this skill when:**

- Historical weather data → use weather archives/APIs
- Climate analysis or trends → use specialized data sources
- Hyper-local microclimate data → use local sensors
- Severe weather alerts → check official NWS sources
- Aviation/marine weather → use specialized services (METAR, etc.)

## Location

Always include a city, region, or airport code in weather queries.

## Commands

### Current Weather

```bash
# One-line summary
curl "wttr.in/London?format=3"

# Detailed current conditions
curl "wttr.in/London?0"

# Specific city
curl "wttr.in/New+York?format=3"
```

### Forecasts

```bash
# 3-day forecast
curl "wttr.in/London"

# Week forecast
curl "wttr.in/London?format=v2"

# Specific day (0=today, 1=tomorrow, 2=day after)
curl "wttr.in/London?1"
```

### Format Options

```bash
# One-liner
curl "wttr.in/London?format=%l:+%c+%t+%w"

# JSON output
curl "wttr.in/London?format=j1"

# PNG image
curl "wttr.in/London.png"
```

### Format Codes

- `%c` — Weather condition emoji
- `%t` — Temperature
- `%f` — "Feels like"
- `%w` — Wind
- `%h` — Humidity
- `%p` — Precipitation
- `%l` — Location

## Quick Responses

**"What's the weather?"**

```bash
curl -s "wttr.in/London?format=%l:+%c+%t+(feels+like+%f),+%w+wind,+%h+humidity"
```

**"Will it rain?"**

```bash
curl -s "wttr.in/London?format=%l:+%c+%p"
```

**"Weekend forecast"**

```bash
curl "wttr.in/London?format=v2"
```

## Chinese City Fallback (Important)

**⚠️ wttr.in has poor recognition of Chinese city names.** When querying Chinese cities (深圳/北京/上海/广州 etc.), wttr.in may resolve to wrong locations (e.g., "Shenzhen" → Kaiserslautern, Germany → 2°C). Always verify results make sense.

**Fallback rule:** If the returned temperature is obviously wrong for the queried city (e.g., sub-5°C for a subtropical city), switch to Open-Meteo immediately.

**Recommended for Chinese cities — use Open-Meteo directly:**

```bash
# Shenzhen (22.54°N, 113.94°E)
curl "https://api.open-meteo.com/v1/forecast?latitude=22.54&longitude=113.94&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,uv_index&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum&timezone=Asia/Shanghai&forecast_days=3"

# Beijing (39.9°N, 116.4°E)
curl "https://api.open-meteo.com/v1/forecast?latitude=39.9&longitude=116.4&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,uv_index&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum&timezone=Asia/Shanghai&forecast_days=3"

# Shanghai (31.2°N, 121.5°E)
curl "https://api.open-meteo.com/v1/forecast?latitude=31.2&longitude=121.5&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,uv_index&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum&timezone=Asia/Shanghai&forecast_days=3"

# Guangzhou (23.1°N, 113.3°E)
curl "https://api.open-meteo.com/v1/forecast?latitude=23.1&longitude=113.3&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,uv_index&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum&timezone=Asia/Shanghai&forecast_days=3"
```

**Common Chinese city coordinates:**

| City | Latitude | Longitude |
|------|----------|-----------|
| 深圳 | 22.54 | 113.94 |
| 北京 | 39.9 | 116.4 |
| 上海 | 31.2 | 121.5 |
| 广州 | 23.1 | 113.3 |
| 杭州 | 30.3 | 120.2 |
| 成都 | 30.6 | 104.0 |
| 武汉 | 30.6 | 114.3 |
| 西安 | 34.3 | 108.9 |
| 南京 | 32.1 | 118.8 |
| 重庆 | 29.5 | 106.5 |

**Weather code → emoji translation (for Open-Meteo output):**

| Code | Meaning | Emoji |
|------|---------|-------|
| 0 | 晴朗 | ☀️ |
| 1 | 基本晴朗 | 🌤️ |
| 2 | 多云 | ⛅ |
| 3 | 阴天 | ☁️ |
| 45/48 | 雾 | 🌫️ |
| 51/53/55 | 毛毛雨 | 🌧️ |
| 61/63/65 | 小/中/大雨 | 🌧️ |
| 71/73/75 | 小/中/大雪 | ❄️ |
| 80/81/82 | 阵雨 | 🌦️ |
| 95/96/99 | 雷暴 | ⛈️ |

## Notes

- No API key needed (uses wttr.in or Open-Meteo)
- Rate limited; don't spam requests
- wttr.in works best for English city names and airport codes
- **Always use Open-Meteo for Chinese cities** — it uses lat/lon, no location ambiguity
- Open-Meteo is the recommended fallback when wttr.in returns implausible data
