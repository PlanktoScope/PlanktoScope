# nodes

Custom Node-RED modules for the PlanktoScope

- https://nodered.org/docs/creating-nodes/
- https://github.com/node-red/node-red-node-test-helper/
- https://nodejs.org/docs/latest-v20.x/api/test.html
- https://nodejs.org/docs/latest-v20.x/api/assert.html

## Development

```sh
cd nodes
npm install
npm test
```

Run excotaxa:

https://github.com/ecotaxa/ecotaxa_front/tree/master/docker/all_in_one

Note:

On Fedora you need to disable SELinux with

```sh
sudo setenforce 0
```

Start node-red manually

```sh
npm run dev
```

The script will watch for changes in the `flows` directory and restart `node-red` automatically.

## Tests

Currently broken

```
node --test ecotaxa.test.js
```
