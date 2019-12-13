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

    python3.7 $HOME/PlanktonScope/scripts/pump.py 1 10 suck
    
_________________
### Image
##### image.py `in_path` `sample_project` `sample_id` `acq_id` `volume` `flowrate`

- `in_path` : **string** - directory to store acquisitions **the path has to end with /**
- `sample_project` : **string**
- `sample_id` : **string**
- `acq_id` : **string**
- `volume` : **integer**
- `flowrate` : **float**

Example:

    python3.7 $HOME/PlanktonScope/scripts/image.py $HOME/PlanktonScope/Acquisitions/ tara_pacific station_125 exp_1 24 3.2
    

_________________

### Light
##### light.py `state`

- `state` : **string** - `on` OR `off`

Example:

    python3.7 $HOME/PlanktonScope/scripts/light.py on


_________________
### Fan
##### fan.py `state`

- `state` : **string** - `on` OR `off`

Example:

    python3.7 $HOME/PlanktonScope/scripts/fan.py on
    
_________________
### Killing Focus or Pump event
##### killer.sh `event_to_kill.py`

- `event_to_kill.py` : **string**


Example:

    bash $HOME/PlanktonScope/scripts/killer.sh pump.py
    
_________________
### Kill Image
##### kill_image.sh image.py `sample_project` `sample_id` `acq_id`

- `sample_project` : **string**
- `sample_id` : **string**
- `acq_id` : **string**

Example:

    bash $HOME/PlanktonScope/scripts/killer.sh image.py tara_pacific station_125 exp_1
    
