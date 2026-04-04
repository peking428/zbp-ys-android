# -*- coding: utf-8 -*-
"""
ZBP Compress/Decompress Tool - Android Version
Version 5.0 - Robust error handling and font fallback
"""

import os
import sys
import traceback

from kivy.config import Config

Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('kivy', 'keyboard_mode', 'systemanddock')

import zipfile
import threading
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.logger import Logger
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.window import Window

HAS_PYZIPPER = False
HAS_ANDROID = False
HAS_PYJNIUS = False

try:
    import pyzipper
    HAS_PYZIPPER = True
    Logger.info('ZBP: pyzipper loaded successfully')
except ImportError as e:
    Logger.warning(f'ZBP: pyzipper not available: {e}')

try:
    from jnius import autoclass
    HAS_PYJNIUS = True
    Logger.info('ZBP: pyjnius loaded successfully')
except ImportError as e:
    Logger.warning(f'ZBP: pyjnius not available: {e}')

try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    HAS_ANDROID = True
    Logger.info('ZBP: android module loaded successfully')
except ImportError as e:
    Logger.warning(f'ZBP: android module not available: {e}')

if HAS_PYJNIUS:
    try:
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Environment = autoclass('android.os.Environment')
        Logger.info('ZBP: Android classes loaded successfully')
    except Exception as e:
        Logger.error(f'ZBP: Failed to load Android classes: {e}')
        HAS_PYJNIUS = False

APP_FONT = None

def find_system_font():
    system_font_paths = [
        '/system/fonts/NotoSansSC-Regular.otf',
        '/system/fonts/NotoSansCJK-Regular.otf',
        '/system/fonts/NotoSansCJKsc-Regular.otf',
        '/system/fonts/DroidSansFallback.ttf',
        '/system/fonts/DroidSans.ttf',
        '/system/fonts/Roboto-Regular.ttf',
        '/system/fonts/NotoSans-Regular.ttf',
        '/system/fonts/HarmonyOS-Sans-Regular.ttf',
        '/system/fonts/HmosFont-Regular.ttf',
        '/system/fonts/SourceHanSansSC-Regular.otf',
    ]
    
    for font_path in system_font_paths:
        try:
            if os.path.exists(font_path):
                Logger.info(f'ZBP: Found system font: {font_path}')
                return font_path
        except Exception as e:
            Logger.warning(f'ZBP: Error checking font {font_path}: {e}')
    
    return None

def setup_font():
    global APP_FONT
    Logger.info('ZBP: Setting up font system...')
    
    try:
        font_path = None
        
        if hasattr(sys, 'android') or HAS_ANDROID:
            Logger.info('ZBP: Running on Android, checking system fonts...')
            font_path = find_system_font()
        
        if font_path:
            try:
                Logger.info(f'ZBP: Registering font: {font_path}')
                LabelBase.register(name='AppFont', fn_regular=font_path)
                Config.set('kivy', 'default_font', 'AppFont')
                APP_FONT = 'AppFont'
                Logger.info(f'ZBP: Font registered successfully: {font_path}')
                return 'AppFont'
            except Exception as e:
                Logger.error(f'ZBP: Failed to register font: {e}')
                Logger.error(traceback.format_exc())
        
        Logger.warning('ZBP: Using default font')
        APP_FONT = DEFAULT_FONT
        return DEFAULT_FONT
        
    except Exception as e:
        Logger.error(f'ZBP: Font setup error: {e}')
        Logger.error(traceback.format_exc())
        APP_FONT = DEFAULT_FONT
        return DEFAULT_FONT

def get_font():
    global APP_FONT
    if APP_FONT:
        return APP_FONT
    return 'Roboto'

