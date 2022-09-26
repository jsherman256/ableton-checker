import streamlit as st
import gzip
import xml.etree.ElementTree as ET
import xmltodict

# Return a tuple (Id, dict()) where the dict has metadata on the track
def analyze_track(track):
    return (track['@Id'], {
        'name': track['Name']['EffectiveName']['@Value'],
        'color': track['Color']['@Value'],
        'input': track['DeviceChain']['AudioInputRouting']['UpperDisplayString']['@Value'],
        'frozen': None if 'Freeze' not in track else track['Freeze']['@Value'],
        'device_chain': analyze_devices(track['DeviceChain']['DeviceChain']['Devices']),
    })

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

# Compress the analyzed tracks into a dict
def get_track_dict(tracks):
    return {k: v for (k, v) in [analyze_track(t) for t in tracks]}

als_file = st.file_uploader('Ableton Live Session')
if als_file:
    compressed_data = als_file.getvalue()
    xml_data = gzip.decompress(compressed_data).decode()
    als_dict = xmltodict.parse(xml_data)

    all_tracks = als_dict['Ableton']['LiveSet']['Tracks']

    # If there's only a single track, we get it as a dict; Make it a length-1 list instead
    midi_tracks = [all_tracks['MidiTrack']] if type(all_tracks['MidiTrack']) == dict else all_tracks['MidiTrack']
    audio_tracks = [all_tracks['AudioTrack']] if type(all_tracks['AudioTrack']) == dict else all_tracks['AudioTrack']
    return_tracks = [all_tracks['ReturnTrack']] if type(all_tracks['ReturnTrack']) == dict else all_tracks['ReturnTrack']

    midi = get_track_dict(midi_tracks)
    audio = get_track_dict(audio_tracks)
    returns = get_track_dict(return_tracks)

    all = {
        'Midi': midi,
        'Audio': audio,
        'Returns': returns
    }

    st.write(all)