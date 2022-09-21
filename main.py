import streamlit as st
import gzip
import xml.etree.ElementTree as ET
import xmltodict

def analyze_devices(devices):
    d = []
    plugin_type = 'builtin'
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

def analyze_track(track):
    return {
        'name': track['Name']['EffectiveName']['@Value'],
        'color': track['Color']['@Value'],
        'input': track['DeviceChain']['AudioInputRouting']['UpperDisplayString']['@Value'],
        'frozen': None if 'Freeze' not in track else track['Freeze']['@Value'],
        'device_chain': analyze_devices(track['DeviceChain']['DeviceChain']['Devices']),
    }

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

    st.write(f"Found {len(midi_tracks)} MIDI track(s)")
    for t in midi_tracks:
        st.write(analyze_track(t))
    st.write(f"Found {len(audio_tracks)} audio track(s)")
    for t in audio_tracks:
        st.write(analyze_track(t))
    st.write(f"Found {len(return_tracks)} return track(s)")
    for t in return_tracks:
        st.write(analyze_track(t))

    #st.write(type(als_dict['Ableton']['LiveSet']['Tracks']['MidiTrack']))
    #st.write(analyze_track(als_dict['Ableton']['LiveSet']['Tracks']['MidiTrack']))
    #st.write(als_dict['Ableton']['LiveSet']['Tracks']['AudioTrack'][18])
