# Details about used MQTT messages

## Topic lists
- [`actuator`](#actuator)
    - [`actuator/pump`](#actuatorpump)
    - [`actuator/focus`](#actuatorfocus)
- [`imager/image`](#imagerimage)
- [`segmenter/segment`](#segmentersegment)
- [`status`](#status)
    - [`status/pump`](#statuspump)
    - [`status/focus`](#statusfocus)
    - [`status/imager`](#statusimager)
    - [`status/segmenter`](#statussegmenter)
    - [`status/segmenter/name`](#statussegmentername)
    - [`status/segmenter/object_id`](#statussegmenterobject_id)
    - [`status/segmenter/metric`](#statussegmentermetric)



## Topic details
### `actuator`
#### `actuator/pump`
Control the movement of the pump. The message is a JSON object:
```json
{
  "action": "move",
  "direction": "FORWARD",
  "volume": 10,
  "flowrate": 1
}
```
This messages make the pump move 10mL forward at 1mL/min.

Another supported message is:
```json
{
  "action": "stop"
}
```

- Receive only

#### `actuator/focus`
Control of the focus stage. The message is a JSON object, speed is optional:
```json
{
  "action": "move",
  "direction": "UP",
  "distance": 0.26,
  "speed": 1
}
```

This message makes the stage move up by 10mm.

Another supported message is:
```json
{
  "action": "stop"
}
```

- Receive only


### `imager/image`
This topic controls the camera and capture. The message allowed is a JSON message:
```json
{
  "action": "image",
  "pump_direction": "FORWARD",
  "volume": 1,
  "nb_frame": 200
}
```

Volume is in mL.

This topic can also receive a config update message:
```json
{
  "action": "config",
  "config": {...}
}
```

A camera settings message can also be received here. The fields `iso` and `shutter_speed` are optionals:
```json
{
  "action": "settings",
  "iso": 100,
  "shutter_speed": 40
}
```

- Receive only

### `segmenter/segment`
This topic controls the segmentation process. The message is a JSON object:
```json
{
  "action": "segment",
  "path": "/path/to/segment",
  "settings": {
    "force": False,
    "recursive": True,
    "ecotaxa": True,
    "keep": True
  }
}
```

`action` can also be `stop`.
The `action` element is the only element required. If no `path` is supplied, the whole images repository is segmented recursively (this is very long!).
`force` is going to overcome the presence of the file `done` that is here to prevent for resegmenting a folder already segmented.
`recursive` will force parsing all folders below `path`.
`ecotaxa` activates the export of an ecotaxa compatible archive.
`keep` allows to remove or keep the roi (when you do an ecotaxa export, no effects otherwise, the roi are kept).

- Receive only

### `status`
This high-level topic is used to send information to the Node-Red process. There is no publication or receive at this level.

#### `status/pump`
State of the pump. It's a JSON object with:
```json
{
  "status": "Started",
  "duration": 25
}
```

Duration is a best guess estimate. It should not be used to control the other events. If you want to wait for a movement to finish, the best thing to do is to wait for the message `Done`.

Status can be `Started`, `Ready`, `Done`, `Interrupted`, `Error`, `Dead`.

- Publish only

#### `status/focus`
State of the focus stage. It's a JSON object with:
```json
{
  "status": "Started",
  "duration": 25
}
```

Duration is a best guess estimate. It should not be used to control the other events. If you want to wait for a movement to finish, the best thing to do is to wait for the message `Done`.

Status is one of `Started`, `Ready`, `Done`, `Interrupted`, `Error`, `Dead`.

- Publish only

#### `status/imager`
State of the imager. It's a JSON object with:
```json
{
  "status": "Started",
  "time_left": 25
}
```

Status is one of `Started`, `Ready`, `Completed` or `12_11_15_0.1.jpg has been imaged`.

- Publish only

#### `status/segmenter`
Status of the segmentation. It's a JSON object with:
```json
{
  "status": "Started",
}
```

`status` is one of `Started`, `Done`, `Interrupted`, `Busy`, `Ready` or `Dead`.

- Publish only

#### `status/segmenter/object_id`
```json
{
  "object_id": "13449"
}
```

#### `status/segmenter/metric`
```json
{
  "name": "01_13_28_232066_0",
  "metadata": {
      "label": 0, "width": 29, "height": 80, ....
}
```