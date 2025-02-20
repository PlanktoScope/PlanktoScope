# Software Customization

Your PlanktoScope's embedded Raspberry Pi computer has a PlanktoScope-specific operating system (the *[PlanktoScope OS](../reference/software/architecture/os.md)*) with software for operating your PlanktoScope. This software can be customized in various ways, for example by downloading and enabling additional apps or by adjusting the behaviors of the provided apps.

All URLs in this guide are written assuming you access your PlanktoScope using [planktoscope.local](http://planktoscope.local) as the domain name; if you need to use a [different domain name](./index.md#access-your-planktoscopes-software) such as [home.pkscope](http://home.pkscope), you should substitute that domain name into the links on this page.

## Add supported apps

The PlanktoScope OS provides supported integration for some optional apps which are not included with the standard SD card image, in order to keep SD card image files smaller. You can download and enable these apps on a PlanktoScope which has been [configured to have internet access](./networking.md#connect-your-planktoscope-to-the-internet).

### Portainer

[Portainer](https://www.portainer.io/) is a graphical administration dashboard which provides an advanced interface for inspecting and troubleshooting running Docker containers; compared to [Dozzle](https://dozzle.dev/), which is provided by default with the PlanktoScope OS, Portainer is more powerful and much more complicated to use.

You can install and enable Portainer on a PlanktoScope with internet access by running the following commands in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> (which you should log in to with the username `pi` and the `pi` user's password, which is `copepode` by default) and then restart the PlanktoScope:

```
forklift pallet enable-deployment apps/portainer
forklift pallet stage
```

Then you will be able to access Portainer at <http://planktoscope.local/admin/portainer>. You should do this immediately after the first time you restart the PlanktoScope after enabling Portainer in order to set up an administrative account (including a username and a password) for controlling access to the Portainer interface; if you wait longer than five minutes before doing so, then Portainer will lock itself down, and you will then have to restart the PlanktoScope again and access Portainer within five minutes to set up the administrative account.

To disable Portainer, run the following commands in the Cockpit Terminal and then restart the PlanktoScope:

```
forklift pallet disable-deployment apps/portainer
forklift pallet stage --no-cache-img
```

## Customize provided apps

The apps provided by the PlanktoScope OS can be customized in various ways.

### PlanktoScope documentation site

The PlanktoScope OS includes a documentation site at <http://planktoscope.local/ps/docs/> for offline access to the project documentation. However, by default the offline copy of the documentation site excludes the hardware setup guides at <http://planktoscope.local/ps/docs/setup/hardware/>, because that section of the site includes many photographs which would significantly increase the size of the SD card images we provide for the PlanktoScope OS. You can download and the hardware setup guides to include as part of your PlanktoScope's offline copy of the documentation site while your PlanktoScope has a (perhaps temporary) connection to the internet by running the following commands in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> (which you should log in to with the username `pi` and the `pi` user's password, which is `copepode` by default) and then restart the PlanktoScope:

```
forklift pallet enable-deployment-feature apps/ps/docs full-site
forklift pallet stage
```

Then you will be able to view the hardware setup guides at <http://planktoscope.local/ps/docs/setup/hardware/>.

To revert back to hiding the hardware setup guides from the documentation site, run the following commands in the Cockpit Terminal and then restart the PlanktoScope:

```
forklift pallet disable-deployment-feature apps/ps/docs full-site
forklift pallet stage --no-cache-img
```

Note that your PlanktoScope will still have a copy of the hardware setup guides even if you hide them. If you really want to delete that copy, you can run the following command in the Cockpit Terminal:

```
docker image prune -a
```

Note that this may also delete other copies of apps which are not currently enabled - so, for example, if you [disabled Grafana](#grafana), then you will only be able to re-enable Grafana once your PlanktoScope has an internet connection to re-download Grafana, and you will need to run `forklift pallet stage` instead of `forklift pallet stage --no-cache-img` (so that Grafana will be re-downloaded).

### Segmenter

#### Consecutive mask subtraction

Since the v2024.0.0-beta.0 prerelease of PlanktoScope OS, the segmenter no longer subtracts consecutive segmentation masks from each other by default. We will eventually add a GUI toggle for this behavior; in the meantime, if you would like to re-enable this behavior by default, you can do so (even on a PlanktoScope without internet access) by running the following commands in the Cockpit Terminal and then restarting the PlanktoScope:

```
forklift plt enable-depl-feat apps/ps/backend/proc-segmenter pipeline-subtract-consecutive-masks
forklift pallet stage --no-cache-img
```

To revert back to disabling this behavior by default, run the following commands in the Cockpit Terminal and then restart the PlanktoScope:

```
forklift plt disable-depl-feat apps/ps/backend/proc-segmenter pipeline-subtract-consecutive-masks
forklift pallet stage --no-cache-img
```

## Disable provided apps

The PlanktoScope OS includes some apps which you might want to disable for some reason (e.g. as part of troubleshooting). You can disable these apps on a PlanktoScope regardless of whether it has internet access.

### Grafana

[Grafana](https://grafana.com/grafana/) is a metrics visualization dashboard which is currently used by the PlanktoScope's Node-RED dashboard to provide gauges and plots of various system metrics such as CPU temperature, RAM usage, and disk space usage. A future version of the Node-RED dashboard will replace these Grafana-based plots, after which Grafana will be disabled by default in the PlanktoScope OS. If you'd like to disable Grafana in the meantime, you can run the following commands in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> (which you should log in to with the username `pi` and the `pi` user's password, which is `copepode` by default) and then restart the PlanktoScope:

```
forklift pallet disable-deployment apps/grafana
forklift pallet stage --no-cache-img
```

To re-enable Grafana, run the following commands in the Cockpit Terminal and then restart the PlanktoScope:

```
forklift pallet enable-deployment apps/grafana
forklift pallet stage --no-cache-img
```