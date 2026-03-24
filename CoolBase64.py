import string
import base64
import io
import webbrowser

import sublime_plugin
import sublime

class Base64EncodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        for s in view.sel():
            if s.empty():
                sublime.active_window().run_command("copy_file_as_base64")
                break

            encoded = base64.encodebytes(view.substr(s).encode())
            view.replace(edit, s, encoded.decode().replace("\n", ""))

class Base64DecodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        for s in view.sel():
            if s.empty():
                continue
            enc_s = view.substr(s)
            if len(enc_s) % 4 == 2:
                enc_s += "=="
            elif len(enc_s) % 4 == 3:
                enc_s += "="

            decoded = base64.decodebytes(enc_s.encode())
            try:
                decodedstring = decoded.decode("utf-8").replace("\r", "")
            except UnicodeDecodeError:
                decodedstring = decoded.decode("cp1252").replace("\r", "")
            view.replace(edit, s, decodedstring)

class CopyFileAsBase64Command(sublime_plugin.WindowCommand):
    def run(self):
    	fileinfo = sublime.active_window().extract_variables()
    	encoded = io.BytesIO()
    	base64.encode(open(fileinfo["file"], "rb"), encoded)
    	encoded = encoded.getvalue().decode().replace("\n", "")
    	sublime.set_clipboard(encoded)
    	print(fileinfo["file_name"] + " copied as Base64")

class CopyFileAsBase64WebUrlCommand(sublime_plugin.WindowCommand):
    def run(self):
        fileinfo = sublime.active_window().extract_variables()
        encoded = io.BytesIO()
        base64.encode(open(fileinfo["file"], "rb"), encoded)
        encoded = encoded.getvalue().decode().replace("\n", "")
        fileext = fileinfo["file_extension"]

        if (fileext == "jpg" or fileext == "png" or
                fileext == "webp" or fileext == "gif" or
                fileext == "jpeg"):
            datatype = "image/%s" % (fileext)
        elif (fileext == "mp3" or fileext == "ogg" or
                fileext == "opus" or fileext == "wav" or
                fileext == "flac" or fileext == "m4a" or
                fileext == "aac"):
            datatype = "audio/%s" % (fileext)
        elif (fileext == "mp4" or fileext == "avi" or
                fileext == "mkv" or fileext == "mov" or
                fileext == "webm" or fileext == "3gp"):
            datatype = "video/%s" % (fileext)
        else:
            datatype = "text"

        url = "data:%s;base64,%s" % (datatype, encoded)
        sublime.set_clipboard(url)

        print("%s copied as %s Base64 Web URL" % (fileinfo["file_name"], datatype))

class Base64SaveAsBinaryCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def process(index):
            if index >= len(selections):
                return
            binary_data, path, suggested_name = selections[index]

            def on_done(selected_path):
                if selected_path:
                    with open(selected_path, 'wb') as f:
                        f.write(binary_data)
                # Переходим к следующему выделению, независимо от того, сохранили или отменили
                process(index + 1)

            sublime.save_dialog(on_done, directory=path, name=suggested_name)

        view = self.view
        selections = []

        for s in view.sel():
            if s.empty():
                continue
            enc_s = view.substr(s)
            if len(enc_s) % 4 == 2:
                enc_s += "=="
            elif len(enc_s) % 4 == 3:
                enc_s += "="

            if view.file_name():
                path = view.file_name().rsplit('\\', 1)[0]
                suggested_name = view.file_name().rsplit('\\', 1)[1]
            else:
                path = ""
                suggested_name = "decoded_file"

            binary_data = base64.b64decode(enc_s)
            selections.append((binary_data, path, suggested_name))

        process(0)