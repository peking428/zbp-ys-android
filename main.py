# -*- coding: utf-8 -*-
"""
ZBP Compress/Decompress Tool - Android Version
Version 5.8 - Stable Version with Simple File Selection
"""

import os
import sys
import traceback
import zipfile
import threading
from datetime import datetime

from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('kivy', 'keyboard_mode', 'systemanddock')

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


class ZbpYsApp(App):
    def build(self):
        try:
            Logger.info('ZBP: Starting application build v5.8')
            self.title = "ZBP Tool"
            
            Window.clearcolor = (0.95, 0.95, 0.95, 1)
            
            self.base_path = self.get_storage_path()
            Logger.info(f'ZBP: Storage path: {self.base_path}')
            
            if HAS_ANDROID:
                Logger.info('ZBP: Requesting Android permissions')
                self.request_all_permissions()
            
            self.selected_files = []
            self.current_mode = "compress"
            self.is_processing = False
            self.zip_path = None
            
            self.root_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
            
            title_label = Label(
                text='[b]ZBP Compress Tool[/b]',
                font_size='22sp',
                size_hint_y=None,
                height=dp(50),
                markup=True,
                color=(0.1, 0.1, 0.1, 1)
            )
            self.root_layout.add_widget(title_label)
            
            subtitle_label = Label(
                text='ZIP Compress and Decompress Tool',
                font_size='13sp',
                size_hint_y=None,
                height=dp(30),
                color=(0.3, 0.3, 0.3, 1)
            )
            self.root_layout.add_widget(subtitle_label)
            
            mode_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10), padding=dp(5))

            self.compress_btn = ToggleButton(
                text='[b]Compress[/b]',
                group='mode',
                state='down',
                font_size='18sp',
                background_color=(0.2, 0.6, 0.9, 1),
                color=(1, 1, 1, 1),
                markup=True
            )
            self.compress_btn.bind(on_press=self.switch_mode)
            mode_layout.add_widget(self.compress_btn)

            self.decompress_btn = ToggleButton(
                text='[b]Decompress[/b]',
                group='mode',
                state='normal',
                font_size='18sp',
                background_color=(0.7, 0.7, 0.7, 1),
                color=(0.3, 0.3, 0.3, 1),
                markup=True
            )
            self.decompress_btn.bind(on_press=self.switch_mode)
            mode_layout.add_widget(self.decompress_btn)

            self.root_layout.add_widget(mode_layout)

            self.compress_layout = self.create_compress_layout()
            self.decompress_layout = self.create_decompress_layout()
            self.root_layout.add_widget(self.compress_layout)
            
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
                color=(0.2, 0.2, 0.2, 1)
            )
            self.status_label.bind(texture_size=self.status_label.setter('size'))
            self.root_layout.add_widget(self.status_label)
            
            action_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10), padding=dp(5))

            self.action_btn = Button(
                text='[b]Start Compress[/b]',
                font_size='18sp',
                background_color=(0.2, 0.7, 0.3, 1),
                markup=True
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
    
    def create_compress_layout(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))

        file_btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))

        select_file_btn = Button(
            text='[b]Add Test File[/b]',
            font_size='15sp',
            size_hint_x=0.5,
            background_color=(0.25, 0.55, 0.85, 1),
            markup=True
        )
        select_file_btn.bind(on_press=self.add_test_file)
        file_btn_layout.add_widget(select_file_btn)

        select_folder_btn = Button(
            text='[b]Add Test Folder[/b]',
            font_size='15sp',
            size_hint_x=0.5,
            background_color=(0.25, 0.55, 0.85, 1),
            markup=True
        )
        select_folder_btn.bind(on_press=self.add_test_folder)
        file_btn_layout.add_widget(select_folder_btn)

        layout.add_widget(file_btn_layout)

        self.file_list_label = Label(
            text='No files selected',
            font_size='13sp',
            size_hint_y=1,
            halign='left',
            valign='top',
            text_size=(None, None),
            color=(0.3, 0.3, 0.3, 1)
        )
        layout.add_widget(self.file_list_label)

        clear_btn = Button(
            text='[b]Clear Selection[/b]',
            font_size='14sp',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.85, 0.35, 0.35, 1),
            markup=True
        )
        clear_btn.bind(on_press=self.clear_list)
        layout.add_widget(clear_btn)

        name_layout = BoxLayout(size_hint_y=None, height=dp(45))
        name_layout.add_widget(Label(
            text='ZIP Name:',
            font_size='14sp',
            size_hint_x=0.3,
            color=(0.2, 0.2, 0.2, 1)
        ))
        self.zip_name_input = TextInput(
            text=f'compressed_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            font_size='14sp',
            size_hint_x=0.7
        )
        name_layout.add_widget(self.zip_name_input)
        layout.add_widget(name_layout)

        pwd_layout = BoxLayout(size_hint_y=None, height=dp(50))
        self.use_password_cb = CheckBox(size_hint_x=0.15, active=False)
        self.use_password_cb.bind(on_active=self.toggle_password)
        pwd_layout.add_widget(self.use_password_cb)
        pwd_layout.add_widget(Label(
            text='[b]Password[/b]',
            font_size='14sp',
            size_hint_x=0.3,
            markup=True,
            color=(0.2, 0.2, 0.2, 1)
        ))
        self.compress_pwd_input = TextInput(
            password=True,
            font_size='13sp',
            size_hint_x=0.55,
            disabled=True
        )
        pwd_layout.add_widget(self.compress_pwd_input)
        layout.add_widget(pwd_layout)

        return layout
    
    def create_decompress_layout(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))

        zip_btn_layout = BoxLayout(size_hint_y=None, height=dp(50))
        select_zip_btn = Button(
            text='[b]Add Test ZIP[/b]',
            font_size='15sp',
            size_hint_x=1,
            background_color=(0.9, 0.5, 0.2, 1),
            markup=True
        )
        select_zip_btn.bind(on_press=self.add_test_zip)
        zip_btn_layout.add_widget(select_zip_btn)
        layout.add_widget(zip_btn_layout)

        self.zip_path_label = Label(
            text='No file selected',
            font_size='13sp',
            size_hint_y=None,
            height=dp(40),
            halign='center',
            color=(0.3, 0.3, 0.3, 1)
        )
        layout.add_widget(self.zip_path_label)

        self.zip_info_label = Label(
            text='ZIP Info: --',
            font_size='12sp',
            size_hint_y=None,
            height=dp(50),
            halign='center',
            color=(0.3, 0.3, 0.3, 1)
        )
        layout.add_widget(self.zip_info_label)

        pwd_layout = BoxLayout(size_hint_y=None, height=dp(50))
        pwd_layout.add_widget(Label(
            text='Password:',
            font_size='14sp',
            size_hint_x=0.25,
            color=(0.2, 0.2, 0.2, 1)
        ))
        self.decompress_pwd_input = TextInput(
            password=True,
            font_size='14sp',
            size_hint_x=0.75,
            hint_text='(optional)'
        )
        pwd_layout.add_widget(self.decompress_pwd_input)
        layout.add_widget(pwd_layout)

        return layout
    
    def switch_mode(self, instance):
        if instance == self.compress_btn:
            mode = 'compress'
        else:
            mode = 'decompress'
        
        self.current_mode = mode
        if mode == 'compress':
            self.compress_btn.state = 'down'
            self.compress_btn.background_color = (0.2, 0.6, 0.9, 1)
            self.compress_btn.color = (1, 1, 1, 1)
            self.decompress_btn.state = 'normal'
            self.decompress_btn.background_color = (0.7, 0.7, 0.7, 1)
            self.decompress_btn.color = (0.3, 0.3, 0.3, 1)
            if self.decompress_layout in self.root_layout.children:
                self.root_layout.remove_widget(self.decompress_layout)
            if self.compress_layout not in self.root_layout.children:
                self.root_layout.add_widget(self.compress_layout, index=len(self.root_layout.children) - 4)
            self.action_btn.text = '[b]Start Compress[/b]'
            self.action_btn.background_color = (0.2, 0.7, 0.3, 1)
            self.status_label.text = 'Ready - Select files to compress'
        else:
            self.decompress_btn.state = 'down'
            self.decompress_btn.background_color = (0.9, 0.5, 0.2, 1)
            self.decompress_btn.color = (1, 1, 1, 1)
            self.compress_btn.state = 'normal'
            self.compress_btn.background_color = (0.7, 0.7, 0.7, 1)
            self.compress_btn.color = (0.3, 0.3, 0.3, 1)
            if self.compress_layout in self.root_layout.children:
                self.root_layout.remove_widget(self.compress_layout)
            if self.decompress_layout not in self.root_layout.children:
                self.root_layout.add_widget(self.decompress_layout, index=len(self.root_layout.children) - 4)
            self.action_btn.text = '[b]Start Decompress[/b]'
            self.action_btn.background_color = (0.9, 0.5, 0.2, 1)
            self.status_label.text = 'Ready - Select ZIP file to decompress'
        self.progress_bar.value = 0
    
    def toggle_password(self, instance, value):
        self.compress_pwd_input.disabled = not value
        if not value:
            self.compress_pwd_input.text = ''
    
    def add_test_file(self, instance):
        try:
            test_file_path = os.path.join(self.base_path, 'test_file.txt')
            if not os.path.exists(test_file_path):
                with open(test_file_path, 'w', encoding='utf-8') as f:
                    f.write('Test file for ZBP Compress Tool\n')
                    f.write(f'Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                    f.write('This is a test file for compression.\n')
            
            if test_file_path not in self.selected_files:
                self.selected_files.append(test_file_path)
                self.update_file_list()
                self.status_label.text = f'Added test file: {os.path.basename(test_file_path)}'
        except Exception as e:
            Logger.error(f'ZBP: add_test_file error: {e}')
            self.show_popup('Error', f'Failed to add test file: {str(e)}')
    
    def add_test_folder(self, instance):
        try:
            test_folder_path = os.path.join(self.base_path, 'test_folder')
            if not os.path.exists(test_folder_path):
                os.makedirs(test_folder_path, exist_ok=True)
                
                for i in range(1, 4):
                    sub_file = os.path.join(test_folder_path, f'file_{i}.txt')
                    with open(sub_file, 'w', encoding='utf-8') as f:
                        f.write(f'Test file {i}\n')
                        f.write(f'Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            
            folder_label = '[Folder] ' + test_folder_path
            if folder_label not in self.selected_files:
                self.selected_files.append(folder_label)
                self.update_file_list()
                self.status_label.text = f'Added test folder: test_folder'
        except Exception as e:
            Logger.error(f'ZBP: add_test_folder error: {e}')
            self.show_popup('Error', f'Failed to add test folder: {str(e)}')
    
    def add_test_zip(self, instance):
        try:
            test_zip_path = os.path.join(self.base_path, 'test_file.txt')
            if os.path.exists(test_zip_path):
                self.zip_path = test_zip_path
                self.zip_path_label.text = os.path.basename(self.zip_path)
                self.status_label.text = f'Selected: {os.path.basename(self.zip_path)}'
                self.update_zip_info()
            else:
                self.add_test_file(None)
                self.zip_path = os.path.join(self.base_path, 'test_file.txt')
                self.zip_path_label.text = os.path.basename(self.zip_path)
                self.status_label.text = f'Created and selected test file'
        except Exception as e:
            Logger.error(f'ZBP: add_test_zip error: {e}')
            self.show_popup('Error', f'Failed to add test ZIP: {str(e)}')
    
    def update_file_list(self):
        count = len(self.selected_files)
        if count == 0:
            self.file_list_label.text = 'No files selected'
            return
        lines = []
        for f in self.selected_files:
            clean_path = f.replace('[Folder] ', '')
            lines.append(clean_path)
        self.file_list_label.text = f'Selected {count} files/folders:\n\n' + '\n'.join(lines)
        if count > 10:
            self.file_list_label.text += f'\n\n... and {count - 10} more'

    def update_zip_info(self):
        try:
            if self.zip_path and os.path.exists(self.zip_path):
                if self.zip_path.endswith('.zip'):
                    with zipfile.ZipFile(self.zip_path, 'r') as zf:
                        file_count = len(zf.namelist())
                        total_size = sum(info.file_size for info in zf.infolist())
                        is_encrypted = any(info.flag_bits & 0x1 for info in zf.infolist())
                        enc_text = ' [Encrypted]' if is_encrypted else ''
                        self.zip_info_label.text = f'Files: {file_count} | Size: {self.format_size(total_size)}{enc_text}'
                else:
                    self.zip_info_label.text = f'File selected (not a ZIP)'
        except Exception as e:
            Logger.error(f'ZBP: update_zip_info error: {e}')
            self.zip_info_label.text = 'Cannot read file info'

    def clear_list(self, instance):
        self.selected_files.clear()
        self.file_list_label.text = 'No files selected'
    
    def start_action(self, instance):
        try:
            if self.is_processing:
                self.show_popup('Info', 'Processing, please wait...')
                return
            
            self.status_label.text = 'Button clicked - starting...'
            
            if self.current_mode == 'compress':
                self.start_compress()
            else:
                self.start_decompress()
        except Exception as e:
            Logger.error(f'ZBP: start_action error: {e}')
            Logger.error(traceback.format_exc())
            self.show_popup('Error', f'Action failed: {str(e)}')
    
    def start_compress(self):
        try:
            if not self.selected_files:
                self.show_popup('Warning', 'Please select files or folders first!')
                return
            
            if self.use_password_cb.active:
                pwd = self.compress_pwd_input.text
                if not pwd:
                    self.show_popup('Warning', 'Please enter password!')
                    return
                if len(pwd) < 4:
                    self.show_popup('Warning', 'Password must be at least 4 characters!')
                    return
            
            self.is_processing = True
            self.action_btn.disabled = True
            
            thread = threading.Thread(target=self.compress_thread)
            thread.daemon = True
            thread.start()
        except Exception as e:
            Logger.error(f'ZBP: start_compress error: {e}')
            Logger.error(traceback.format_exc())
            self.show_popup('Error', f'Compress start failed: {str(e)}')
            self.is_processing = False
            self.action_btn.disabled = False
    
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
                Clock.schedule_once(lambda dt: self.end_processing())
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
                        elif os.path.isdir(clean_path):
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
                        elif os.path.isdir(clean_path):
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
            Clock.schedule_once(lambda dt: self.end_processing())
    
    def start_decompress(self):
        try:
            if not self.zip_path:
                self.show_popup('Warning', 'Please select ZIP file first!')
                return
            
            self.is_processing = True
            self.action_btn.disabled = True
            
            thread = threading.Thread(target=self.decompress_thread)
            thread.daemon = True
            thread.start()
        except Exception as e:
            Logger.error(f'ZBP: start_decompress error: {e}')
            Logger.error(traceback.format_exc())
            self.show_popup('Error', f'Decompress start failed: {str(e)}')
            self.is_processing = False
            self.action_btn.disabled = False
    
    def decompress_thread(self):
        try:
            output_dir = os.path.join(self.base_path, 'extracted_files')
            os.makedirs(output_dir, exist_ok=True)
            
            password = None
            if self.decompress_pwd_input.text:
                password = self.decompress_pwd_input.text.encode('utf-8')
            
            Clock.schedule_once(lambda dt: self.update_status('Reading ZIP file...'))
            
            if not self.zip_path.endswith('.zip'):
                Clock.schedule_once(lambda dt: self.show_popup('Warning', 'Selected file is not a ZIP!'))
                Clock.schedule_once(lambda dt: self.end_processing())
                return
            
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
            Clock.schedule_once(lambda dt: self.end_processing())
    
    def end_processing(self):
        self.is_processing = False
        self.action_btn.disabled = False
    
    def update_status(self, message):
        self.status_label.text = message
    
    def update_progress(self, value, message=''):
        self.progress_bar.value = value
        if message:
            self.status_label.text = message
    
    def show_popup(self, title, message):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
            content.add_widget(Label(
                text=message, 
                font_size='14sp', 
                color=(0.1, 0.1, 0.1, 1)
            ))
            close_btn = Button(
                text='OK', 
                size_hint_y=None, 
                height=dp(50), 
                font_size='16sp', 
                background_color=(0.2, 0.6, 0.9, 1)
            )
            content.add_widget(close_btn)
            
            popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
            close_btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            Logger.error(f'ZBP: show_popup error: {e}')
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f'{size:.2f} {unit}'
            size /= 1024
        return f'{size:.2f} TB'


if __name__ == '__main__':
    try:
        Logger.info('ZBP: Application starting v5.8')
        ZbpYsApp().run()
    except Exception as e:
        Logger.error(f'ZBP: Fatal error: {e}')
        Logger.error(traceback.format_exc())
