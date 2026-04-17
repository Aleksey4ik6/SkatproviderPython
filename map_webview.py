import json
import os
import sys

import webview


def _escape_js_text(value):
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", " ")
        .replace("\r", " ")
    )


def build_html(payload):
    center = payload.get("center") or {"lat": 53.7209, "lon": 91.4424}
    zoom = int(payload.get("zoom") or 13)
    houses = payload.get("houses") or []
    markers_js = []
    for h in houses:
        house_id = int(h.get("house_id", 0))
        lat = float(h.get("lat", 0))
        lon = float(h.get("lon", 0))
        clients = int(h.get("clients", 0))
        active = int(h.get("active", 0))
        address = _escape_js_text(h.get("address", ""))
        is_alert = active > 0
        fill = "#ff4d4d88" if is_alert else "#35c75988"
        stroke = "#ff2d55" if is_alert else "#1faa59"
        radius = 22 + min(clients, 80) * 1.6
        markers_js.append(
            f"""
            var circle_{house_id} = new ymaps.Circle([[{lat}, {lon}], {radius}],
                {{
                    hintContent: '{address}',
                    balloonContent: '<b>{address}</b><br>Клиентов: {clients}<br>Аварий: {active}'
                }},
                {{
                    fillColor: '{fill}',
                    strokeColor: '{stroke}',
                    strokeWidth: 2
                }});
            map.geoObjects.add(circle_{house_id});
            var label_{house_id} = new ymaps.Placemark([{lat}, {lon}],
                {{ iconContent: '{clients}' }},
                {{
                    preset: 'islands#blackStretchyIcon',
                    iconColor: '{stroke}'
                }});
            map.geoObjects.add(label_{house_id});
            """
        )

    ykey = os.getenv("YANDEX_MAPS_API_KEY", "62d9f365-7a46-4faa-a631-8f50f06091e6").strip()
    key_param = f"&apikey={ykey}" if ykey else ""
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Карта сети SKAT</title>
  <style>
    html, body, #map {{ height: 100%; margin: 0; padding: 0; background: #10151d; }}
    .legend {{
      position: absolute; z-index: 1000; left: 12px; top: 12px;
      background: rgba(16, 21, 29, 0.92); color: #dce6f2;
      font-family: Segoe UI, sans-serif; font-size: 13px;
      padding: 8px 10px; border-radius: 8px;
      border: 1px solid rgba(220,230,242,0.2);
    }}
  </style>
  <script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU{key_param}"></script>
</head>
<body>
  <div class="legend">Зеленый: стабильно | Красный: авария | Число: клиентов</div>
  <div id="map"></div>
  <script>
    ymaps.ready(function() {{
      var map = new ymaps.Map('map', {{
        center: [{float(center.get("lat", 53.7209))}, {float(center.get("lon", 91.4424))}],
        zoom: {zoom},
        controls: ['zoomControl', 'searchControl', 'typeSelector', 'fullscreenControl']
      }});
      map.controls.get('searchControl').options.set({{
        provider: 'yandex#search',
        noPlacemark: false
      }});
      {"".join(markers_js)}
    }});
  </script>
</body>
</html>
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: map_webview.py <payload_json_path>")
        sys.exit(1)
    payload_path = sys.argv[1]
    if not os.path.exists(payload_path):
        print(f"Payload not found: {payload_path}")
        sys.exit(1)
    with open(payload_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    html = build_html(payload)
    webview.create_window("SKAT — Интерактивная карта", html=html, width=900, height=640, min_size=(760, 520))
    webview.start(gui="edgechromium", debug=False)


if __name__ == "__main__":
    main()
