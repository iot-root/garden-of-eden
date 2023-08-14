# coding=utf-8
import os
from threading import Thread
from flask import Flask, request, jsonify
from sensors.led import LED

app = Flask('app')
lights = None


@app.route('/ping', methods=['GET', 'POST'])
def ping():
    res = {
        'code': 200,
        'data': 'ok',
        'page': ''
    }
    return jsonify(res)


@app.route('/led', methods=['GET', 'POST'])
def led():
    global lights
    if lights is None:
        lights = LED()
    operation_complete = False
    command = request.args.get('command')
    if command.lower() == 'off':
        command = '0'
    if command.lower() in ['max', 'on']:
        command = '100'
    if command.lower() in ['+', 'lighter', 'brighter']:
        command = 'lighter'
        lights.lighter()
        operation_complete = True
    if command.lower() in ['-', 'darker', 'dimmer']:
        command = 'dimmer'
        lights.dimmer()
        operation_complete = True
    if operation_complete is False:
        success = lights.adjust(command)
        if success is not False:
            success = True
    else:
        success = True
    if success:
        res = {
            'code': 200,
            'data': 'Lights successfully set to {}'.format(command),
            'page': ''
        }
    else:
        res = {
            'code': 501,
            'data': 'Lights could not be set to {}'.format(command),
            'page': ''
        }
    return jsonify(res)


# TODO: Implement waterlevel endpoints #29
# TODO: Implement temprature and humidity endpoints #30
# TODO: Implement Camera api endpoints #31
# TODO: Implement schedule api endpoints #32


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8011)
