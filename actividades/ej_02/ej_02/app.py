import ure as re
import ujson as json
from machine import Pin
import neopixel

# === Clases básicas para Microdot ===
class Request:
    def __init__(self, method, path, headers, body):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
    def json(self):
        return json.loads(self.body)

class Response:
    def __init__(self, body='', status_code=200, headers=None):
        self.body = body
        self.status_code = status_code
        self.headers = headers or {'Content-Type': 'text/plain'}

    def to_http(self):
        reasons = {
            200: 'OK',
            400: 'Bad Request',
            404: 'Not Found',
            500: 'Internal Server Error'
        }
        reason = reasons.get(self.status_code, 'Unknown')
        lines = [f'HTTP/1.0 {self.status_code} {reason}']
        for header, value in self.headers.items():
            lines.append(f'{header}: {value}')
        lines.append('')
        lines.append(self.body)
        return '\r\n'.join(lines)

class Microdot:
    def __init__(self):
        self.routes = {}
    def route(self, path, methods=['GET']):
        def decorator(f):
            self.routes[path] = f
            return f
        return decorator
    def run(self, host='0.0.0.0', port=8080):
        import usocket as socket
        addr = socket.getaddrinfo(host, port)[0][-1]
        s = socket.socket()
        s.bind(addr)
        s.listen(5)
        print('Listening on', addr)
        while True:
            conn, addr = s.accept()
            try:
                request_data = conn.recv(1024).decode()
                if not request_data:
                    conn.close()
                    continue
                lines = request_data.split('\r\n')
                if len(lines) < 1 or not lines[0]:
                    conn.close()
                    continue
                parts = lines[0].split(' ')
                if len(parts) < 2:
                    conn.close()
                    continue
                method, path = parts[0], parts[1]
                handler = self.routes.get(path.split('?')[0], None)
                if handler:
                    req = Request(method, path, {}, '')
                    res = handler(req)
                    if isinstance(res, str):
                        res = Response(res)
                else:
                    res = Response('Not Found', 404)
                conn.send(res.to_http())
            except Exception as e:
                print('Error:', e)
                try:
                    conn.send(Response('Internal Server Error', 500).to_http())
                except:
                    pass
            finally:
                conn.close()

def send_file(filename, content_type='text/html'):
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return Response(content, 200, {'Content-Type': content_type})
    except:
        return Response('Archivo no encontrado', 404)

CANTIDAD_LEDS = 30
PIN_TIRA = 27
np = neopixel.NeoPixel(Pin(PIN_TIRA), CANTIDAD_LEDS)

led_pins = {
    '1': Pin(32, Pin.OUT),
    '2': Pin(33, Pin.OUT),
    '3': Pin(25, Pin.OUT)
}

app = Microdot()

@app.route('/')
def index(request):
    return send_file('index.html')

@app.route('/styles/base.css')
def css(request):
    return send_file('styles/base.css', 'text/css')

@app.route('/scripts/base.js')
def js(request):
    return send_file('scripts/base.js', 'application/javascript')

@app.route('/toggle')
def toggle_led(request):
    import ure
    match = ure.search(r'led=(\d)', request.path)
    if match:
        led_num = match.group(1)
        if led_num in led_pins:
            led = led_pins[led_num]
            led.value(not led.value())
            print(f"LED {led_num} toggled to {led.value()}")
            return Response(f"LED {led_num} cambiado")
    return Response("LED no válido", 400)

@app.route('/color')
def set_color(request):
    try:
        if '?' not in request.path:
            return Response("Falta parámetro", 400)

        query = request.path.split('?', 1)[1]
        params = dict(param.split('=') for param in query.split('&') if '=' in param)

        if 'hex' not in params:
            return Response("Parámetro 'hex' faltante", 400)

        hex_color = params['hex'].strip()
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]

        print(f"Valor hex recibido (raw): '{params['hex']}'")
        print(f"Valor hex limpiado: '{hex_color}'")

        
        if len(hex_color) != 6 or any(c not in '0123456789abcdefABCDEF' for c in hex_color):
            return Response(f"Color inválido: '{hex_color}'", 400)

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        print(f"RGB a usar: R={r}, G={g}, B={b}")

        for i in range(CANTIDAD_LEDS):
            np[i] = (r, g, b)
        np.write()

        print("Tira actualizada")

        return Response(f"Tira encendida: #{hex_color.upper()}")

    except Exception as e:
        print("Error en /color:", e)
        return Response("Error interno", 500)

@app.route('/test_red')
def test_red(request):
    for i in range(CANTIDAD_LEDS):
        np[i] = (255, 0, 0)
    np.write()
    print("Tira encendida en rojo (test_red)")
    return Response("Tira en rojo")


app.run(port=8080)
