import obspython as S
from datetime import datetime, timedelta
from pprint import pprint

timerStart = datetime.now()
timeBeforeAlert=5
alertName = "Scene Alert"
alert = None
alertUnmuted = False

# Called to set default values of data settings
def script_defaults(settings):
	print("script_defaults")
	S.obs_data_set_default_string(settings, "alert_name", "")
	S.obs_data_set_default_double(settings, "time_before_alert", 5)

# Called to display the properties GUI
def script_properties():
	print("script_properties")
	props = S.obs_properties_create()
	S.obs_properties_add_text(props, "alert_name", "Alert name", S.OBS_TEXT_DEFAULT)
	S.obs_properties_add_int(props, "time_before_alert", "Time before alert (seconds)", 10, 300, 1)
	return props

# Called after change of settings including once after script load
def script_update(settings):
	print("script_update")
	global alertName, timeBeforeAlert

	alertName = S.obs_data_get_string(settings, "alert_name")
	timeBeforeAlert = S.obs_data_get_int(settings, "time_before_alert")

	findAlert()

def script_load(settings):
	print("script_loa")
	S.obs_frontend_add_event_callback(on_event)

	findAlert()

def script_description():
	return "Play a warning sound if a scene has been selected for a period of time"

def script_unload():
	print("script_unload")
	global alert

	if alert:
		signalHandler = S.obs_source_get_signal_handler(alert)
		S.signal_handler_disconnect(signalHandler, "activate", handle_activate)
		S.signal_handler_disconnect(signalHandler, "deactivate", handle_deactivate)

		S.obs_source_release(alert)

def on_event(event):
	if event == S.OBS_FRONTEND_EVENT_FINISHED_LOADING:
		print("finished loading")
		findAlert()
	elif event == S.OBS_FRONTEND_EVENT_SCENE_CHANGED:
		print("Scene changed")
		global alert, timerStart, alertUnmuted

		if alert:
			S.obs_source_set_muted(alert, True)

		alertUnmuted = False
		timerStart = datetime.now()

def timerCallback():
	global alertUnmuted, timerStart, alert, timeBeforeAlert

	duration = datetime.now() - timerStart

	print(f"Duration: {duration}, timeBefore: {timeBeforeAlert}")
	if duration > timedelta(seconds = timeBeforeAlert) and not alertUnmuted:
		if alert:
			S.obs_source_set_muted(alert, False)
			alertUnmuted = True

def findAlert():
	print("In findAlert")
	global alert

	if alert:
		signalHandler = S.obs_source_get_signal_handler(alert)
		S.signal_handler_disconnect(signalHandler, "activate", handle_activate)
		S.signal_handler_disconnect(signalHandler, "deactivate", handle_deactivate)

		S.obs_source_release(alert)
		alert = None

	sources = S.obs_enum_sources()
	for source in sources:
		name = S.obs_source_get_name(source)

		if alertName and name == alertName:
			print("Found alert")
			alert = S.obs_source_get_ref(source)

			signalHandler = S.obs_source_get_signal_handler(alert)
			S.signal_handler_connect(signalHandler, "activate", handle_activate)
			S.signal_handler_connect(signalHandler, "deactivate", handle_deactivate)

			if S.obs_source_active(alert):
				S.obs_source_set_muted(alert, True)
				S.timer_add(timerCallback, 1000)

			break

	S.source_list_release(sources)

def doActivate(callbackData, activate):
	print("doActivate")
	source = S.calldata_source(callbackData, "source")
	if source:
		name = S.obs_source_get_name(source)
		print(f"Source: '{name}, alertName: '{alertName}', activate: {activate}")
		if name == alertName:
			if activate:
				S.timer_add(timerCallback, 1000)
			else:
				S.timer_remove(timerCallback)

def handle_activate(callbackData):
	print("handle_activate")
	doActivate(callbackData, True)

def handle_deactivate(callbackData):
	print("handle_deactivate")
	doActivate(callbackData, False)