class ZbpYsApp(App):
    def build(self):
        try:
            Logger.info('ZBP: Starting application build v5.0')
            self.title = "ZBP Tool"
            
            Window.clearcolor = (0.95, 0.95, 0.95, 1)
            
            setup_font()
            
            self.base_path = self.get_storage_path()
            Logger.info(f'ZBP: Storage path: {self.base_path}')
            
            if HAS_ANDROID:
                Logger.info('ZBP: Requesting Android permissions')
                self.request_all_permissions()
            
            self.selected_files = []
            self.current_mode = "compress"
            self.is_processing = False
            self.zip_path = None
            
            font_name = get_font()
            Logger.info(f'ZBP: Using font: {font_name}')
            
            self.root_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
            
            title_label = Label(
                text='[b]ZBP Compress Tool[/b]',
                font_size='22sp',
                size_hint_y=None,
                height=dp(50),
                markup=True,
                color=(0.1, 0.1, 0.1, 1),
                font_name=font_name
            )
            self.root_layout.add_widget(title_label)
            
            subtitle_label = Label(
                text='ZIP Compress and Decompress Tool',
                font_size='13sp',
                size_hint_y=None,
                height=dp(30),
                color=(0.3, 0.3, 0.3, 1),
                font_name=font_name
            )
            self.root_layout.add_widget(subtitle_label)
            
            mode_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
            
            self.compress_btn = ToggleButton(
                text='Compress',
                group='mode',
                state='down',
                font_size='15sp',
                background_color=(0.2, 0.6, 0.9, 1),
                font_name=font_name
            )
            self.compress_btn.bind(on_press=lambda x: self.switch_mode('compress'))
            mode_layout.add_widget(self.compress_btn)
            
            self.decompress_btn = ToggleButton(
                text='Decompress',
                group='mode',
                state='normal',
                font_size='15sp',
                background_color=(0.9, 0.5, 0.2, 1),
                font_name=font_name
            )
            self.decompress_btn.bind(on_press=lambda x: self.switch_mode('decompress'))
            mode_layout.add_widget(self.decompress_btn)
            
            self.root_layout.add_widget(mode_layout)
            
            self.compress_layout = self.create_compress_layout(font_name)
            self.root_layout.add_widget(self.compress_layout)
            
            self.decompress_layout = self.create_decompress_layout(font_name)
            self.decompress_layout.opacity = 0
            self.decompress_layout.disabled = True
            self.root_layout.add_widget(self.decompress_layout)
            
            self.progress_bar = ProgressBar(
                size_hint_y=None,
                height=dp(25),
                value=0
            )
            self.root_layout.add_widget(self.progress_bar)
            
            self.status_label = Label(
                text='Ready - Select files to compress',
                font_size='12sp',
                size_hint_y=None,
                height=dp(35),
                halign='center',
                color=(0.2, 0.2, 0.2, 1),
                font_name=font_name
            )
            self.status_label.bind(texture_size=self.status_label.setter('size'))
            self.root_layout.add_widget(self.status_label)
            
            action_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            
            self.action_btn = Button(
                text='START COMPRESS',
                font_size='16sp',
                background_color=(0.1, 0.7, 0.3, 1),
                font_name=font_name,
                bold=True
            )
            self.action_btn.bind(on_press=self.start_action)
            action_layout.add_widget(self.action_btn)
            
            self.root_layout.add_widget(action_layout)
            
            Logger.info('ZBP: Application build completed successfully')
            return self.root_layout
            
        except Exception as e:
            Logger.error(f'ZBP: Error in build: {e}')
            Logger.error(traceback.format_exc())
            error_layout = BoxLayout(orientation='vertical', padding=dp(20))
            error_layout.add_widget(Label(text=f'Error:\n{str(e)}', font_size='16sp'))
            return error_layout
    
    def get_storage_path(self):
        if HAS_ANDROID:
            try:
                path = primary_external_storage_path()
                if path and os.path.exists(path):
                    return path
            except:
                pass
            
            if HAS_PYJNIUS:
                try:
                    env_path = Environment.getExternalStorageDirectory().getAbsolutePath()
                    if env_path and os.path.exists(env_path):
                        return env_path
                except:
                    pass
        
        return os.path.expanduser("~")
    
    def request_all_permissions(self):
        if not HAS_ANDROID:
            return
        
        try:
            permissions = [
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ]
            
            try:
                permissions.append(Permission.MANAGE_EXTERNAL_STORAGE)
            except:
                pass
            
            request_permissions(permissions)
            Logger.info('ZBP: Permissions requested')
        except Exception as e:
            Logger.error(f'ZBP: Error requesting permissions: {e}')
    
    def create_compress_layout(self, font_name):
        layout = BoxLayout(orientation='vertical', spacing=dp(5))
        
        file_btn_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        
        select_file_btn = Button(
            text='Select Files',
            font_size='14sp',
            size_hint_x=0.5,
            background_color=(0.3, 0.5, 0.8, 1),
            font_name=font_name
        )
        select_file_btn.bind(on_press=self.select_files)
        file_btn_layout.add_widget(select_file_btn)
        
        select_folder_btn = Button(
            text='Select Folder',
            font_size='14sp',
            size_hint_x=0.5,
            background_color=(0.3, 0.5, 0.8, 1),
            font_name=font_name
        )
        select_folder_btn.bind(on_press=self.select_folder)
        file_btn_layout.add_widget(select_folder_btn)
        
        layout.add_widget(file_btn_layout)
        
        self.file_list_label = Label(
            text='Selected: 0 files',
            font_size='12sp',
            size_hint_y=None,
            height=dp(70),
            halign='left',
            valign='top',
            text_size=(None, None),
            color=(0.2, 0.2, 0.2, 1),
            font_name=font_name
        )
        self.file_list_label.bind(texture_size=self.file_list_label.setter('size'))
        layout.add_widget(self.file_list_label)
        
        clear_btn = Button(
            text='Clear Selection',
            font_size='13sp',
            size_hint_y=None,
            height=dp(35),
            background_color=(0.8, 0.3, 0.3, 1),
            font_name=font_name
        )
        clear_btn.bind(on_press=self.clear_list)
        layout.add_widget(clear_btn)
        
        name_layout = BoxLayout(size_hint_y=None, height=dp(45))
        name_layout.add_widget(Label(
            text='ZIP Name:', 
            font_size='14sp', 
            size_hint_x=0.35, 
            font_name=font_name,
            color=(0.2, 0.2, 0.2, 1)
        ))
        self.zip_name_input = TextInput(
            text=f'compressed_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            font_size='14sp',
            size_hint_x=0.65
        )
        name_layout.add_widget(self.zip_name_input)
        layout.add_widget(name_layout)
        
        pwd_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(130), spacing=dp(5))
        
        pwd_header = BoxLayout(size_hint_y=None, height=dp(30))
        self.use_password_cb = CheckBox(size_hint_x=0.1, active=False)
        self.use_password_cb.bind(on_active=self.toggle_password)
        pwd_header.add_widget(self.use_password_cb)
        pwd_header.add_widget(Label(
            text='Enable Password Protection', 
            font_size='13sp', 
            size_hint_x=0.9, 
            font_name=font_name,
            color=(0.2, 0.2, 0.2, 1)
        ))
        pwd_section.add_widget(pwd_header)
        
        pwd_layout = BoxLayout(size_hint_y=None, height=dp(40))
        pwd_layout.add_widget(Label(
            text='Password:', 
            font_size='13sp', 
            size_hint_x=0.25, 
            font_name=font_name,
            color=(0.2, 0.2, 0.2, 1)
        ))
        self.compress_pwd_input = TextInput(
            password=True,
            font_size='13sp',
            size_hint_x=0.35,
            disabled=True
        )
        pwd_layout.add_widget(self.compress_pwd_input)
        pwd_layout.add_widget(Label(
            text='Confirm:', 
            font_size='13sp', 
            size_hint_x=0.15, 
            font_name=font_name,
            color=(0.2, 0.2, 0.2, 1)
        ))
        self.compress_pwd_confirm = TextInput(
            password=True,
            font_size='13sp',
            size_hint_x=0.25,
            disabled=True
        )
        pwd_layout.add_widget(self.compress_pwd_confirm)
        pwd_section.add_widget(pwd_layout)
        
        show_pwd_layout = BoxLayout(size_hint_y=None, height=dp(25))
        self.show_pwd_cb = CheckBox(size_hint_x=0.1, active=False, disabled=True)
        self.show_pwd_cb.bind(on_active=self.toggle_show_password)
        show_pwd_layout.add_widget(self.show_pwd_cb)
        show_pwd_layout.add_widget(Label(
            text='Show Password', 
            font_size='11sp', 
            size_hint_x=0.9, 
            font_name=font_name,
            color=(0.3, 0.3, 0.3, 1)
        ))
        pwd_section.add_widget(show_pwd_layout)
        
        layout.add_widget(pwd_section)
        
        return layout
    
    def create_decompress_layout(self, font_name):
        layout = BoxLayout(orientation='vertical', spacing=dp(5))
        
        zip_btn_layout = BoxLayout(size_hint_y=None, height=dp(45))
        select_zip_btn = Button(
            text='Select ZIP File',
            font_size='14sp',
            size_hint_x=1,
            background_color=(0.9, 0.5, 0.2, 1),
            font_name=font_name
        )
        select_zip_btn.bind(on_press=self.select_zip_file)
        zip_btn_layout.add_widget(select_zip_btn)
        layout.add_widget(zip_btn_layout)
        
        self.zip_path_label = Label(
            text='No file selected',
            font_size='12sp',
            size_hint_y=None,
            height=dp(35),
            halign='center',
            color=(0.3, 0.3, 0.3, 1),
            font_name=font_name
        )
        layout.add_widget(self.zip_path_label)
        
        self.zip_info_label = Label(
            text='ZIP Info: --',
            font_size='11sp',
            size_hint_y=None,
            height=dp(50),
            halign='center',
            color=(0.3, 0.3, 0.3, 1),
            font_name=font_name
        )
        layout.add_widget(self.zip_info_label)
        
        pwd_layout = BoxLayout(size_hint_y=None, height=dp(45))
        pwd_layout.add_widget(Label(
            text='Password:', 
            font_size='14sp', 
            size_hint_x=0.3, 
            font_name=font_name,
            color=(0.2, 0.2, 0.2, 1)
        ))
        self.decompress_pwd_input = TextInput(
            password=True,
            font_size='14sp',
            size_hint_x=0.5,
            hint_text='(Optional)'
        )
        pwd_layout.add_widget(self.decompress_pwd_input)
        
        self.show_decompress_pwd_cb = CheckBox(size_hint_x=0.1, active=False)
        self.show_decompress_pwd_cb.bind(on_active=self.toggle_show_decompress_password)
        pwd_layout.add_widget(self.show_decompress_pwd_cb)
        pwd_layout.add_widget(Label(
            text='Show', 
            font_size='11sp', 
            size_hint_x=0.1, 
            font_name=font_name,
            color=(0.3, 0.3, 0.3, 1)
        ))
        layout.add_widget(pwd_layout)
        
        return layout
    
    def switch_mode(self, mode):
        self.current_mode = mode
        font_name = get_font()
        
        if mode == 'compress':
            self.compress_layout.opacity = 1
            self.compress_layout.disabled = False
            self.decompress_layout.opacity = 0
            self.decompress_layout.disabled = True
            self.action_btn.text = 'START COMPRESS'
            self.action_btn.background_color = (0.1, 0.7, 0.3, 1)
            self.status_label.text = 'Ready - Select files to compress'
        else:
            self.compress_layout.opacity = 0
            self.compress_layout.disabled = True
            self.decompress_layout.opacity = 1
            self.decompress_layout.disabled = False
            self.action_btn.text = 'START DECOMPRESS'
            self.action_btn.background_color = (0.9, 0.5, 0.2, 1)
            self.status_label.text = 'Ready - Select ZIP file to decompress'
        self.progress_bar.value = 0
    
    def toggle_password(self, instance, value):
        self.compress_pwd_input.disabled = not value
        self.compress_pwd_confirm.disabled = not value
        self.show_pwd_cb.disabled = not value
        if not value:
            self.compress_pwd_input.text = ''
            self.compress_pwd_confirm.text = ''
    
    def toggle_show_password(self, instance, value):
        self.compress_pwd_input.password = not value
        self.compress_pwd_confirm.password = not value
    
    def toggle_show_decompress_password(self, instance, value):
        self.decompress_pwd_input.password = not value
    
    def select_files(self, instance):
        try:
            if HAS_PYJNIUS:
                self.open_android_file_picker()
            else:
                try:
                    from plyer import filechooser
                    filechooser.open_file(on_selection=self.on_file_selected, multiple=True)
                except Exception as e:
                    Logger.error(f'ZBP: plyer filechooser error: {e}')
                    self.show_popup('Info', 'Please enter file path manually')
                    self.show_path_input_dialog('file')
        except Exception as e:
            Logger.error(f'ZBP: select_files error: {e}')
            self.show_popup('Error', f'Select file failed: {str(e)}')
    
    def select_folder(self, instance):
        try:
            if HAS_PYJNIUS:
                self.open_android_folder_picker()
            else:
                try:
                    from plyer import filechooser
                    filechooser.choose_dir(on_selection=self.on_folder_selected)
                except Exception as e:
                    Logger.error(f'ZBP: plyer folder chooser error: {e}')
                    self.show_popup('Info', 'Please enter folder path manually')
                    self.show_path_input_dialog('folder')
        except Exception as e:
            Logger.error(f'ZBP: select_folder error: {e}')
            self.show_popup('Error', f'Select folder failed: {str(e)}')
    
    def select_zip_file(self, instance):
        try:
            if HAS_PYJNIUS:
                self.open_android_file_picker(is_zip=True)
            else:
                try:
                    from plyer import filechooser
                    filechooser.open_file(
                        filters=[('ZIP files', '*.zip')],
                        on_selection=self.on_zip_selected
                    )
                except Exception as e:
                    Logger.error(f'ZBP: plyer zip chooser error: {e}')
                    self.show_popup('Info', 'Please enter ZIP file path manually')
                    self.show_path_input_dialog('zip')
        except Exception as e:
            Logger.error(f'ZBP: select_zip_file error: {e}')
            self.show_popup('Error', f'Select ZIP file failed: {str(e)}')
    
    def open_android_file_picker(self, is_zip=False):
        if not HAS_PYJNIUS:
            return
        
        try:
            activity = PythonActivity.mActivity
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType('*/*' if not is_zip else 'application/zip')
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, True)
            
            REQUEST_CODE = 1001 if not is_zip else 1002
            activity.startActivityForResult(intent, REQUEST_CODE)
            
            self.show_popup('Info', 'Please select file in file manager')
        except Exception as e:
            Logger.error(f'ZBP: Android file picker error: {e}')
            self.show_popup('Error', f'Cannot open file picker: {str(e)}')
    
    def open_android_folder_picker(self):
        if not HAS_PYJNIUS:
            return
        
        try:
            activity = PythonActivity.mActivity
            intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
            REQUEST_CODE = 1003
            activity.startActivityForResult(intent, REQUEST_CODE)
            
            self.show_popup('Info', 'Please select folder in file manager')
        except Exception as e:
            Logger.error(f'ZBP: Android folder picker error: {e}')
            self.show_popup('Error', f'Cannot open folder picker: {str(e)}')
    
    def show_path_input_dialog(self, path_type):
        font_name = get_font()
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        hint = 'Enter file full path' if path_type == 'file' else ('Enter ZIP file path' if path_type == 'zip' else 'Enter folder path')
        path_input = TextInput(
            hint_text=hint,
            font_size='14sp',
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(path_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50))
        
        cancel_btn = Button(text='Cancel', font_size='14sp', font_name=font_name)
        btn_layout.add_widget(cancel_btn)
        
        confirm_btn = Button(text='OK', font_size='14sp', font_name=font_name)
        btn_layout.add_widget(confirm_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(title='Input Path', content=content, size_hint=(0.9, 0.4))
        
        cancel_btn.bind(on_press=popup.dismiss)
        
        def on_confirm(instance):
            path = path_input.text.strip()
            if path:
                if path_type == 'zip':
                    self.on_zip_selected([path])
                elif path_type == 'file':
                    self.on_file_selected([path])
                else:
                    self.on_folder_selected([path])
            popup.dismiss()
        
        confirm_btn.bind(on_press=on_confirm)
        popup.open()
    
    def on_file_selected(self, selection):
        if selection:
            for f in selection:
                if isinstance(f, str) and f not in self.selected_files:
                    self.selected_files.append(f)
            self.update_file_list()
    
    def on_folder_selected(self, selection):
        if selection:
            for f in selection:
                if isinstance(f, str) and f not in self.selected_files:
                    self.selected_files.append('[Folder] ' + f)
            self.update_file_list()
    
    def on_zip_selected(self, selection):
        if selection:
            self.zip_path = selection[0] if isinstance(selection[0], str) else str(selection[0])
            self.zip_path_label.text = os.path.basename(self.zip_path)
            self.update_zip_info()
    
    def update_file_list(self):
        count = len(self.selected_files)
        self.file_list_label.text = f'Selected: {count} files/folders\n' + '\n'.join(
            [os.path.basename(f.replace('[Folder] ', '')) for f in self.selected_files[:5]]
        )
        if count > 5:
            self.file_list_label.text += f'\n... and {count-5} more'
    
    def update_zip_info(self):
        try:
            if self.zip_path and os.path.exists(self.zip_path):
                with zipfile.ZipFile(self.zip_path, 'r') as zf:
                    file_count = len(zf.namelist())
                    total_size = sum(info.file_size for info in zf.infolist())
                    is_encrypted = any(info.flag_bits & 0x1 for info in zf.infolist())
                    enc_text = ' [Encrypted]' if is_encrypted else ''
                    self.zip_info_label.text = f'Files: {file_count} | Size: {self.format_size(total_size)}{enc_text}'
        except Exception as e:
            Logger.error(f'ZBP: update_zip_info error: {e}')
            self.zip_info_label.text = 'Cannot read file info'
    
    def clear_list(self, instance):
        self.selected_files.clear()
        self.file_list_label.text = 'Selected: 0 files'
    
    def start_action(self, instance):
        if self.is_processing:
            self.show_popup('Info', 'Processing, please wait...')
            return
        
        if self.current_mode == 'compress':
            self.start_compress()
        else:
            self.start_decompress()
    
    def start_compress(self):
        if not self.selected_files:
            self.show_popup('Warning', 'Please select files or folders first!')
            return
        
        if self.use_password_cb.active:
            pwd = self.compress_pwd_input.text
            pwd_confirm = self.compress_pwd_confirm.text
            if not pwd:
                self.show_popup('Warning', 'Please enter password!')
                return
            if pwd != pwd_confirm:
                self.show_popup('Error', 'Passwords do not match!')
                return
            if len(pwd) < 4:
                self.show_popup('Warning', 'Password must be at least 4 characters!')
                return
        
        self.is_processing = True
        self.action_btn.disabled = True
        
        thread = threading.Thread(target=self.compress_thread)
        thread.daemon = True
        thread.start()
    
    def compress_thread(self):
        try:
            zip_name = self.zip_name_input.text.strip()
            if not zip_name:
                zip_name = f'compressed_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            if not zip_name.endswith('.zip'):
                zip_name += '.zip'
            
            output_path = os.path.join(self.base_path, zip_name)
            password = None
            if self.use_password_cb.active:
                password = self.compress_pwd_input.text.encode('utf-8')
            
            Clock.schedule_once(lambda dt: self.update_status('Counting files...'))
            
            total_files = 0
            for path in self.selected_files:
                clean_path = path.replace('[Folder] ', '')
                if os.path.isfile(clean_path):
                    total_files += 1
                elif os.path.isdir(clean_path):
                    for root, dirs, files in os.walk(clean_path):
                        total_files += len(files)
            
            if total_files == 0:
                Clock.schedule_once(lambda dt: self.show_popup('Warning', 'No files to compress!'))
                return
            
            processed = 0
            
            if password and HAS_PYZIPPER:
                with pyzipper.AESZipFile(output_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
                    zf.setpassword(password)
                    for path in self.selected_files:
                        clean_path = path.replace('[Folder] ', '')
                        if os.path.isfile(clean_path):
                            arcname = os.path.basename(clean_path)
                            zf.write(clean_path, arcname)
                            processed += 1
                            progress = (processed / total_files) * 100
                            Clock.schedule_once(lambda dt, p=progress, f=arcname: self.update_progress(p, f'Compress: {f}'))
                        else:
                            folder_name = os.path.basename(clean_path)
                            for root, dirs, files in os.walk(clean_path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.join(folder_name, os.path.relpath(file_path, clean_path))
                                    zf.write(file_path, arcname)
                                    processed += 1
                                    progress = (processed / total_files) * 100
                                    Clock.schedule_once(lambda dt, p=progress, f=file: self.update_progress(p, f'Compress: {f}'))
            else:
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for path in self.selected_files:
                        clean_path = path.replace('[Folder] ', '')
                        if os.path.isfile(clean_path):
                            arcname = os.path.basename(clean_path)
                            zf.write(clean_path, arcname)
                            processed += 1
                            progress = (processed / total_files) * 100
                            Clock.schedule_once(lambda dt, p=progress, f=arcname: self.update_progress(p, f'Compress: {f}'))
                        else:
                            folder_name = os.path.basename(clean_path)
                            for root, dirs, files in os.walk(clean_path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.join(folder_name, os.path.relpath(file_path, clean_path))
                                    zf.write(file_path, arcname)
                                    processed += 1
                                    progress = (processed / total_files) * 100
                                    Clock.schedule_once(lambda dt, p=progress, f=file: self.update_progress(p, f'Compress: {f}'))
            
            Clock.schedule_once(lambda dt: self.update_progress(100, 'Compress Complete!'))
            pwd_info = '\nPassword: Enabled' if password else ''
            Clock.schedule_once(lambda dt: self.show_popup('Success', f'Compress Complete!\nSave to: {output_path}{pwd_info}'))
            
        except Exception as e:
            Logger.error(f'ZBP: compress_thread error: {e}')
            Logger.error(traceback.format_exc())
            Clock.schedule_once(lambda dt: self.show_popup('Error', f'Compress failed: {str(e)}'))
        finally:
            self.is_processing = False
            Clock.schedule_once(lambda dt: setattr(self.action_btn, 'disabled', False))
    
    def start_decompress(self):
        if not self.zip_path:
            self.show_popup('Warning', 'Please select ZIP file first!')
            return
        
        self.is_processing = True
        self.action_btn.disabled = True
        
        thread = threading.Thread(target=self.decompress_thread)
        thread.daemon = True
        thread.start()
    
    def decompress_thread(self):
        try:
            output_dir = os.path.join(self.base_path, 'extracted_files')
            os.makedirs(output_dir, exist_ok=True)
            
            password = None
            if self.decompress_pwd_input.text:
                password = self.decompress_pwd_input.text.encode('utf-8')
            
            Clock.schedule_once(lambda dt: self.update_status('Reading ZIP file...'))
            
            if HAS_PYZIPPER:
                with pyzipper.AESZipFile(self.zip_path, 'r') as zf:
                    if password:
                        zf.setpassword(password)
                    file_list = zf.namelist()
                    total_files = len(file_list)
                    
                    processed = 0
                    for file in file_list:
                        zf.extract(file, output_dir, pwd=password)
                        processed += 1
                        progress = (processed / total_files) * 100
                        Clock.schedule_once(lambda dt, p=progress, f=file: self.update_progress(p, f'Extract: {f}'))
            else:
                with zipfile.ZipFile(self.zip_path, 'r') as zf:
                    if password:
                        zf.setpassword(password)
                    file_list = zf.namelist()
                    total_files = len(file_list)
                    
                    processed = 0
                    for file in file_list:
                        zf.extract(file, output_dir, pwd=password)
                        processed += 1
                        progress = (processed / total_files) * 100
                        Clock.schedule_once(lambda dt, p=progress, f=file: self.update_progress(p, f'Extract: {f}'))
            
            Clock.schedule_once(lambda dt: self.update_progress(100, 'Extract Complete!'))
            Clock.schedule_once(lambda dt: self.show_popup('Success', f'Extract Complete!\nLocation: {output_dir}\nFiles: {total_files}'))
            
        except RuntimeError as e:
            if 'password' in str(e).lower() or 'encrypted' in str(e).lower():
                Clock.schedule_once(lambda dt: self.show_popup('Error', 'Wrong password or password required!'))
            else:
                Clock.schedule_once(lambda dt: self.show_popup('Error', f'Extract failed: {str(e)}'))
        except Exception as e:
            Logger.error(f'ZBP: decompress_thread error: {e}')
            Logger.error(traceback.format_exc())
            Clock.schedule_once(lambda dt: self.show_popup('Error', f'Extract failed: {str(e)}'))
        finally:
            self.is_processing = False
            Clock.schedule_once(lambda dt: setattr(self.action_btn, 'disabled', False))
    
    def update_status(self, message):
        self.status_label.text = message
    
    def update_progress(self, value, message=''):
        self.progress_bar.value = value
        if message:
            self.status_label.text = message
    
    def show_popup(self, title, message):
        font_name = get_font()
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(
            text=message, 
            font_size='14sp', 
            font_name=font_name,
            color=(0.1, 0.1, 0.1, 1)
        ))
        close_btn = Button(
            text='OK', 
            size_hint_y=None, 
            height=dp(50), 
            font_size='16sp', 
            font_name=font_name,
            background_color=(0.2, 0.6, 0.9, 1)
        )
        content.add_widget(close_btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f'{size:.2f} {unit}'
            size /= 1024
        return f'{size:.2f} TB'


if __name__ == '__main__':
    try:
        Logger.info('ZBP: Application starting v5.0')
        ZbpYsApp().run()
    except Exception as e:
        Logger.error(f'ZBP: Fatal error: {e}')
        Logger.error(traceback.format_exc())
