import tempfile
import os, sys
import subprocess
import time
from . import walk_projects, rest_header

class Statistics:

    def __init__(self, artefact_path, output_path, index_path):

        # which directory to scan for repositories
        self.artefact_path = artefact_path

        # base directory for output
        self.output_path = output_path

        # index page in reStructuredText format
        self.statistics_index = os.path.join(index_path, 'statistics.rst')

        # 3rd party tools
        self.gitstats = os.environ.get('GITSTATS', 'gitstats')
        self.statsvn = os.environ.get('STATSVN', 'statsvn.jar')

        # all projects to work on
        self.projects = []

        # don't render statistics for "gitstats" itself
        self.projects_blacklist = ['gitstats', 'statsvn', '-develop']

        # just regenerate every week
        self.regenerate_threshold = 60 * 60 * 24 * 7

        # for debugging purposes (generate statistics for listed projects only, if not empty)
        self.projects_whitelist = []
        #self.projects_whitelist = ['image_proxy']


    def scan_projects(self):
        for project in walk_projects(self.artefact_path):

            # compute whether to skip this project by blacklist
            skip = False
            for blacklist_item in self.projects_blacklist:
                if blacklist_item in project.name:
                    skip = True
            if skip: continue

            if project.vcs in ('git', 'svn'):
                if not self.projects_whitelist or (self.projects_whitelist and project.name in self.projects_whitelist):
                    self.projects.append(project)

    def write_index(self):
        path = os.path.dirname(self.statistics_index)
        if not os.path.isdir(path):
            os.makedirs(path)
        f = open(self.statistics_index, 'w')
        f.write(rest_header('Repository statistics', 'zt.manticore.ext.statistics'))
        f.write('Statistics of the following projects:\n\n')
        for project in self.projects:
            f.write('- `{0} <./statistics/{0}/index.html>`_'.format(project.name))
            f.write('\n')
        f.write('\n\n\n')
        f.close()

    def generate_statistics(self):
        git_projects = []
        for project in self.projects:
            print "Generating statistics for {0}".format(project)
            if project.vcs == 'git':
                self.run_gitstats(project)
                git_projects.append(project)
            elif project.vcs == 'svn':
                cwd = os.getcwd()
                try:
                    self.run_statsvn(project)
                    #pass
                #except:
                #    pass
                finally:
                    os.chdir(cwd)

        # 2011-11-07: generate multi-repo statistics
        self.run_gitstats_multi(git_projects, alias='all-git')

    def is_up_to_date(self, output_path):
        # check if it actually should be regenerated
        try:
            path_to_index = os.path.join(output_path, 'index.html')
            project_mtime = os.stat(path_to_index).st_mtime
            now = time.time()
            if abs(now - project_mtime) < self.regenerate_threshold:
                return True
        except:
            pass
        return False

    def get_output_path(self, project):
        output_path = os.path.join(self.output_path, project.name)
        return output_path

    def run_command(self, command):
        returncode = subprocess.call(command)
        if returncode != 0:
            print "Command '{0}' had errors, exit code was {1}".format(' '.join(command), returncode >> 8)

    def run_command_system(self, command):
        command = ' '.join(command)
        returncode = os.system(command)
        if returncode == 0:
            return True
        else:
            print "Command '{0}' had errors, exit code was {1}".format(command, returncode >> 8)
            return False

    def run_gitstats(self, project):
        # example: ./parts/gitstats/gitstats -c project_name=foobar -c max_authors=60 .git /tmp/test/
        input_path = os.path.join(project.path, '.git')
        output_path = self.get_output_path(project)
        if self.is_up_to_date(output_path):
            return

        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        print "Running 'gitstats' for project '{0}'".format(project.name)
        command = [self.gitstats, '-c', 'project_name={0}'.format(project.name), '-c', 'max_authors=60', input_path, output_path]
        self.run_command(command)

    def run_gitstats_multi(self, projects, alias):
        input_paths = []
        project_names = []
        for project in projects:
            input_paths.append(os.path.abspath(os.path.join(project.path, '.git')))
            project_names.append(project.name)

        output_path = os.path.join(self.output_path, alias)
        if self.is_up_to_date(output_path):
            return

        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        #print "Running 'gitstats' for multiple projects '{0}'".format(input_paths)
        command = [self.gitstats, '-c', 'project_name={0}'.format(', '.join(project_names))]
        command += input_paths
        command.append(output_path)
        print "command:", command
        self.run_command(command)

    def run_statsvn(self, project):
        # http://wiki.statsvn.org/
        # example:
        # svn log -v --xml parts/acme/ > tmp_svn.log
        # java -jar parts/statsvn/statsvn.jar tmp_svn.log parts/acme/

        input_path = project.path
        output_path = self.get_output_path(project)
        if self.is_up_to_date(output_path):
            return

        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        print "Running 'svn log' and 'StatSVN' for project '{0}'".format(project.name)

        # run "svn log"
        tempdir = tempfile.mkdtemp()
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
        svn_log = os.path.join(tempdir, '{0}.svnlog'.format(project.name))
        command = ['svn', 'log', '-v', '--xml', input_path, '>', svn_log]
        success = self.run_command_system(command)

        # fix svn log
        if not success:
            payload = file(svn_log).read()
            if '<log>' in payload and not '</log>' in payload:
                payload += '\n</log>\n'
                file(svn_log, 'w').write(payload)

        # run "statsvn.jar"
        os.chdir(output_path)
        command = ['java', '-mx768m', '-jar', self.statsvn, svn_log, input_path]
        self.run_command_system(command)

def build_statistics():
    print "Generating repository statistics"
    artefact_path = sys.argv[1]
    output_path = sys.argv[2]
    index_path = sys.argv[3]
    stats = Statistics(artefact_path, output_path, index_path)
    stats.scan_projects()
    stats.write_index()
    stats.generate_statistics()
