import ScreenCloud
from PythonQt.QtCore import QFile, QSettings
from PythonQt.QtGui import QWidget, QDialog, QDesktopServices
from PythonQt.QtUiTools import QUiLoader
import subprocess, time, string, sys
from collections import defaultdict

class PuushUploader():
	def __init__(self):
		self.uil = QUiLoader()

	def showSettingsUI(self, parentWidget):
		self.parentWidget = parentWidget
		self.settingsDialog = self.uil.load(QFile(workingDir + "/settings.ui"), parentWidget)
		self.settingsDialog.connect("accepted()", self.saveSettings)
		self.loadSettings()
		self.settingsDialog.group_puush.input_api_key.text = self.apiKey
		self.settingsDialog.open()

	def loadSettings(self):
		settings = QSettings()
		settings.beginGroup("uploaders")
		settings.beginGroup("puush")
		self.apiKey = settings.value("apiKey", "")
		self.outputIsUrl = True
		settings.endGroup()
		settings.endGroup()

	def saveSettings(self):
		settings = QSettings()
		settings.beginGroup("uploaders")
		settings.beginGroup("puush")
		settings.setValue("apiKey", self.settingsDialog.group_puush.input_api_key.text)
		settings.endGroup()
		settings.endGroup()

	def isConfigured(self):
		self.loadSettings()
		if not self.apiKey:
			return False
		return True

	def getFilename(self):
		timestamp = time.time()
		return ScreenCloud.formatFilename(str(timestamp))

	def upload(self, screenshot, name):
		self.loadSettings()
		try:
			tmpFilename = QDesktopServices.storageLocation(QDesktopServices.TempLocation) + "/" + name
		except AttributeError:
			from PythonQt.QtCore import QStandardPaths #fix for Qt5
			tmpFilename = QStandardPaths.writableLocation(QStandardPaths.TempLocation) + "/" + name
		screenshot.save(QFile(tmpFilename), ScreenCloud.getScreenshotFormat())
		base_path=os.path.dirname(os.path.realpath(__file__)) + '/'
		command = "bash " + base_path + "puush.sh " + self.apiKey + " " + tmpFilename
		try:
			command = command.encode(sys.getfilesystemencoding())
		except UnicodeEncodeError:
			ScreenCloud.setError("Invalid characters in command '" + command + "'")
			return False
		try:
			if self.outputIsUrl:
				pipe = subprocess.PIPE
			else:
				pipe = None


			p = subprocess.Popen(command, shell=True, stdout=pipe)
			p.wait()
			if p.returncode > 0:
				ScreenCloud.setError("Command " + command + " did not return 0")
				return False
			elif self.outputIsUrl:
				result = p.stdout.read()
				result = result.strip()
				ScreenCloud.setUrl(result)

		except OSError:
			ScreenCloud.setError("Failed to run command " + command)
			return False

		return True