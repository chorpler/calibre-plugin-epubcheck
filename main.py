#!/usr/bin/env python
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
__copyright__ = '2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 Doitsu'

# standard libraries
import zipfile
import re, os, locale, sys, tempfile, socket, urllib, json, shutil
from os.path import expanduser, basename
from datetime import datetime, timedelta

# Qt
from qt.core import (
    QTextEdit, QDockWidget, QApplication, QAction,
    QFileDialog, QMessageBox, QDialog, QListWidget, QVBoxLayout,
    QListWidgetItem, QDialogButtonBox, Qt, QEventLoop, QBrush, QColor
)

# Calibre libraries
from calibre.gui2.tweak_book.plugin import Tool
from calibre.gui2.tweak_book.ui import Main
from calibre.utils.config import config_dir, JSONConfig
from calibre.constants import iswindows, islinux, isosx

# make sure the plugin will work with the Python 3 version of Calibre
if sys.version_info[0] == 2:
    from urllib import urlopen, urlretrieve
else:
    from urllib.request import urlopen, urlretrieve

# get epubcheck.jar version number
def get_epc_version(epc_path):
    version = ''

    # make sure that epubcheck.jar actually exists
    if os.path.exists(epc_path):

        # read .jar file as zip file
        archive = zipfile.ZipFile(epc_path)

        # make sure that pom.xml exists
        if 'META-INF/maven/org.w3c/epubcheck/pom.xml' in archive.namelist():
            pom_data = archive.read('META-INF/maven/org.w3c/epubcheck/pom.xml')
            archive.close()

            # parse pom.xml as ElementTree
            from xml.etree import ElementTree as ET
            root = ET.fromstring(pom_data)
            tag = root.find("*//{http://maven.apache.org/POM/4.0.0}tag")
            # look for <tag>
            if tag is not None:
                version = tag.text
            else:
                # look for <version>
                project_version = root.find("{http://maven.apache.org/POM/4.0.0}version")
                if project_version is not None:
                    version = 'v' + project_version.text
        else:
            print('pom.xml not found!')
    else:
        print('epubcheck.jar not found!')

    return version

# get latest EPUBCheck version
def latest_epc_version(github_url):
    latest_version = ''
    browser_download_url = ''
    if is_connected():
        # check for github updates
        response = urlopen(github_url).read().decode('utf-8')
        parsed_json = json.loads(response)
        latest_version = parsed_json[0]['tag_name']
        browser_download_url = parsed_json[0]['assets'][0]['browser_download_url']
    return latest_version, browser_download_url

# code provided by DiapDealer
def is_connected():
    try:
        sock = socket.create_connection(('8.8.8.8', 53), 1)
        sock.close()
        return True
    except:
        pass

# code provided by DiapDealer
def string_to_date(datestring):
    return datetime.strptime(datestring, "%Y-%m-%d %H:%M:%S.%f")

# DiapDealer's temp folder code
from contextlib import contextmanager

@contextmanager
def make_temp_directory():
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

