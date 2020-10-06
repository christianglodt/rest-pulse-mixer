#!/usr/bin/env python3

from flask import Flask, request, redirect
from flask_restful import reqparse, abort, Api, Resource
import pulsectl

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

def get_sinks(pulse):
    return [{ 'sink_index': s.index, **s.proplist, 'channels': [{c: v} for c, v in zip(s.channel_list, s.volume.values)]} for s in pulse.sink_list()]

def get_sink_by_index(pulse, sink_index):
    return next(filter(lambda s: s['sink_index'] == int(sink_index), get_sinks(pulse)))

class SinkList(Resource):
    def get(self):
        # curl http://localhost:5000/sinks
        with pulsectl.Pulse() as pulse:
            return get_sinks(pulse)

class Sink(Resource):
    def get(self, sink_index):
        with pulsectl.Pulse() as pulse:
            return get_sink_by_index(pulse, sink_index)

class SinkChannels(Resource):
    def get(self, sink_index):
        with pulsectl.Pulse() as pulse:
            sink = get_sink_by_index(pulse, sink_index)
            return sink['channels']

    def post(self, sink_index):
        # curl --header "Content-Type: application/json" --request POST --data '[{"front-left": 0.5}, {"front-right": 0.5}]' http://localhost:5000/sink/1/channels
        new_volumes_list = request.get_json()
        new_volumes_map = {}
        for o in new_volumes_list:
            new_volumes_map.update(o)

        res = []
        with pulsectl.Pulse() as pulse:
            for sink in pulse.sink_list():
                if sink.index != int(sink_index):
                    continue

                new_volumes = []
                for channel_name, current_volume in zip(sink.channel_list, sink.volume.values):
                    new_volume = new_volumes_map.get(channel_name, current_volume)
                    new_volumes.append(new_volume)

                new_pulse_volume = pulsectl.PulseVolumeInfo(new_volumes)
                pulse.volume_set(sink, new_pulse_volume)
                break

            return get_sink_by_index(pulse, sink_index)['channels']

api.add_resource(SinkList, '/sinks')
api.add_resource(Sink, '/sink/<sink_index>')
api.add_resource(SinkChannels, '/sink/<sink_index>/channels')

if __name__ == '__main__':
    app.run(debug=True)
