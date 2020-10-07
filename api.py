#!/usr/bin/env python3

from flask import Flask, request, redirect
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS
import pulsectl
import os

app = Flask(__name__)
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()

def get_sink_id(pulse, sink):
    server = pulse.server or '(local)'
    return f'{server}|{sink.name}'

def get_sinks(pulse):
    return [{ 'sink_id': get_sink_id(pulse, s), **s.proplist, 'channels': [{c: v} for c, v in zip(s.channel_list, s.volume.values)]} for s in pulse.sink_list()]

def get_sink_by_id(pulse, sink_id):
    return next(filter(lambda s: s['sink_id'] == sink_id, get_sinks(pulse)))

def get_pulse():
    server = os.environ.get('PULSE_SERVER', None)
    if server:
        return pulsectl.Pulse(server=server)
    return pulsectl.Pulse()

class SinkList(Resource):
    def get(self):
        # curl http://localhost:5000/sinks
        with get_pulse() as pulse:
            return get_sinks(pulse)

class Sink(Resource):
    def get(self, sink_id):
        with get_pulse() as pulse:
            return get_sink_by_id(pulse, sink_id)

class SinkChannels(Resource):
    def get(self, sink_id):
        with get_pulse() as pulse:
            sink = get_sink_by_id(pulse, sink_id)
            return sink['channels']

    def post(self, sink_id):
        # curl --header "Content-Type: application/json" --request POST --data '[{"front-left": 0.5}, {"front-right": 0.5}]' http://localhost:5000/sink/1/channels
        new_volumes_list = request.get_json()
        new_volumes_map = {}
        for o in new_volumes_list:
            new_volumes_map.update(o)

        res = []
        with get_pulse() as pulse:
            for sink in pulse.sink_list():
                if get_sink_id(pulse, sink) != sink_id:
                    continue

                new_volumes = []
                for channel_name, current_volume in zip(sink.channel_list, sink.volume.values):
                    new_volume = new_volumes_map.get(channel_name, current_volume)
                    new_volumes.append(new_volume)

                new_pulse_volume = pulsectl.PulseVolumeInfo(new_volumes)
                pulse.volume_set(sink, new_pulse_volume)
                break

            return get_sink_by_id(pulse, sink_id)['channels']

api.add_resource(SinkList, '/sinks')
api.add_resource(Sink, '/sink/<sink_id>')
api.add_resource(SinkChannels, '/sink/<sink_id>/channels')

if __name__ == '__main__':
    app.run(debug=True)
