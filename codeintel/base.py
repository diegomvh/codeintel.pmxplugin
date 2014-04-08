#!/usr/bin/env python
from __future__ import print_function

VERSION = "1.0"

import os
import stat
import time
import datetime
import threading
import logging

from codeintel2.manager import Manager
from codeintel2.environment import SimplePrefsEnvironment
from codeintel.utils import get_revision, tryGetMTime, find_back, tryReadDict

CODEINTEL_HOME_DIR = os.path.expanduser(os.path.join('~', '.codeintel'))

codeintel_log = logging.getLogger("codeintel")
log = logging.getLogger("SublimeCodeIntel")
condeintel_log_filename = ''
condeintel_log_file = None

_ci_mgr_ = {}
_ci_envs_ = {}
_ci_next_scan_ = {}

def codeintel_manager(folders_id):
    folders_id = None
    global _ci_mgr_, condeintel_log_filename, condeintel_log_file
    mgr = _ci_mgr_.get(folders_id)
    if mgr is None:
        for thread in threading.enumerate():
            if thread.name == "CodeIntel Manager":
                thread.finalize() # this finalizes the index, citadel and the manager and waits them to end (join)
        mgr = Manager(
            extra_module_dirs=None,
            db_base_dir=None, # os.path.expanduser(os.path.join('~', '.codeintel', 'databases', folders_id)),
            db_catalog_dirs=[],
            db_import_everything_langs=None,
        )
        mgr.upgrade()
        mgr.initialize()

        # Connect the logging file to the handler
        condeintel_log_filename = os.path.join(mgr.db.base_dir, 'codeintel.log')
        condeintel_log_file = open(condeintel_log_filename, 'w', 1)
        codeintel_log.handlers = [logging.StreamHandler(condeintel_log_file)]
        msg = "Starting logging SublimeCodeIntel v%s rev %s (%s) on %s" % (VERSION, get_revision()[:12], os.stat(__file__)[stat.ST_MTIME], datetime.datetime.now().ctime())
        print("%s\n%s" % (msg, "=" * len(msg)), file=condeintel_log_file)

        _ci_mgr_[folders_id] = mgr
    return mgr

