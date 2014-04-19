import os, sys
import re
import shutil
import subprocess
from . import Project, walk_projects

"""
Renders video of repository commit history using gource, adds background song.

Prerequisites::

    sudo port install ffmpeg gource mp3wrap

Synopsis::

    bin/gource-render-single \
        --name acme-trunk \
        --path ~/dev/three-investigators/acme/trunk \
        --audio-source '/home/foobar/music/Beastie boys/Suco De Tangerina.mp3' \
        --audio-loops 50 \
        # --overwrite
"""

class GourceRenderer(object):
    """Renders project history using 'gource'."""

    def __init__(self, source_path, target_path, overwrite = False, audio_source = None, audio_loops = None):

        self.project_path = source_path
        self.output_path = target_path

        # configuration data
        self.gource_cmd_tpl = """
            gource --title "%(title)s"  \\
                --seconds-per-day 5 --time-scale 1.5  \\
                --disable-auto-rotate --file-idle-time 20  \\
                --hide bloom  \\
                --stop-at-end -o -"""

        # options
        self.overwrite = overwrite
        if audio_loops is None:
            audio_loops = 10
        self.audio_source = audio_source
        self.audio_loops = audio_loops

    def get_gource_command(self, title):
        gource_options = {
            'title': title,
        }
        command = self.gource_cmd_tpl % gource_options
        return command

    def choose_background_song(self):
        # TODO: enhance song picker (e.g. random or mapped selection from a directory)
        if self.audio_source and os.path.isfile(self.audio_source):
            return self.audio_source
        elif os.path.isfile(os.environ.get('GOURCE_AUDIO_SOURCE', '')):
            return os.environ.get('GOURCE_AUDIO_SOURCE')

    def process_projects(self):

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        """Scans all main level directories in the projects directory"""
        for project in walk_projects(self.project_path):

            if project.name.endswith('-develop'): continue
            self.process_project(project)
            print

            # debugging (exit after processing one video)
            #break

    def process_project(self, project):

        print "=" * 42
        print "Processing project '%s'" % project.name
        print "=" * 42

        video_file = self.create_video(project.path, self.output_path, project.name)
        if not video_file:
            print "ERROR: video could not be created"
            return False

        mi = MediaInfo(video_file)
        if not 'video' in mi.get_streams():
            print "ERROR: video '%s' could not be recorded" % video_file
            os.unlink(video_file)
            video_file = None
            return False

        return True

    def create_video(self, project_path, video_path, video_filename):

        vr = VideoRecorder(video_path, video_filename)
        if vr.exists() and not self.overwrite:
            return vr.get_video_file()

        background_song = self.choose_background_song()
        if background_song:
            audio_source = self.loop_audio(background_song, self.audio_loops)
            vr.set_audio_source(audio_source)

        print "-" * 42
        print "Creating video '%s'" % vr.get_video_file()
        cd_cmd = 'cd "%s"' % project_path
        run_cmd = self.get_gource_command(title = video_filename) + ' | ' + vr.get_command()
        cmd = cd_cmd + '; ' + run_cmd
        print "command:", cmd
        print "-" * 42

        if self.run_command(cmd):
            return vr.get_video_file()

    def run_command(self, command):
        returncode = os.system(command)
        if returncode == 0:
            return True
        else:
            print "ERROR while executing command '%s'" % command
            return False

    def loop_audio(self, audio_source, times = 2):

        # TODO: remove looped audio file after usage

        name = os.path.basename(audio_source)
        audio_sources = ('"%s" ' % audio_source) * times
        mp3wrap_file = "/tmp/tmp_%s" % name

        if not times or times <= 1:
            shutil.copy(audio_source, mp3wrap_file)
            return mp3wrap_file

        # WTF?
        mp3wrap_file_real = mp3wrap_file.replace('.mp3', '_MP3WRAP.mp3')
        if os.path.exists(mp3wrap_file_real):
            os.unlink(mp3wrap_file_real)

        mp3wrap_command = 'mp3wrap "%s" %s' % (mp3wrap_file, audio_sources)
        if self.run_command(mp3wrap_command):
            return mp3wrap_file_real


