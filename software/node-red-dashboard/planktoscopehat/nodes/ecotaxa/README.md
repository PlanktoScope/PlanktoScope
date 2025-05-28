# node-red-contrib-ecotaxa

A work in progress ecotaxa module for Node-RED

- https://nodered.org/docs/creating-nodes/
- https://github.com/node-red/node-red-node-test-helper/
- https://nodejs.org/docs/latest-v20.x/api/test.html
- https://nodejs.org/docs/latest-v20.x/api/assert.html

## Development

Run excotaxa:

https://github.com/ecotaxa/ecotaxa_front/tree/master/docker/all_in_one

Note:

On Fedora you need to disable SELinux with

```sh
sudo setenforce 0
```

Start node-red manually

```sh
sudo systemctl stop node-red
node-red-pi --settings /home/pi/PlanktoScope/software/node-red-dashboard/settings.js
```

## Tests

Currently broken

```
node --test ecotaxa.test.js
```
