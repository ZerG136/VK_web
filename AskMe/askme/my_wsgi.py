from urllib.parse import parse_qs

def application(environ, start_response):
    print("Request Environment:", environ)

    query_string = environ.get('QUERY_STRING', '')
    print("Query String:", query_string)

    method = environ.get('REQUEST_METHOD', 'GET')
    print("Request Method:", method)

    if method == 'GET':
        params = parse_qs(query_string)
    elif method == 'POST':
        try:
            length = int(environ.get('CONTENT_LENGTH', 0))
            post_data = environ['wsgi.input'].read(length).decode()
            print("POST Data:", post_data)
            params = parse_qs(post_data)
        except (ValueError, KeyError):
            params = {}
    else:
        raise NotImplementedError

    response_body = f"GET and POST parameters: {params}"

    status = '200 OK'
    response_headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, response_headers)

    return [response_body.encode('utf-8')]