class MediaInfo(object):

    """
      Duration: 00:00:01.73, start: 0.000000, bitrate: 662 kb/s
        Stream #0.0(und): Video: h264, yuv420p, 1024x768, 651 kb/s, 60 fps, 59.94 tbr, 60 tbn, 120 tbc
    """

    def __init__(self, mediafile):
        self.mediafile = mediafile
        self.raw = ""
        self.duration = ""
        self.streams = []
        self.read_info()
        self.parse_info()

    def read_info(self):
        cmd = 'ffmpeg -i "%s"' % self.mediafile
        p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
        stdout, stderr = p.communicate()
        self.raw = stderr

    def parse_info(self):
        r_duration = re.compile('.*Duration: ([.:0-9]+)')
        r_stream = re.compile('.*Stream .*: (Video|Audio)')
        for line in self.raw.split("\n"):
            m = r_duration.match(line)
            if m: self.duration = m.group(1)
            m = r_stream.match(line)
            if m: self.streams.append(m.group(1).lower())

    def get_duration(self):
        return self.duration

    def get_streams(self):
        return self.streams


class VideoRecorder(object):

    def __init__(self, video_path, video_name, audio_source = None):
        self.video_path = video_path
        self.video_name = video_name
        self.video_file = self.get_video_file()
        self.audio_source = audio_source

    def get_command(self):
        arguments = self.__dict__.copy()

        # compute additional options when audio source is given
        arguments['audio_mixin'] = ''
        if arguments['audio_source']:
            arguments['audio_mixin'] = '-i "%(audio_source)s" -shortest' % arguments

        # Some remarks about "ffmpeg" options:
        #   - The encoder 'aac' is experimental but experimental codecs are not enabled,
        #     add '-strict -2' if you want to use it.
        command = """
            ffmpeg -y \\
                -r 60 -f image2pipe -vcodec ppm \\
                -i - \\
                %(audio_mixin)s \\
                -vcodec libx264 -preset slow -threads 0 \\
                -strict -2 \\
                -shortest \\
                "%(video_file)s" \\
            """ % arguments
        return command

    def get_video_file(self):
        return os.path.join(self.video_path, self.video_name + self.get_extension())

    def get_extension(self):
        return '.mp4'

    def exists(self):
        return os.path.exists(self.get_video_file())

    def set_audio_source(self, audio_source):
        self.audio_source = audio_source


def render_all():
    """Renders all projects' vcs repositories"""

    print "Rendering project history of all projects using 'gource'"
    source_path = sys.argv[1]
    target_path = sys.argv[2]

    if not os.path.isdir(target_path):
        os.makedirs(target_path)

    gr = GourceRenderer(source_path, target_path)
    gr.process_projects()


def render_single():
    """
    Renders single projects' vcs repository, e.g.::

        bin/gource-render-single \
            --name acme-trunk \
            --path ~/dev/three-investigators/acme/trunk \
            --audio-source '/home/foobar/music/Beastie boys/Suco De Tangerina.mp3' \
            --audio-loops 50 \
            # --overwrite
    """

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p", "--path", dest = "path", help = "path to vcs repository")
    parser.add_option("-n", "--name", dest = "name", help = "project name (output video basename w/o extension) [optional]")
    parser.add_option("-a", "--audio-source", dest = "audio_source", type = "str", help = "path to background song")
    parser.add_option("-l", "--audio-loops", dest = "audio_loops", type = "int", help = "how often to loop the given background song (*must* be longer than video since ffmpeg is started with option '-shortest')")
    parser.add_option("-o", "--overwrite", dest = "overwrite", action = "store_true", help = "whether to overwrite video files")
    (options, args) = parser.parse_args()

    if not options.path:
        print "ERROR: Option '--path' is mandatory!"
        sys.exit(1)

    options.path = os.path.abspath(options.path)
    if not os.path.isdir(options.path):
        print "ERROR: Directory '%s' does not exist" % options.path
        sys.exit(1)

    if not options.name:
        options.name = os.path.basename(options.path)

    print "Rendering project history of single project '%s <%s>' using 'gource'" % (options.name, options.path)
    source_path = sys.argv[1]
    target_path = sys.argv[2]
    gr = GourceRenderer(source_path, target_path, overwrite = options.overwrite, audio_source = options.audio_source, audio_loops = options.audio_loops)
    gr.process_project(Project(name=options.name, path=options.path))

if __name__ == '__main__':
    render_all()
