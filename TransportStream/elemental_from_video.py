#!/usr/bin/python3

from click import command, option
from pathlib import Path
from subprocess import CalledProcessError, run

MAX_RATE = "5000k"
MIN_RATE = MAX_RATE
INTENDED_RATE = MAX_RATE
AUDIO_BITRATE = "128000"
AUDIO_SAMPLE_RATE = "48000"


@command()
@option(
    "--input",
    prompt="Input Video File",
    help="The name of the video file elemental streams will be generated from",
)
@option(
    "--output",
    prompt="Output File Prefix",
    help="The prefix to output the elemental streams to. These will be appened with _audio.pes and _video.pes.",
)
def generate_elemental_streams(input: str, output: str):
    """
    Generates elemental streams for multiplexing from a input video file.
    """

    input_path = Path(input)
    if not input_path.is_file():
        print(f"{input} is not a video file!")
        return
    
    print("Performing FFMPEG conversion")

    video_enc_proc = run(
        [
            "ffmpeg",
            "-i",
            input,
            "-an",
            "-vcodec",
            "mpeg2video",
            "-f",
            "mpeg2video",
            "-b",
            INTENDED_RATE,
            "-maxrate",
            MAX_RATE,
            "-minrate",
            MIN_RATE,
            "-bf",
            "2",
            "-bufsize",
            "1835008",
            "-y",
            f"{output}_video.mp2",
        ],
        capture_output=True,
    )

    audio_enc_proc = run(
        [
            "ffmpeg",
            "-i",
            input,
            "-ac",
            "2",
            "-vn",
            "-acodec",
            "mp2",
            "-f",
            "mp2",
            "-ab",
            AUDIO_BITRATE,
            "-ar",
            AUDIO_SAMPLE_RATE,
            "-y",
            f"{output}_audio.mp2",
        ],
        capture_output=True,
    )

    try:
        video_enc_proc.check_returncode()
    except CalledProcessError:
        print("Failed to perform video FFPEG encoding. See below for details:")
        print(video_enc_proc.stderr.decode("utf-8"))
        return
    
    try:
        audio_enc_proc.check_returncode()
    except CalledProcessError:
        print("Failed to perform audio FFPEG encoding. See below for details:")
        print(audio_enc_proc.stderr.decode("utf-8"))
        return

    print("Converting MPEG 2 streams to PES")

    print("Converting PES to TS")

if __name__ == "__main__":
    generate_elemental_streams()
