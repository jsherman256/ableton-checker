import streamlit as st
import gzip
import xml.etree.ElementTree as ET
import xmltodict

# Find and analyze all tracks of a certain type
def get_tracks_by_type(all_tracks, track_type):
    # If there's only a single track, we get it as a dict; Make it a length-1 list instead
    tracks = [all_tracks[track_type]] if type(all_tracks[track_type]) == dict else all_tracks[track_type]

    # Analyze each track (and its devices) and return the data as a nice dict
    return {k: v for (k, v) in [analyze_track(t) for t in tracks]}


# Takes a single track object
# Return a tuple (Id, dict()) where the dict has metadata on the track
def analyze_track(track):
    return (track['@Id'], {
        'name': track['Name']['EffectiveName']['@Value'],
        'color': track['Color']['@Value'],
        'input': track['DeviceChain']['AudioInputRouting']['UpperDisplayString']['@Value'],
        'frozen': None if 'Freeze' not in track else track['Freeze']['@Value'],
        'device_chain': analyze_devices(track['DeviceChain']['DeviceChain']['Devices']),
    })


# Take devices object for a single track
# Return information about the devices on that track
def analyze_devices(devices):
    d = []
    plugin_type = 'builtin'
    if not devices:
        return []
    for name, data in devices.items():
        if name == 'AuPluginDevice':
            name = data['PluginDesc']['AuPluginInfo']['Name']['@Value']
            plugin_type = 'AU'
        elif name == 'PluginDevice':
            if "Vst3PluginInfo" in data['PluginDesc']:
                name = data['PluginDesc']['Vst3PluginInfo']['Name']['@Value']
                plugin_type = 'VST3'
            elif "VstPluginInfo" in data['PluginDesc']:
                name = data['PluginDesc']['VstPluginInfo']['PlugName']['@Value']
                plugin_type = 'VST'
        d.append((name, plugin_type))
    return d


als_file = st.file_uploader('Ableton Live Session')
if als_file:
    compressed_data = als_file.getvalue()
    xml_data = gzip.decompress(compressed_data).decode()
    
    all_tracks = xmltodict.parse(xml_data)['Ableton']['LiveSet']['Tracks']

    all = {
        'Midi': get_tracks_by_type(all_tracks, 'MidiTrack'),
        'Audio': get_tracks_by_type(all_tracks, 'AudioTrack'),
        'Groups': get_tracks_by_type(all_tracks, 'GroupTrack'),
        'Returns': get_tracks_by_type(all_tracks, 'ReturnTrack'),
    }

    st.write(all)