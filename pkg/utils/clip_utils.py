import subprocess
from pydub import AudioSegment


def create_clip(yt_resource, start, duration, output_file):
    resources = str(subprocess.check_output(["youtube-dl", "-g", yt_resource])).split("\\n")
    subprocess.call(['ffmpeg', '-y', '-ss', start, '-i', resources[1], '-t', duration, '-b:a', '192k', output_file])


# clips_metadata is list of tuples (clip file path, position in ms).
# Overlay all audio at interval specified by delay. Save to filesystem
def mix_clips(clips_metadata):
    # Parse all clips
    clips = [(AudioSegment.from_wav(path) if '.wav' in path else AudioSegment.from_mp3(path), position)
             for path, position in clips_metadata]

    # Determine duration of new sound
    dur = max([len(clip) + position for clip, position in clips])

    [len(clip) + position for clip, position in clips]

    # Create silent sound, overlay other sounds on top
    final_sound = AudioSegment.silent(duration=dur)
    for clip, pos in clips:
        final_sound = final_sound.overlay(clip, position=pos)

    # Save the final result
    final_sound.export('resources/tmp.mp3', format='mp3')


def clip_length(path):
    clip = AudioSegment.from_wav(path) if '.wav' in path else AudioSegment.from_mp3(path)
    return len(clip)
