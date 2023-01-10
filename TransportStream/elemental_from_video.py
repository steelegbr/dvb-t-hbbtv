#!/usr/bin/python3

from click import command, IntRange, option
from pathlib import Path
from subprocess import CalledProcessError, run
from tempfile import gettempdir, NamedTemporaryFile
from typing import IO
from uuid import uuid4

MAX_RATE = "5000k"
MIN_RATE = MAX_RATE
INTENDED_RATE = MAX_RATE
AUDIO_BITRATE = "128000"
AUDIO_SAMPLE_RATE = "48000"


def convert_to_mp2(input_path: str, path_audio_mp2: str, path_video_mp2: str):
    print("Performing FFMPEG conversion")

    video_enc_proc = run(
        [
            "ffmpeg",
            "-i",
            input_path,
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
            path_video_mp2,
        ],
        capture_output=True,
    )

    audio_enc_proc = run(
        [
            "ffmpeg",
            "-i",
            input_path,
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
            path_audio_mp2,
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


def convert_to_pes(
    path_audio_mp2: str,
    path_video_mp2: str,
    temp_audio_pes: IO[bytes],
    temp_video_pes: IO[bytes],
):
    print("Converting MPEG 2 streams to PES")

    video_pes_proc = run(
        [
            "esvideompeg2pes",
            path_video_mp2,
        ],
        capture_output=True,
    )

    audio_pes_proc = run(
        [
            "esaudio2pes",
            path_audio_mp2,
        ],
        capture_output=True,
    )

    temp_video_pes.write(video_pes_proc.stdout)
    temp_audio_pes.write(audio_pes_proc.stdout)
    temp_video_pes.flush()
    temp_audio_pes.flush()


def convert_to_ts(
    temp_audio_pes: IO[bytes],
    temp_video_pes: IO[bytes],
    path_audio_ts: str,
    path_video_ts: str,
    video_pid,
    audio_pid,
):
    print("Converting PES to TS")

    video_ts_proc = run(
        [
            "pesvideo2ts",
            f"{video_pid}",
            "25",
            "112",
            "7000000",
            "0",
            temp_video_pes.name,
        ],
        capture_output=True,
    )

    audio_ts_proc = run(
        [
            "pesaudio2ts",
            f"{audio_pid}",
            "1152",
            "48000",
            "384",
            "0",
            temp_audio_pes.name,
        ],
        capture_output=True,
    )

    with open(path_video_ts, "w+b") as video_ts_file, open(
        path_audio_ts, "w+b"
    ) as audio_ts_file:
        video_ts_file.write(video_ts_proc.stdout)
        audio_ts_file.write(audio_ts_proc.stdout)


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
@option("--video-pid", prompt="PID for the video stream", type=IntRange(1, 8191))
@option("--audio-pid", prompt="PID for the audio stream", type=IntRange(1, 8191))
def generate_elemental_streams(input: str, output: str, video_pid: int, audio_pid: int):
    """
    Generates elemental streams for multiplexing from a input video file.
    """

    input_path = Path(input)
    if not input_path.is_file():
        print(f"{input} is not a video file!")
        return

    temp_path_base = Path(gettempdir())
    temp_file_name = uuid4()

    path_video_mp2 = temp_path_base / f"{temp_file_name}_video.mp2"
    path_audio_mp2 = temp_path_base / f"{temp_file_name}_audio.mp2"
    path_video_ts = f"{output}_video.ts"
    path_audio_ts = f"{output}_audio.ts"

    temp_video_pes = NamedTemporaryFile()
    temp_audio_pes = NamedTemporaryFile()

    convert_to_mp2(input, path_audio_mp2, path_video_mp2)
    convert_to_pes(path_audio_mp2, path_video_mp2, temp_video_pes, temp_audio_pes)
    convert_to_ts(
        temp_audio_pes,
        temp_video_pes,
        path_audio_ts,
        path_video_ts,
        video_pid,
        audio_pid,
    )


if __name__ == "__main__":
    generate_elemental_streams()
