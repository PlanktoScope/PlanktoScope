# dashboard

This is the new [Node-RED](https://nodered.org/) project for the [PlanktoScope](https://www.planktoscope.org/).

## Setup

1. **Prepare the SD Card**

   - Download the [latest development PlanktoScope OS](https://github.com/PlanktoScope/PlanktoScope/blob/main/documentation/docs/community/contribute/tips-and-tricks.md#development-os).

   - Flash the `.img.xz` file to an SD card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/).

     - Open Raspberry Pi Imager.
     - Select **"Choose OS"** and locate the PlanktoScope image.
     - Select **"Choose Storage"** and pick your SD card.
     - Click **"Write"** to flash the image.

   - Insert the SD card into the PlanktoScope.

2. **Connect to the Local Network**

   - Use an Ethernet cable to connect the PlanktoScope to your local router.
   - Power on the PlanktoScope.

3. **Connect the PlanktoScope to Wi-Fi**

   - Once the PlanktoScope’s Wi-Fi becomes visible, use your computer or mobile device to connect it to your local router’s Wi-Fi network.

4. **Switch to the Node-RED dashboard project**

- Go to [Node-RED admin](http://planktoscope.local/admin/ps/node-red-v2/)
- In the main menu, select `Projects` → `Open` and select "dashboard"

5. **Update the dashboard project**

- In the right sidebar, open the `history` tab → `Commit History` → hit the refresh button
- If there are remote changes hit the `pull` button

[/ps/node-red-v2/dashboard/](http://planktoscope.local/ps/node-red-v2/dashboard/) to access the dashboard
[/admin/ps/node-red-v2/](http://planktoscope.local/admin/ps/node-red-v2/) to access the Node-RED editor

## Development

Before making contributions you will need to setup authentication, there are 2 methods available

<!-- TODO: Once the PlanktoScope is secured use SSH with passphrase only? -->

<details>
  <summary>Simple (Node-RED and token)</summary>

- Go to https://github.com/settings/personal-access-tokens
- `Generate new token`
- `Token name`: "PlanktoScope dashboard"
- `Resource owner`: "PlanktoScope"
- `Repository access` → `Only select repositories` select `PlanktoScope/dashboard`
- `Permissions` → `Repository permissions` → `Contents` select `Read and Write`
- Hit `Generate token`

Copy the token somehwere safe.

When using the Node-RED GUI to push changes, you will be prompted for git username and password.

Use your GitHub username and the generated token as password.

</details>

<details>
  <summary>Advanced (CLI and SSH)</summary>

See [Development Environment](https://github.com/PlanktoScope/PlanktoScope/blob/main/documentation/docs/community/contribute/tips-and-tricks.md#development-environment) then:

```sh
cd PlanktoScope/node-red/projects/dashboard
git remote set-url origin git@github.com:PlanktoScope/dashboard.git
git fetch origin
git checkout main
git pull

# use Git CLI instead of Node-RED history tab
```

</details>

## Updating PlanktoScope

If you pull changes on the dashboard project, Node-RED may complain about missing nodes.

In that case you will need to type the following commands in the PlanktoScope

```sh
cd /home/pi/PlanktoScope
git pull
sudo systemctl restart nodered
```

You can use SSH or the Cockpit terminal.

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
