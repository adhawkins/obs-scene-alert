# obs-scene-alert
An OBS Python script to unmute an alert sound if you stay on the same scene for too long.

If the specified source appears on the active scene, a timer is started. When the configured elapsed time expires, the alert is unmuted.

Optionally, if the alert sound is manually muted while active, then the timer is restarted allowing the alert sound to be played again after the configured period.

# Settings
* Alert name - The name of the alert
* Time before alert - The time to elapse before the alert is unmuted
* Restart timer after manual mute - Whether or not to restart the timer if the alert is manually muted

# Usage
Create a source in OBS that contains the alert sound. If placing this alert on multiple scenes, be sure to place the existing alert on subsequent scenes. If you don't want this alert to play back on stream (or in the recording) then set its advanced audio properties to 'Monitor Only' and ensure an appropriate audio monitoring device is configured in OBS.

The script will then monitor scene changes, and if the scene is changed to one which contains the configured alert, then a timer is started (or restarted). If this timer expires (the configured 'Time before alert' is reached) then the alert will be unmuted.

Optionally, if the alert is then manually muted, the timer can be automatically restarted, allowing it to fire again if the same scene remains selected for the configured time.