import os, sys
from . import walk_projects

bugseverywhere_script = os.environ.get('BE', 'be')

def bugseverywhere_walk_projects(source_path):
    """Scans all main level directories in the projects directory for
    an active 'BugsEverywhere' (i.e. contains a directory '.be')"""
    for project in walk_projects(source_path):
        bugseverywhere_path = os.path.join(project.path, '.be')
        if os.path.exists(bugseverywhere_path):
            yield project.name, project.path

def bugseverywhere_build_html(source_path, target_path):
    """Converts 'BugsEverywhere' issues to HTML"""
    command = 'cd "%s"; "%s" html --output="%s"' % (source_path, bugseverywhere_script, target_path)
    try:
        os.system(command)
    except:
        print >>sys.stderr, "ERROR while executing command: %s" % command

def build_html():
    print "Generating HTML from BugsEverywhere issues for these projects:"
    source_path = sys.argv[1]
    for project_name, project_path in bugseverywhere_walk_projects(source_path):
        print project_name
        target_path = os.path.join(issues_html_path, project_name)
        if not os.path.isdir(target_path):
            os.makedirs(target_path)
        bugseverywhere_build_html(project_path, target_path)
