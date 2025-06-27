import ure as re
import sys
import ujson as json

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
        reason = 'OK' if self.status_code == 200 else 'Not Found'
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

    def run(self, host='0.0.0.0', port=8080): #Tuve que buscar como cambiar de puerto por que me tiraba error de puerto usado.
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
                handler = self.routes.get(path, None)

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

app.run(port=8080)
