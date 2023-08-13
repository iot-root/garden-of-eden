from flask import Flask, Response
import json

app = Flask('app')

@app.route('/', methods=['GET'])
def home():
  res = {
    'apis': [
      {
        'path': '/pump',
        'method': 'GET',
        'purpose': 'Returns current status of pump'
      },
      {
        'path': '/pump/on',
        'method': 'POST',
        'purpose': 'Turns on the pump'
      },
      {
        'path': '/pump/off',
        'method': 'POST',
        'purpose': 'Turns off the pump'
      },
      {
        'path': '/led',
        'method': 'GET',
        'purpose': 'Returns current status of led'
      },
      {
        'path': '/led/on',
        'method': 'POST',
        'purpose': 'Turns on the LED at 100%'
      },
      {
        'path': '/led/off',
        'method': 'POST',
        'purpose': 'Turns off the LED'
      },
      {
        'path': '/led/adjust',
        'method': 'POST',
        'purpose': 'Adjust the LED to given percentage'
      }
    ]
  }
  return build_response(res, 200)

def build_response(res, status):
  r = Response(response=json.dumps(res), status=status, mimetype='text/json')
  r.headers['Content-Type'] = 'text/json; charset=utf-8'
  return r


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)