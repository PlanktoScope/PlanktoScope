import "./HomeText.css";

export function HomeText({ name, hostname }) {
  return (
    <main>
      <section className="section content">
        <div className="container">
          <h1>PlanktoScope {name}</h1>
          <p>
            Welcome! This is the home page for your PlanktoScope with machine
            name
            <code>{name}</code>.
          </p>
          <p>
            Below you can find a list of links to browser applications provided
            by your PlanktoScope, documentation for operating your PlanktoScope,
            and other information to help you use your PlanktoScope.
          </p>

          {!hostname.endsWith(".local") ? (
            <article className="message is-warning">
              <div className="message-body">
                Note: you are using the hostname <code>{hostname}</code>, which
                might not work outside of direct connections to the PlanktoScope
                through its Wi-Fi hotspot or through an Ethernet cable. If/when
                you want to connect to the PlanktoScope through a Wi-Fi router
                or Ethernet router (for example because you have connected your
                PlanktoScope to the internet through an external Wi-Fi network,
                which disables the PlanktoScope's Wi-Fi hotspot), you may
                instead need to use{` `}
                <a href={`//pkscope-${name}.local`}>pkscope-{name}.local</a>
                {` `}to access this PlanktoScope (though{` `}
                <a href="//planktoscope.local">planktoscope.local</a>
                {` `}should also work if no other PlanktoScopes are connected to
                the router).
              </div>
            </article>
          ) : (
            !hostname.startsWith("pkscope-") && (
              <article className="message is-info">
                <div className="message-body">
                  Note: you are using the hostname <code>{hostname}</code>,
                  which will be ambiguous if/when you are potentially connected
                  (either directly or indirectly) to multiple PlanktoScopes. In
                  such situations, you will instead need to use{` `}
                  <a href={`//pkscope-${name}.local`}>pkscope-{name}.local</a>
                  {` `}to access this PlanktoScope.
                </div>
              </article>
            )
          )}

          <h2>Browser applications</h2>
          <p>PlanktoScope operation:</p>
          <ul>
            <li>
              <strong>
                <a href="/ps/node-red-v2/ui/" target="_blank">
                  Node-RED dashboard
                </a>
              </strong>
              : Provides the standard user interface to operate the PlanktoScope
            </li>
            <li>
              <strong>
                <a href="/ps/data/browse/" target="_blank">
                  Dataset file manager
                </a>
              </strong>
              : Provides a file browsing and management interface for the
              datasets collected by the PlanktoScope
            </li>
          </ul>
          <p>System administration and troubleshooting:</p>
          <ul>
            <li>
              <strong>
                <a href="/admin/ps/device-backend-logs/browse/" target="_blank">
                  Backend logs file manager
                </a>
              </strong>
              : Provides a file browsing and management interface for the
              PlanktoScope device backend's logs
            </li>
          </ul>

          <h2>Need help?</h2>

          <h3 className="is-size-5">Wrong PlanktoScope?</h3>
          <p>
            This PlanktoScope has machine name <code>{name}</code>. If you're
            looking for a different PlanktoScope:
          </p>
          <ul>
            <li>
              You should use your web browser to open that PlanktoScope's
              machine-specific URL instead.
              {hostname.endsWith(".pkscope") ? (
                <>
                  For example, the machine-specific URL for this PlanktoScope is
                  <a href={`//${name}.pkscope`}>{name}.pkscope</a>.
                  Alternatively,
                  <a href={`//pkscope-${name}.local`}>pkscope-{name}.local</a>
                  might also work if your web browser supports mDNS.
                </>
              ) : (
                hostname.endsWith(".local") && (
                  <>
                    {" "}
                    For example, the machine-specific URL for this PlanktoScope
                    is
                    <a href={`//pkscope-${name}.local`}>pkscope-{name}.local</a>
                    . Alternatively,
                    <a href={`//${name}.pkscope`}>{name}.pkscope</a>
                    might also work if you're connecting directly to your
                    PlanktoScope (i.e. to its Ethernet port or to a Wi-Fi
                    network created by your PlanktoScope) and your web browser
                    isn't using Private DNS to look up domain names.
                  </>
                )
              )}
            </li>
            <li>
              {hostname.endsWith(".pkscope") ? (
                <>
                  You're probably trying to connect directly to your
                  PlanktoScope (i.e. to its Ethernet port or to a Wi-Fi network
                  created by that PlanktoScope). You
                </>
              ) : (
                <>
                  If you're trying to connect directly to a different
                  PlanktoScope (i.e. to its Ethernet port or to a Wi-Fi network
                  created by that PlanktoScope), you
                </>
              )}
              might need to change your network configuration in order to
              connect to that PlanktoScope's Wi-Fi network or Ethernet port, and
              you might also need to disconnect from{` `}
              <code>{name}</code>'s Wi-Fi network or Ethernet port.
            </li>
          </ul>

          <h3 className="is-size-5">Documentation</h3>
          <p>Accessible offline:</p>
          <ul>
            <li>
              <strong>
                <a href="/ps/docs/" target="_blank">
                  Official PlanktoScope documentation
                </a>
              </strong>
              : Provides an offline copy of the official PlanktoScope project
              documentation
            </li>
            <li>
              <strong>
                <a href="/ps/docs/operation/protocol-v4.pdf" target="_blank">
                  Protocol for plankton imaging, v4
                </a>
              </strong>
              : Provides an offline copy of version 4 of the protocol for
              quantifying plankton diversity using the official PlanktoScope
              hardware (versions v2.5 - v2.6) and the official PlanktoScope
              software (version v2024.0)
            </li>
          </ul>
          <p>On the internet:</p>
          <ul>
            <li>
              <strong>
                <a href="https://docs.planktoscope.community" target="_blank">
                  PlanktoScope project documentation
                </a>
              </strong>
              : Provides the latest version of the PlanktoScope project
              documentation
            </li>
            <li>
              <strong>
                <a
                  href="https://www.protocols.io/view/planktoscope-protocol-for-plankton-imaging-bp2l6bq3zgqe"
                  target="_blank"
                >
                  Protocol for plankton imaging
                </a>
              </strong>
              : Provides the latest version of the protocol for quantifying
              plankton diversity using the official PlanktoScope hardware and
              software
            </li>
          </ul>

          <h3 className="is-size-5">Community</h3>
          <ul>
            <li>
              <strong>
                <a href="https://www.planktoscope.org" target="_blank">
                  Official PlanktoScope website
                </a>
              </strong>
              : Provides information about the PlanktoScope project and about
              how to get involved in the PlanktoScope community
            </li>
            <li>
              <strong>
                <a href="https://planktoscope.slack.com" target="_blank">
                  PlanktoScope on Slack
                </a>
              </strong>
              : Hosts the community for people building, using, and improving
              PlanktoScopes
            </li>
            <li>
              <strong>
                <a href="https://www.planktoscope.org/join" target="_blank">
                  PlanktoScope Slack registration form
                </a>
              </strong>
              : Provides a registration form to join the PlanktoScope community
              on Slack
            </li>
            <li>
              <strong>
                <a href="https://github.com/PlanktoScope" target="_blank">
                  PlanktoScope on GitHub
                </a>
              </strong>
              : Hosts the community for developing and maintaining the
              PlanktoScope's software and hardware
            </li>
            <li>
              <strong>
                <a href="https://www.fairscope.co/" target="_blank">
                  FairScope
                </a>
              </strong>
              : Provides preassembled PlanktoScopes, PlanktoScope hardware kits,
              and paid support services for operating PlanktoScopes - from the
              inventor of the PlanktoScope
            </li>
          </ul>

          <h2>For advanced users</h2>

          <h3 className="is-size-5">Browser applications</h3>
          <p>System administration and troubleshooting:</p>
          <ul>
            <li>
              <strong>
                <a href="/admin/cockpit/" target="_blank">
                  Cockpit
                </a>
              </strong>
              : Provides a general-purpose system administration dashboard for
              the computer embedded in the PlanktoScope
            </li>
            <li>
              <strong>
                <a href="/admin/fs/" target="_blank">
                  System file manager
                </a>
              </strong>
              : Provides a file browsing and management interface for the entire
              filesystem of the computer embedded in the PlanktoScope
            </li>
            <li>
              <strong>
                <a href="/admin/dozzle/" target="_blank">
                  Dozzle
                </a>
              </strong>
              : Provides a Docker container log viewer
            </li>
            <li>
              <strong>
                <a href="/admin/grafana/" target="_blank">
                  Grafana
                </a>
              </strong>
              : Provides a graphical dashboard for monitoring system and
              application metrics
            </li>
            <li>
              <strong>
                <a href="/admin/fs/files/run/mac-addresses.yml" target="_blank">
                  MAC address viewer
                </a>
              </strong>
              : Provides an auto-generated report of the MAC addresses of all
              network interfaces in the PlanktoScope, updated every few minutes
            </li>
          </ul>
          <p>Software development:</p>
          <ul>
            <li>
              <strong>
                <a href="/admin/ps/node-red-v2/" target="_blank">
                  Node-RED dashboard editor
                </a>
              </strong>
              : Provides a Node-RED flow editor to modify the Node-RED dashboard
            </li>
          </ul>
          <p>System recovery:</p>
          <ul>
            <li>
              <strong>
                <a href={`//${hostname}:9090/admin/cockpit/`} target="_blank">
                  Cockpit (direct-access fallback)
                </a>
              </strong>
              : Provides fallback access to the Cockpit application, accessible
              even if the system's service proxy stops working
            </li>
          </ul>

          <h3 className="is-size-5">Network APIs</h3>
          <p>PlanktoScope operation:</p>
          <ul>
            <li>
              <strong>PlanktoScope hardware controller</strong>: Provides an
              MQTT service on topics under <code>/actuator</code>,{" "}
              <code>/imager</code>,<code>/status/pump</code>,{" "}
              <code>/status/focus</code>, and <code>/status/imager</code>
              for operating the PlanktoScope hardware
            </li>
            <li>
              <strong>
                <a href="/ps/hal/camera/streams/preview.mjpg" target="_blank">
                  PlanktoScope microscope camera preview
                </a>
              </strong>
              : Provides an MJPEG stream to preview the latest microscope camera
              frame
            </li>
            <li>
              <strong>PlanktoScope object segmenter</strong>: Provides an MQTT
              service on topics under <code>/segmenter</code> and
              <code>/status/segmenter</code> for operating the PlanktoScope
              object segmenter
            </li>
            <li>
              <strong>
                <a
                  href="/ps/processing/segmenter/streams/object.mjpg"
                  target="_blank"
                >
                  PlanktoScope segmented object preview
                </a>
              </strong>
              : Provides an MJPEG stream to preview the latest segmented object
            </li>
          </ul>

          <p>System administration and troubleshooting:</p>
          <ul>
            <li>
              <strong>Host metrics</strong>: Provides Prometheus metrics about
              the Raspberry Pi at <code>{hostname}:9100/metrics</code>
            </li>
          </ul>

          <h3 className="is-size-5">System infrastructure</h3>
          <p>Networking:</p>
          <ul>
            <li>
              <strong>SSH server</strong>: Provides SSH access to the
              PlanktoScope at <code>{hostname}:22</code>
            </li>
            <li>
              <strong>MQTT broker</strong>: Provides a broker for MQTT messages
              at <code>{hostname}:1883</code>
            </li>
            <li>
              <strong>Service proxy</strong>: Provides a reverse-proxy to make
              browser applications and HTTP network APIs uniformly available at
              different paths at <code>{hostname}</code>
            </li>
            <li>
              <strong>
                <a href="/" target="_blank">
                  Device portal
                </a>
              </strong>
              : Provides a landing page as a portal to the browser applications,
              network APIs, and system infrastructure on the PlanktoScope
            </li>
          </ul>

          <p>System administration and troubleshooting:</p>
          <ul>
            <li>
              <strong>
                <a href="/admin/prometheus/" target="_blank">
                  Prometheus server
                </a>
              </strong>
              : Records, aggregates, and monitors metrics
            </li>
          </ul>
        </div>
      </section>
    </main>
  );
}
