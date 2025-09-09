# dashboard

This is the new [Node-RED](https://nodered.org/) project for the [PlanktoScope](https://www.planktoscope.org/).

On `main` it is the project used by default.

See *Building the OS* (https://github.com/PlanktoScope/PlanktoScope/blob/main/documentation/docs/community/contribute/tips-and-tricks.md#building-the-os)

## URLs

[/ps/node-red-v2/dashboard/](http://planktoscope.local/ps/node-red-v2/dashboard/) to access the dashboard
[/admin/ps/node-red-v2/](http://planktoscope.local/admin/ps/node-red-v2/) to access the Node-RED editor

## Read and Write Data in global.json

Data is stored in a file located at: [`/home/pi/PlanktoScope/node-red/context/global/global.json`](http://planktoscope.local/admin/fs/files/home/pi/PlanktoScope/node-red/context/global/global.json).

### Read Data

To retrieve a value stored in this file, use the following script in a Function Node:

```javascript
// Retrieve the global variable
msg.variable = global.get("variable")
return msg
```

### Template Node to Display and Modify Data

```html
<template>
  <v-text-field
    label="My variable"
    variant="outlined"
    v-model="msg.variable"
    @update:model-value="send({ variable: msg.variable })"
  ></v-text-field>
</template>
```

### Write Data

To set a value in the file, use the following script in a Function Node:

```javascript
// Set a value in the global context
global.set("variable", msg.variable)
return msg
```
