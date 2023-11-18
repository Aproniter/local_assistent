import argparse
import queue
import sys
import sounddevice as sd
import json


from vosk import Model, KaldiRecognizer
from playsound import playsound

import commands
import db
import config
from voice_buffer_parser import VoiceBufferParser
from logger import logger as log


q = queue.Queue()

buffer = []


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)

command_flag = 0
voice_buffer = []


def parse_command(data):
    global command_flag, voice_buffer
    if data in commands.create_note:
        playsound(f'{config.sounds_path}/record_start.mp3')
        command_flag = 1
    elif data in commands.close_note:
        playsound(f'{config.sounds_path}/understand.mp3')
        command_flag = 0
        VoiceBufferParser('note_creater', voice_buffer, config.notes_path, config.db_path)
        voice_buffer = []
    elif data in commands.save_page:
        playsound(f'{config.sounds_path}/understand.mp3')
        VoiceBufferParser('save_internet_page', voice_buffer, config.notes_path, config.db_path)
    else:
        if command_flag:
            playsound(f'{config.sounds_path}/understand.mp3')
            voice_buffer.append(data)

if __name__ == '__main__':
    db.create_notes_table(config.db_path)
    try:
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, "input")
            args.samplerate = int(device_info["default_samplerate"])

        model = Model(r"vosk-model-small-ru-0.22")
        # model = Model(r"vosk-model-ru-0.22") # ноут не тянет
        # model = Model(r"vosk-model-ru-0.42") # ноут не тянет

        if args.filename:
            dump_fn = open(args.filename, "wb")
        else:
            dump_fn = None

        with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
                dtype="int16", channels=1, callback=callback):
            log.info("Press Ctrl+C to stop the recording")

            rec = KaldiRecognizer(model, args.samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if result['text']:
                        if len(buffer) > 100:
                            with open('record.txt', 'a+') as record:
                                record.writelines(buffer)
                                buffer = []
                        buffer.append(result['text'])
                        print(result['text'])
                        parse_command(result['text'])

                if dump_fn is not None:
                    dump_fn.write(data)

    except KeyboardInterrupt:
        log.info("\nDone")
        parser.exit(0)
    # except Exception as e:
    #     parser.exit(type(e).__name__ + ": " + str(e))