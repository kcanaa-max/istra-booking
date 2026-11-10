import os, json, datetime, urllib.request, re
from pathlib import Path
url = os.environ["BARN_ICS_URL"]
request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(request, timeout=35) as response:
    ics = response.read().decode("utf-8-sig")
if "BEGIN:VCALENDAR" not in ics: raise ValueError("Invalid ICS")
busy = set()
for event in ics.split("BEGIN:VEVENT")[1:]:
    event = event.split("END:VEVENT")[0]
    start = re.search(r"^DTSTART[^:]*:(\d{8})", event, re.M)
    end = re.search(r"^DTEND[^:]*:(\d{8})", event, re.M)
    if not start or not end: continue
    d = datetime.datetime.strptime(start.group(1), "%Y%m%d").date()
    stop = datetime.datetime.strptime(end.group(1), "%Y%m%d").date()
    if stop <= d or (stop-d).days > 730: continue
    while d < stop:
        busy.add(d.isoformat()); d += datetime.timedelta(days=1)
if not re.search(r"BEGIN:VEVENT", ics):
    raise ValueError("ICS contains no events; refusing to publish potentially empty calendar")
output = {"updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "busy": sorted(busy)}
Path("barn-busy-dates.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