# jar wrapper for epubcheck
def jarWrapper(*args):
    import subprocess
    startupinfo = None

    # stop the windows console popping up every time the prog is run
    if iswindows:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    process = subprocess.Popen(list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
    ret = process.communicate()
    returncode = process.returncode
    return ret, returncode

# get JVM bitness (https://stackoverflow.com/questions/2062020)
def get_arch(java_path):
    arch = '64'
    args = [java_path, '-XshowSettings:properties', '-version']
    ret, retcode = jarWrapper(*args)
    arch_pattern = re.compile(r'sun.arch.data.model = (\d+)')
    arch_info = arch_pattern.search(ret[1].decode('utf-8'))
    if arch_info:
        if len(arch_info.groups()) == 1:
            arch = arch_info.group(1)
            print('Java bitness detected:', arch)
    else:
        print('Java bitness not detected!' )
    return arch

class DemoTool(Tool):

    #: Set this to a unique name it will be used as a key
    name = 'epub-check'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction(get_icons('images/icon.png'), 'Run EpubCheck', self.gui)  # noqa
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'epub-check-tool', default_keys=('Ctrl+Shift+Alt+G',))
        ac.triggered.connect(self.ask_user)
        return ac

    def ask_user(self):

        #-----------------------------------
        # define EPUBCheck paths and URL
        #-----------------------------------
        epubcheck_dir = os.path.join(config_dir, 'plugins', 'EPUBCheck')
        if not os.path.isdir(epubcheck_dir):
            os.makedirs(epubcheck_dir)
        epc_path = os.path.join(epubcheck_dir, 'epubcheck.jar')
        epc_lib_dir = os.path.join(epubcheck_dir, 'lib')
        github_url = 'https://api.github.com/repos/w3c/epubcheck/releases'

        #----------------------------------------
        # get user preference file
        #----------------------------------------
        prefs = JSONConfig('plugins/EpubCheck')

        #----------------------------------------
        # set default preferences
        #----------------------------------------
        if prefs == {}:
            prefs.set('close_cb', False)
            prefs.set('clipboard_copy', False)
            prefs.set('usage', False)
            prefs.set('github', True)
            prefs.set('last_time_checked', str(datetime.now() - timedelta(days=7)))
            prefs.set('check_interval', 7)
            prefs.set('java_path', 'java')
            prefs.set('is32bit', get_arch('java') == '32')
            prefs.commit()

        #---------------------------
        # get preferences
        #---------------------------
        locale = prefs.get('locale', None)
        close_cb = prefs.get('close_cb', False)
        clipboard_copy = prefs.get('clipboard_copy', False)
        usage = prefs.get('usage', False)
        github = prefs.get('github', True)
        last_time_checked = prefs.get('last_time_checked', str(datetime.now() - timedelta(days=7)))
        check_interval = prefs.get('check_interval', 7)
        java_path = prefs.get('java_path', 'java').replace('\\\\', '/').replace('\\', '/')
        is32bit = prefs.get('is32bit', get_arch(java_path) == '32')

        #-----------------------------------------------------
        # create a savepoint
        #----------------------------------------------------
        self.boss.add_savepoint('Before: EPUBCheck')

        #--------------------------------------------------------------------
        # create a dictionary that maps names to relative hrefs
        #--------------------------------------------------------------------
        epub_mime_map = self.current_container.mime_map
        epub_name_to_href = {}
        for href in epub_mime_map:
            epub_name_to_href[os.path.basename(href)] = href

        #--------------------------------------------------------------------
        # create temp directory and unpack epubcheck files
        #--------------------------------------------------------------------
        with make_temp_directory() as td:
            # write current container to temporary epub
            epub_path = os.path.join(td, 'temp.epub')
            self.boss.commit_all_editors_to_container()
            self.current_container.commit(epub_path)

            # check if the EPUBCheck Java files were downloaded
            if not os.path.isdir(epubcheck_dir) or not os.path.isfile(epc_path) or not os.path.isdir(epc_lib_dir):
                epc_missing = True
            else:
                epc_missing = False

            #----------------------------
            # check for EPUBCheck updates
            #----------------------------
            if github or epc_missing:

                # make sure we have an Internet connection
                if is_connected():

                    # compare current date against last update check date
                    time_delta = (datetime.now() - string_to_date(last_time_checked)).days
                    if (time_delta >= check_interval) or epc_missing:

                        # display searching for updates... message
                        if epc_missing:
                            self.gui.show_status_message("No EPUBCheck files found.", 7)
                        else:
                            self.gui.show_status_message("Running update check...", 7)
                        QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

                        # update time stamp in EpubCheck.json
                        prefs.set('last_time_checked', str(datetime.now()))
                        prefs.commit()

                        # get current epubcheck version from epubcheck.jar
                        epc_version = get_epc_version(epc_path)
                        print('epc_version', epc_version)

                        # get latest version and browser download url
                        latest_version, browser_download_url = latest_epc_version(github_url)
                        print('latest_version:', latest_version, 'browser_download_url:', browser_download_url)

                        if 'alpha' in browser_download_url or 'beta' in browser_download_url and not epc_missing: browser_download_url = '' # exclude alpha/beta versions

                        # only run the update if a new version is available
                        if latest_version != epc_version and latest_version !='' and browser_download_url != '':
                            answer = QMessageBox.question(self.gui, "EPUBCheck update available", "EPUBCheck {} is available.\nDo you want to download the latest version?".format(latest_version))

                            # update EPUBCheck
                            if answer == QMessageBox.StandardButton.Yes:

                                # create a temp folder
                                with make_temp_directory() as td:
                                    base_name = os.path.basename(browser_download_url)
                                    root_path = os.path.splitext(base_name)[0]
                                    zip_file_name = os.path.join(td, base_name)

                                    # display status message
                                    self.gui.show_status_message("Downloading {}...".format(browser_download_url), 3)
                                    QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

                                    # download the zip file
                                    urlretrieve(browser_download_url, zip_file_name)

                                    # make sure the file was actually downloaded
                                    if os.path.exists(zip_file_name):

                                        # display status message
                                        self.gui.show_status_message("{} downloaded.".format(browser_download_url), 3)
                                        QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

                                        # read zip file
                                        # https://stackoverflow.com/questions/19618268/extract-and-rename-zip-file-folder
                                        archive = zipfile.ZipFile(zip_file_name)
                                        files = archive.namelist()
                                        files_to_extract = [m for m in files if (m.startswith(root_path + '/lib') or m == root_path + '/epubcheck.jar')]
                                        archive.extractall(td, files_to_extract)
                                        archive.close()

                                        # temp paths to epubcheck.jar and the /lib folder
                                        temp_epc_path = os.path.join(td, root_path + '/epubcheck.jar')
                                        temp_epc_lib_dir = os.path.join(td, root_path + '/lib')

                                        # make sure the files were actually extracted
                                        if os.path.isdir(temp_epc_lib_dir) and os.path.isfile(temp_epc_path):

                                            epc_missing = False

                                            # delete /lib folder
                                            if os.path.isdir(epc_lib_dir):
                                                shutil.rmtree(epc_lib_dir)

                                            # delete epubcheck.jar
                                            if os.path.exists(epc_path):
                                                os.remove(epc_path)

                                            # move new files to the plugin folder
                                            shutil.move(temp_epc_lib_dir, epubcheck_dir)
                                            shutil.move(temp_epc_path, epubcheck_dir)

                                            # ensure you have execute rights for unix based platforms
                                            if isosx or islinux:
                                                os.chmod(epc_path, 0o744)

                                            # display update successful message
                                            self.gui.show_status_message("EPUBCheck updated to EPUBCheck {}".format(latest_version), 5)
                                            QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

                                        else:

                                            # display unzip error message
                                            self.gui.show_status_message("EPUBCheck update failed. The EPUBCheck .zip file couldn\'t be unpacked.", 10)
                                            QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
                                    else:

                                        # display download error message
                                        self.gui.show_status_message("EPUBCheck update failed. The latest EPUBCheck .zip file couldn\'t be downloaded", 10)
                                        QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

                        else:

                            # display miscellanenous internal error messages
                            if latest_version != '':
                                self.gui.show_status_message("No new EPUBCheck version found.", 5)
                                QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
                            elif epc_version == '':
                                self.gui.show_status_message("Current EPUBCheck version not found.", 5)
                                QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
                            else:
                                self.gui.show_status_message("Internal error: update check failed.", 5)
                                QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
                else:

                    # display no Internet error message
                    self.gui.show_status_message("Update check skipped: no Internet.", 5)
                    QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

            # double-check that the Java files were downloaded
            if epc_missing:
                QMessageBox.critical(self.gui, "EPUBCheck Java files missing!", 'Please re-run the plugin while connected to the Internet.')
                return

            #-------------------------------------
            # assemble epubcheck parameters
            #-------------------------------------

            # display busy cursor
            QApplication.setOverrideCursor(Qt.WaitCursor)

            # define epubcheck command line parameters
            if is32bit:
                args = [java_path, '-Dfile.encoding=UTF8', '-Xss1024k', '-jar', epc_path]
            else:
                args = [java_path, '-Dfile.encoding=UTF8', '-jar', epc_path]

            # display messages in a different language
            if locale is not None:
                args.extend(['--locale', locale])

            # display usage messages
            if usage:
                args.append('--usage')

            args.append(epub_path)

            # run epubcheck
            self.gui.show_status_message("Running EPUBCheck...", 3)
            QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
            result, returncode = jarWrapper(*args)
            stdout = result[0].decode('utf-8')
            stderr = result[1].decode('utf-8')

            # check for Java errors
            if returncode == 1 and 'java.lang.' in stderr:
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(self.gui, "Fatal Java error", stdout + '\n' + stderr)
                return

            # add usage messages, which are written to stdout!
            if usage:
                stderr += stdout

            # get windows temp drive letter
            if iswindows:
                drive_letter = tempfile.gettempdir()[0] + ':'

        #--------------------------------------------
        # process output
        #--------------------------------------------
        if returncode != 0 or re.search('(INFO|USAGE|WARNING)\(.*?\)', stderr) is not None:
            # copy to clipboard
            if clipboard_copy:
                QApplication.clipboard().setText(stderr)

            # errors found; parse messages
            error_messages = []

            # get each line of the messages
            epc_errors = stderr.splitlines()

            # process messages
            for line in epc_errors:

                #---------------------------------------------------------------
                # process only errors, warnings and info messages
                #----------------------------------------------------------------
                if line.startswith(('ERROR', 'WARNING', 'FATAL', 'INFO', 'USAGE')):

                    # replace colon after Windows drive letter with a placeholder to simplify colon based parsing
                    if iswindows:
                        line = re.sub(drive_letter, 'C^',  line, flags=re.I)

                    # split message by colons
                    err_list = line.split(':')

                    # check for colons in error message
                    if len(err_list) > 3:
                        # merge list items
                        err_list[2:len(err_list)] = [':'.join(err_list[2:len(err_list)])]

                    # get error code e.g. FATAL(RSC-016) or ERROR(RSC-005)
                    err_code = err_list[0]

                    # get message
                    msg = err_list[2].strip()

                    # get file name, line/column numbers
                    linenumber = None
                    colnumber = None
                    line_pos = re.search('\((-*\d+),(-*\d+)*\)', err_list[1])

                    if line_pos:
                        # get file name and line/column numbers
                        filename = re.sub('\(-*\d+,-*\d+\)', '',  err_list[1])

                        if int(line_pos.group(1)) != -1:
                            linenumber = line_pos.group(1)
                        if int(line_pos.group(2)) != -1:
                            colnumber = line_pos.group(2)
                    else:
                        # get file name only
                        filename = err_list[1]

                    # remove folder information from file name
                    if iswindows:
                        filename = os.path.basename(re.sub('C^', drive_letter, filename))
                        msg = msg.replace('C^', drive_letter.lower())
                    # elif isosx:
                        # suggested by wrCisco
                        # filename = ".".join((filename.split('.')[-2], filename.split('.')[-1]))
                    else:
                        # Linux
                        filename = os.path.basename(filename)

                    # get relative file path
                    if filename in epub_name_to_href:
                        filepath = epub_name_to_href[filename]
                    else:
                        filepath = 'NA'

                    # assemble error message
                    message = os.path.basename(filepath)
                    if linenumber:
                        message += ' Line: ' + linenumber
                    else:
                        message += ' '
                    if colnumber:
                        message += ' Col: ' + colnumber + ' '
                    message += err_code + ': ' +  msg

                    #--------------------------------------------------------------------------------------------------------------
                    # save error information in list (filepath, line number, err_code, filename, error message)
                    #--------------------------------------------------------------------------------------------------------------
                    error_messages.append((filepath, linenumber, colnumber, err_code, message))

            if error_messages != []:
                #---------------------------------------------------------------
                # auxiliary routine for loading the file into the editor
                #---------------------------------------------------------------
                def GotoLine(item):
                    # get list item number
                    current_row = listWidget.currentRow()

                    # get error information
                    filepath, line, col, err_code, message = error_messages[current_row]

                    # go to the file
                    if not os.path.basename(filepath).endswith('NA'):
                        if line:
                            self.boss.edit_file(filepath)
                            editor = self.boss.gui.central.current_editor
                            if editor is not None and editor.has_line_numbers:
                                if col is not None:
                                    editor.editor.go_to_line(int(line), col=int(col) - 1)
                                else:
                                    editor.current_line = int(line)
                        else:
                            QMessageBox.information(self.gui, "Unknown line number", "EPUBCheck didn't report a line number for this error.")
                    else:
                        QMessageBox.information(self.gui, "Unknown file name", "EPUBCheck didn't report the name of the file that caused this error.")

                #------------------------------------------------------------------------------------------------
                # remove existing EPUBCheck/FlightCrew docks and close Check Ebook dock
                #------------------------------------------------------------------------------------------------
                for widget in self.gui.children():
                    if isinstance(widget, QDockWidget) and widget.objectName() == 'epubcheck-dock':
                        #self.gui.removeDockWidget(widget)
                        #widget.close()
                        widget.setParent(None)
                    if isinstance(widget, QDockWidget) and widget.objectName() == 'check-book-dock' and close_cb == True:
                        widget.close()

                #----------------------------------
                # define dock widget layout
                #----------------------------------
                try:
                    is_dark_theme = QApplication.instance().is_dark_theme
                except:
                    is_dark_theme = False
                listWidget = QListWidget()
                l = QVBoxLayout()
                l.addWidget(listWidget)
                dock_widget = QDockWidget(self.gui)
                dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
                dock_widget.setObjectName('epubcheck-dock')
                dock_widget.setWindowTitle('EPUBCheck')
                dock_widget.setWidget(listWidget)

                #--------------------------------------------
                # add error messages to list widget
                #--------------------------------------------
                for error_msg in error_messages:
                    filename, line, col, err_code, message = error_msg
                    item = QListWidgetItem(message)

                    # select background color based on severity
                    if err_code.startswith(('ERROR', 'FATAL')):
                        bg_color = QBrush(QColor(255, 230, 230))
                    elif err_code.startswith('WARNING'):
                        bg_color = QBrush(QColor(255, 255, 230))
                    else:
                        bg_color = QBrush(QColor(224, 255, 255))
                    item.setBackground(QColor(bg_color))
                    if is_dark_theme:
                        item.setForeground(QBrush(QColor("black")))
                    listWidget.addItem(item)
                    print(filename, line, col, err_code, message)
                listWidget.itemClicked.connect(GotoLine)

                # add dock widget to the dock
                self.gui.addDockWidget(Qt.TopDockWidgetArea, dock_widget)

            # hide busy cursor
            QApplication.restoreOverrideCursor()
        else:
            #------------------------------------------------------------------------------------------------
            # remove existing EpubCheck/FlightCrew docks and close Check Ebook dock
            #------------------------------------------------------------------------------------------------
            for widget in self.gui.children():
                if isinstance(widget, QDockWidget) and widget.objectName() == 'epubcheck-dock':
                    #self.gui.removeDockWidget(widget)
                    #widget.close()
                    widget.setParent(None)
                if isinstance(widget, QDockWidget) and widget.objectName() == 'check-book-dock' and close_cb == True:
                    widget.close()

            #----------------------------------
            # define dock widget layout
            #----------------------------------
            textbox = QTextEdit()
            l = QVBoxLayout()
            l.addWidget(textbox)
            dock_widget = QDockWidget(self.gui)
            dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
            dock_widget.setObjectName('epubcheck-dock')
            dock_widget.setWindowTitle('EPUBCheck')
            # add version info to stdout
            epubcheck_dir = os.path.join(config_dir, 'plugins', 'EPUBCheck')
            epc_path = os.path.join(epubcheck_dir, 'epubcheck.jar')
            version = get_epc_version(epc_path)
            if os.path.isfile(epc_path) and version != '':
                version = 'EPUBCheck {}'.format(version)
                stdout = version + '\n' + stdout
            textbox.setText(stdout)
            dock_widget.setWidget(textbox)
            self.gui.addDockWidget(Qt.TopDockWidgetArea, dock_widget)

            # hide busy cursor
            QApplication.restoreOverrideCursor()
