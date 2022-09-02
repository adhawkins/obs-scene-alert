import obspython as S
from datetime import datetime, timedelta

class SingletonType(type):
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(SingletonType, cls).__call__(*args, **kwargs)
            return cls.__instance

class SceneAlert(metaclass=SingletonType):
	def __init__(self):
		self.timerStart = datetime.now()
		self.timeBeforeAlert = 5
		self.alertName = ""
		self.alert = None
		self.alertUnmuted = False
		self.restartAfterMute = True

	def unload(self):
		self.stopTimer()

		if self.alert:
			signalHandler = S.obs_source_get_signal_handler(self.alert)
			S.signal_handler_disconnect(signalHandler, "activate", handle_activate)
			S.signal_handler_disconnect(signalHandler, "deactivate", handle_deactivate)
			S.signal_handler_disconnect(signalHandler, "mute", handle_mute)

			S.obs_source_release(self.alert)

	def defaults(self, settings):
		S.obs_data_set_default_string(settings, "alert_name", "")
		S.obs_data_set_default_double(settings, "time_before_alert", 5)
		S.obs_data_set_default_bool(settings, "restart_after_mute", True)

	def properties(self):
		props = S.obs_properties_create()
		S.obs_properties_add_text(props, "alert_name", "Alert name", S.OBS_TEXT_DEFAULT)
		S.obs_properties_add_int(props, "time_before_alert", "Time before alert (seconds)", 10, 300, 1)
		S.obs_properties_add_bool(props, "restart_after_mute", "Restart timer after manual mute")

		return props

	def update(self, settings):
		self.alertName = S.obs_data_get_string(settings, "alert_name")
		self.timeBeforeAlert = S.obs_data_get_int(settings, "time_before_alert")
		self.restartAfterMute = S.obs_data_get_bool(settings, "restart_after_mute")

		print(f"Alert: '{self.alertName}', time: {self.timeBeforeAlert}, restart: {self.restartAfterMute}")

		self.findAlert()

	def finishedLoading(self):
		self.findAlert()

	def sceneChanged(self):
		if self.alert:
			S.obs_source_set_muted(self.alert, True)

			if S.obs_source_active(self.alert):
				self.startTimer()
			else:
				self.stopTimer()

	def startTimer(self):
		self.stopTimer()

		self.timerStart = datetime.now()
		self.alertUnmuted = False

		S.timer_add(timerCallback, 1000)

	def stopTimer(self):
		S.timer_remove(timerCallback)

	def timerCallback(self):
		duration = datetime.now() - self.timerStart

		print(f"Duration: {duration}, timeBefore: {self.timeBeforeAlert}")
		if duration > timedelta(seconds = self.timeBeforeAlert) and not self.alertUnmuted:
			if self.alert:
				S.obs_source_set_muted(self.alert, False)
				self.alertUnmuted = True
				self.stopTimer()

	def findAlert(self):
		print("In findAlert")

		if self.alert:
			signalHandler = S.obs_source_get_signal_handler(self.alert)
			S.signal_handler_disconnect(signalHandler, "activate", handle_activate)
			S.signal_handler_disconnect(signalHandler, "deactivate", handle_deactivate)
			S.signal_handler_disconnect(signalHandler, "mute", handle_mute)

			S.obs_source_release(self.alert)
			self.alert = None

		sources = S.obs_enum_sources()
		for source in sources:
			name = S.obs_source_get_name(source)

			if self.alertName and name == self.alertName:
				print("Found alert")
				self.alert = S.obs_source_get_ref(source)

				S.obs_source_set_muted(self.alert, True)

				signalHandler = S.obs_source_get_signal_handler(self.alert)
				S.signal_handler_connect(signalHandler, "activate", handle_activate)
				S.signal_handler_connect(signalHandler, "deactivate", handle_deactivate)
				S.signal_handler_connect(signalHandler, "mute", handle_mute)

				if S.obs_source_active(self.alert):
					self.startTimer()

				break

		S.source_list_release(sources)

	def doActivate(self, callbackData, activate):
		source = S.calldata_source(callbackData, "source")
		if source:
			name = S.obs_source_get_name(source)
			print(f"Source: '{name}, alertName: '{self.alertName}', activate: {activate}")
			if name == self.alertName:
				if activate:
					self.startTimer()
				else:
					self.stopTimer()

	def handleMute(self, callbackData):
		if self.restartAfterMute:
			source = S.calldata_source(callbackData, "source")
			if source:
				name = S.obs_source_get_name(source)
				if name == self.alertName:
					if S.obs_source_active(self.alert):
						muted = S.calldata_bool(callbackData, "muted")
						if muted:
							self.startTimer()

def script_load(settings):
	print("script_load")

	S.obs_frontend_add_event_callback(on_event)

	sceneAlert = SceneAlert()
	sceneAlert.findAlert()

def script_unload():
	print("script_unload")

	sceneAlert = SceneAlert()
	sceneAlert.unload()

# Called to set default values of data settings
def script_defaults(settings):
	sceneAlert = SceneAlert()
	sceneAlert.defaults(settings)

# Called to display the properties GUI
def script_properties():
	sceneAlert = SceneAlert()
	return sceneAlert.properties()

# Called after change of settings including once after script load
def script_update(settings):
	print("script_update")
	sceneAlert = SceneAlert()
	sceneAlert.update(settings)

def script_description():
	return "Play a warning sound if a scene has been selected for a period of time"

def on_event(event):
	sceneAlert = SceneAlert()

	if event == S.OBS_FRONTEND_EVENT_FINISHED_LOADING:
		print("finished loading")
		sceneAlert.finishedLoading()
	elif event == S.OBS_FRONTEND_EVENT_SCENE_CHANGED:
		print("Scene changed")
		sceneAlert.sceneChanged()

def timerCallback():
	sceneAlert = SceneAlert()
	sceneAlert.timerCallback()

def handle_activate(callbackData):
	print("handle_activate")
	sceneAlert = SceneAlert()
	sceneAlert.doActivate(callbackData, True)

def handle_deactivate(callbackData):
	print("handle_deactivate")
	sceneAlert = SceneAlert()
	sceneAlert.doActivate(callbackData, False)

def handle_mute(callbackData):
	print("handle_mute")
	sceneAlert = SceneAlert()
	sceneAlert.handleMute(callbackData)

