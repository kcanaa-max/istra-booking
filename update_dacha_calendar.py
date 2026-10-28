#!/usr/bin/env python3
import datetime as dt, json, re, urllib.request, pathlib
URL = 'https://sutochno.ru/calendar/ical/f285a2f4019ed66387c4b0217d04e045e89b208.ics'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (compatible; CalendarSync/1.0)'})
with urllib.request.urlopen(req, timeout=30) as response:
    ics = response.read().decode('utf-8-sig')
if 'BEGIN:VCALENDAR' not in ics or 'END:VCALENDAR' not in ics:
    raise ValueError('Суточно вернул не календарь')
busy = set()
for event in ics.split('BEGIN:VEVENT')[1:]:
    if 'END:VEVENT' not in event: continue
    start = re.search(r'^DTSTART[^:]*:(\d{8})', event, re.M)
    end = re.search(r'^DTEND[^:]*:(\d{8})', event, re.M)
    if not start or not end: continue
    first = dt.datetime.strptime(start.group(1), '%Y%m%d').date()
    last = dt.datetime.strptime(end.group(1), '%Y%m%d').date()
    if last <= first or (last-first).days > 365: raise ValueError('Некорректный период')
    for n in range((last-first).days): busy.add((first+dt.timedelta(days=n)).isoformat())
if not ics.count('BEGIN:VEVENT') == ics.count('END:VEVENT'):
    raise ValueError('Неполный календарь')
pathlib.Path('dacha-busy-dates.json').write_text(json.dumps({'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(), 'busy':sorted(busy)},ensure_ascii=False,indent=2)+'\n')
print(f'Загружено занятых ночей: {len(busy)}')
