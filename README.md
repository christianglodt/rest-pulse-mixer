# rest-pulse-mixer
A simple REST API for changing the volume of PulseAudio sinks. It is developed
together with its frontend [react-pulse-mixer](https://github.com/christianglodt/react-pulse-mixer).

## Configuration
Configure the PulseAudio server to connect to using the `PULSE_SERVER` environment variable. You can also configure a path prefix using the `PATH_PREFIX` environment variable.

## API
Nr | URL | Method | Description
---|-----|--------|------------
 1 | `/sinks` | GET | Retrieve a list of all sinks
 2 | `/sink/<sink_id>` | GET | Retrieve a single sink by its sink_id
 3 | `/sink/<sink_id>/channels` | GET | Retrieve the channel volumes of single sink
 4 | `/sink/<sink_id>/channels` | POST | Set channel volumes of a single sink

The endpoints work as follows:
1. Returns a list of sinks including all their properties. Also includes a computed
   `sink_id` field that is used by other endpoints to identify a sink.
1. Returns a single sink.
1. Returns the channel volumes of a sink identified by a sink_id in the following
   format: `{ <channel_name>: <volume>, ... }`. Example: `{ left: 0.5, right: 0.5}`.
1. Sets the channel volumes of a sink identified by a sink_id using the same format
   as described in the previous point. Channels that are not included remain
   unmodified.
