import obspython as S
from datetime import datetime, timedelta

timerStart = datetime.now()
timeBeforeAlert=5
alertName = "Scene Alert"
alert = None
alertUnmuted = False
restartAfterMute = True

# Called to set default values of data settings
def script_defaults(settings):
	S.obs_data_set_default_string(settings, "alert_name", "")
	S.obs_data_set_default_double(settings, "time_before_alert", 5)
	S.obs_data_set_default_bool(settings, "restart_after_mute", True)

# Called to display the properties GUI
def script_properties():
	props = S.obs_properties_create()
	S.obs_properties_add_text(props, "alert_name", "Alert name", S.OBS_TEXT_DEFAULT)
	S.obs_properties_add_int(props, "time_before_alert", "Time before alert (seconds)", 10, 300, 1)
	S.obs_properties_add_bool(props, "restart_after_mute", "Restart timer after manual mute")

	return props

# Called after change of settings including once after script load
def script_update(settings):
	print("script_update")
	global alertName, timeBeforeAlert, restartAfterMute

	alertName = S.obs_data_get_string(settings, "alert_name")
	timeBeforeAlert = S.obs_data_get_int(settings, "time_before_alert")
	restartAfterMute = S.obs_data_get_bool(settings, "restart_after_mute")

	print(f"Alert: '{alertName}', time: {timeBeforeAlert}, restart: {restartAfterMute}")

	findAlert()

def script_load(settings):
	print("script_load")
	S.obs_frontend_add_event_callback(on_event)

	findAlert()

def script_description():
	return "Play a warning sound if a scene has been selected for a period of time"

def script_unload():
	print("script_unload")
	global alert

	stop_timer()

	if alert:
		signalHandler = S.obs_source_get_signal_handler(alert)
		S.signal_handler_disconnect(signalHandler, "activate", handle_activate)
		S.signal_handler_disconnect(signalHandler, "deactivate", handle_deactivate)
		S.signal_handler_disconnect(signalHandler, "mute", handle_mute)

		S.obs_source_release(alert)

def on_event(event):
	if event == S.OBS_FRONTEND_EVENT_FINISHED_LOADING:
		print("finished loading")
		findAlert()
	elif event == S.OBS_FRONTEND_EVENT_SCENE_CHANGED:
		print("Scene changed")
		global alert

		if alert:
			S.obs_source_set_muted(alert, True)

			if S.obs_source_active(alert):
				start_timer()
			else:
				stop_timer()

def timerCallback():
	global alertUnmuted, timerStart, alert, timeBeforeAlert

	duration = datetime.now() - timerStart

	print(f"Duration: {duration}, timeBefore: {timeBeforeAlert}")
	if duration > timedelta(seconds = timeBeforeAlert) and not alertUnmuted:
		if alert:
			S.obs_source_set_muted(alert, False)
			alertUnmuted = True
			stop_timer()

def findAlert():
	print("In findAlert")
	global alert

	if alert:
		signalHandler = S.obs_source_get_signal_handler(alert)
		S.signal_handler_disconnect(signalHandler, "activate", handle_activate)
		S.signal_handler_disconnect(signalHandler, "deactivate", handle_deactivate)
		S.signal_handler_disconnect(signalHandler, "mute", handle_mute)

		S.obs_source_release(alert)
		alert = None

	sources = S.obs_enum_sources()
	for source in sources:
		name = S.obs_source_get_name(source)

		if alertName and name == alertName:
			print("Found alert")
			alert = S.obs_source_get_ref(source)

			S.obs_source_set_muted(alert, True)

			signalHandler = S.obs_source_get_signal_handler(alert)
			S.signal_handler_connect(signalHandler, "activate", handle_activate)
			S.signal_handler_connect(signalHandler, "deactivate", handle_deactivate)
			S.signal_handler_connect(signalHandler, "mute", handle_mute)

			if S.obs_source_active(alert):
				start_timer()

			break

	S.source_list_release(sources)

def doActivate(callbackData, activate):
	source = S.calldata_source(callbackData, "source")
	if source:
		name = S.obs_source_get_name(source)
		print(f"Source: '{name}, alertName: '{alertName}', activate: {activate}")
		if name == alertName:
			if activate:
				start_timer()
			else:
				stop_timer()

def handle_activate(callbackData):
	print("handle_activate")
	doActivate(callbackData, True)

def handle_deactivate(callbackData):
	print("handle_deactivate")
	doActivate(callbackData, False)

def handle_mute(callbackData):
	global alertName, alert, restartAfterMute

	source = S.calldata_source(callbackData, "source")
	if source:
		name = S.obs_source_get_name(source)
		if name == alertName:
			if S.obs_source_active(alert):
				muted = S.calldata_bool(callbackData, "muted")
				if muted:
					if restartAfterMute:
						start_timer()

def start_timer():
	stop_timer()

	global timerStart, alertUnmuted

	timerStart = datetime.now()
	alertUnmuted = False

	S.timer_add(timerCallback, 1000)

def stop_timer():
	global alert

	S.timer_remove(timerCallback)

