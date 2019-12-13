_________________
### Focusing
##### focus.py `nb_step` `orientation`

- `nb_step` : **integer** (from 1 to 100000) - number of step to perform by the stage (about 31um/step)
- `orientation` : **string** - orientation of the focus either `up` or `down`

Example:

    python3.7 $HOME/PlanktonScope/scripts/focus.py 650 up

_________________
### Pumping
##### pump.py `volume` `flowrate` `action`

- `volume` : **integer** 
- `flowrate` : **float** 
- `action` : **string**

Example:

    python3.7 $HOME/PlanktonScope/scripts/pump.py 24 3.2 suck
    
_________________
### Killing Focus or Pump event
##### killer.sh `event_to_kill.py`

- `event_to_kill.py` : **string**


Example:

    bash killer.sh pump.py
    
_________________
### Image
##### image.py `sample_project` `sample_id` `acq_id` `volume` `flowrate`

-`sample_project` : **string**
- `sample_id` : **string**
- `acq_id` : **string**
- `volume` : **integer**
- `flowrate` : **float**

Example:

    python3.7 pump.py tara_pacific station_125 exp_1 24 3.2
    
_________________
### Kill Image
##### kill_image.sh image.py `sample_project` `sample_id` `acq_id`

- `sample_project` : **string**
- `sample_id` : **string**
- `acq_id` : **string**

Example:

    bash killer.sh image.py tara_pacific station_125 exp_1
    
_________________

### Light
##### light.py `state`

- `state` : **string**

Example:

    python3.7 light.py on