def codeintel_scan(editor, path, content, lang, callback=None, pos=None, forms=None):
    global despair
    for thread in threading.enumerate():
        if thread.isAlive() and thread.name == "scanning thread":
            #logger(view, 'info', "Updating indexes... The first time this can take a while. Do not despair!", timeout=20000, delay=despair)
            despair = 0
            return
    #logger(view, 'info', "processing `%s': please wait..." % lang)
    #is_scratch = view.is_scratch()
    is_scratch = True
    #is_dirty = view.is_dirty()
    is_dirty = True
    vid = id(editor)
    #folders = getattr(view.window(), 'folders', lambda: [])() # FIXME: it's like this for backward compatibility (<= 2060)
    folders = []
    folders_id = str(hash(frozenset(folders)))
    #view_settings = view.settings()
    view_settings = {}
    codeintel_config = view_settings.get('codeintel_config', {})
    _codeintel_max_recursive_dir_depth = view_settings.get('codeintel_max_recursive_dir_depth', 10)
    _codeintel_scan_files_in_project = view_settings.get('codeintel_scan_files_in_project', True)
    _codeintel_selected_catalogs = view_settings.get('codeintel_selected_catalogs', [])

    def _codeintel_scan():
        global despair, despaired
        env = None
        mtime = None
        catalogs = []
        now = time.time()

        mgr = codeintel_manager(folders_id)
        #mgr.db.event_reporter = lambda m: logger(view, 'event', m)
        mgr.db.event_reporter = lambda m: print(m)

        try:
            env = _ci_envs_[vid]
            if env._folders != folders:
                raise KeyError
            if now > env._time:
                mtime = max(tryGetMTime(env._config_file), tryGetMTime(env._config_default_file))
                if env._mtime < mtime:
                    raise KeyError
        except KeyError:
            if env is not None:
                config_default_file = env._config_default_file
                project_dir = env._project_dir
                project_base_dir = env._project_base_dir
                config_file = env._config_file
            else:
                config_default_file = os.path.join(CODEINTEL_HOME_DIR, 'config')
                if not (config_default_file and os.path.exists(config_default_file)):
                    config_default_file = None
                project_dir = None
                project_base_dir = None
                for folder_path in folders + [path]:
                    if folder_path:
                        # Try to find a suitable project directory (or best guess):
                        for folder in ['.codeintel', '.git', '.hg', '.svn', 'trunk']:
                            project_dir = find_back(folder_path, folder)
                            if project_dir:
                                if folder == '.codeintel':
                                    if project_dir == CODEINTEL_HOME_DIR or os.path.exists(os.path.join(project_dir, 'databases')):
                                        continue
                                if folder.startswith('.'):
                                    project_base_dir = os.path.abspath(os.path.join(project_dir, '..'))
                                else:
                                    project_base_dir = project_dir
                                break
                        if project_base_dir:
                            break
                if not (project_dir and os.path.exists(project_dir)):
                    project_dir = None
                config_file = project_dir and folder == '.codeintel' and os.path.join(project_dir, 'config')
                if not (config_file and os.path.exists(config_file)):
                    config_file = None
            print(project_dir, project_base_dir)
            valid = True
            if not mgr.is_citadel_lang(lang) and not mgr.is_cpln_lang(lang):
                if lang in ('Console', 'Plain text'):
                    msg = "Invalid language: %s. Available: %s" % (lang, ', '.join(set(mgr.get_citadel_langs() + mgr.get_cpln_langs())))
                    log.debug(msg)
                    codeintel_log.warning(msg)
                valid = False

            codeintel_config_lang = codeintel_config.get(lang, {})
            codeintel_max_recursive_dir_depth = codeintel_config_lang.get('codeintel_max_recursive_dir_depth', _codeintel_max_recursive_dir_depth)
            codeintel_scan_files_in_project = codeintel_config_lang.get('codeintel_scan_files_in_project', _codeintel_scan_files_in_project)
            codeintel_selected_catalogs = codeintel_config_lang.get('codeintel_selected_catalogs', _codeintel_selected_catalogs)

            avail_catalogs = mgr.db.get_catalogs_zone().avail_catalogs()

            # Load configuration files:
            all_catalogs = []
            for catalog in avail_catalogs:
                all_catalogs.append("%s (for %s: %s)" % (catalog['name'], catalog['lang'], catalog['description']))
                if catalog['lang'] == lang:
                    if catalog['name'] in codeintel_selected_catalogs:
                        catalogs.append(catalog['name'])
            msg = "Avaliable catalogs: %s" % ', '.join(all_catalogs) or None
            log.debug(msg)
            codeintel_log.debug(msg)

            config = {
                'codeintel_max_recursive_dir_depth': codeintel_max_recursive_dir_depth,
                'codeintel_scan_files_in_project': codeintel_scan_files_in_project,
                'codeintel_selected_catalogs': catalogs,
            }
            config.update(codeintel_config_lang)

            _config = {}
            try:
                tryReadDict(config_default_file, _config)
            except Exception as e:
                msg = "Malformed configuration file '%s': %s" % (config_default_file, e)
                log.error(msg)
                codeintel_log.error(msg)
            try:
                tryReadDict(config_file, _config)
            except Exception as e:
                msg = "Malformed configuration file '%s': %s" % (config_default_file, e)
                log.error(msg)
                codeintel_log.error(msg)
            config.update(_config.get(lang, {}))

            for conf in ['pythonExtraPaths', 'rubyExtraPaths', 'perlExtraPaths', 'javascriptExtraPaths', 'phpExtraPaths']:
                v = [p.strip() for p in config.get(conf, []) + folders if p.strip()]
                config[conf] = os.pathsep.join(set(p if p.startswith('/') else os.path.expanduser(p) if p.startswith('~') else os.path.abspath(os.path.join(project_base_dir, p)) if project_base_dir else p for p in v if p.strip()))
            for conf, p in config.items():
                if isinstance(p, basestring) and p.startswith('~'):
                    config[conf] = os.path.expanduser(p)

            # Setup environment variables
            env = config.get('env', {})
            _environ = dict(os.environ)
            for k, v in env.items():
                _old = None
                while '$' in v and v != _old:
                    _old = v
                    v = os.path.expandvars(v)
                _environ[k] = v
            config['env'] = _environ

            env = SimplePrefsEnvironment(**config)
            env._valid = valid
            env._mtime = mtime or max(tryGetMTime(config_file), tryGetMTime(config_default_file))
            env._folders = folders
            env._config_default_file = config_default_file
            env._project_dir = project_dir
            env._project_base_dir = project_base_dir
            env._config_file = config_file
            env.__class__.get_proj_base_dir = lambda self: project_base_dir
            _ci_envs_[vid] = env
        env._time = now + 5 # don't check again in less than five seconds

        msgs = []
        if env._valid:
            if forms:
                #set_status(view, 'tip', "")
                #set_status(view, 'event', "")
                msg = "CodeIntel(%s) for %s@%s [%s]" % (', '.join(forms), path, pos, lang)
                msgs.append(('info', "\n%s\n%s" % (msg, "-" * len(msg))))

            if catalogs:
                msg = "New env with catalogs for '%s': %s" % (lang, ', '.join(catalogs) or None)
                log.debug(msg)
                codeintel_log.warning(msg)
                msgs.append(('info', msg))

            buf = mgr.buf_from_content(content, lang, env, path or "<Unsaved>", 'utf-8')

            if mgr.is_citadel_lang(lang):
                now = datetime.datetime.now()
                if not _ci_next_scan_.get(vid) or now > _ci_next_scan_[vid]:
                    _ci_next_scan_[vid] = now + datetime.timedelta(seconds=10)
                    despair = 0
                    despaired = False
                    msg = "Updating indexes for '%s'... The first time this can take a while." % lang
                    print(msg, file=condeintel_log_file)
                    #logger(view, 'info', msg, timeout=20000, delay=1000)
                    if not path or is_scratch:
                        buf.scan() # FIXME: Always scanning unsaved files (since many tabs can have unsaved files, or find other path as ID)
                    else:
                        if is_dirty:
                            mtime = 1
                        else:
                            mtime = os.stat(path)[stat.ST_MTIME]
                        buf.scan(mtime=mtime, skip_scan_time_check=is_dirty)
        else:
            buf = None
        if callback:
            msg = "Doing CodeIntel for '%s' (hold on)..." % lang
            print(msg, file=condeintel_log_file)
            #logger(view, 'info', msg, timeout=20000, delay=1000)
            callback(buf, msgs)
        else:
            #logger(view, 'info', "")
            pass
    threading.Thread(target=_codeintel_scan, name="scanning thread").start()