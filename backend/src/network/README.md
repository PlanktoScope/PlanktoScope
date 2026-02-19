# network service

This is an MQTT service that is started as part of `bakcend`.

### API

### list

**topic** `network/wifi/list`

**payload:**
```json
[
  {
    "ssid": "FOO",
    "frequency": 2412,
    "strength": 55,
    "path": "/org/freedesktop/NetworkManager/AccessPoint/23"
  },
  {
    "ssid": "BAR",
    "frequency": 5500,
    "strength": 75,
    "path": "/org/freedesktop/NetworkManager/AccessPoint/24"
  }
  ...
]
```

Subscribe to this topic to get the list of available access points.
The list will be automatically published to new subscribers and can be updated at any point.

See `scan` below to request an explicit update.

### scan

**topic** `network/wifi/scan`

Publish a request to this topic to have the wireless device scan for networks.
The response is emitted once the scan is done and contains no payload.

This is likely to cause an update on `network/wifi/list`.

### connect

**topic** `network/wifi/connect`

**payload:**
```json
{
  "path": "/org/freedesktop/NetworkManager/AccessPoint/24" // a path from the list of wifis
}
```

Publish a request to this topic to have the wireless device connect to the specified access point.
The response is emitted once the connection is established and contains no payload.
