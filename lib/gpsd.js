// https://gpsd.gitlab.io/gpsd/gpsd_json.html
// https://gpsd.gitlab.io/gpsd/client-howto.html

import { Duplex } from "node:stream"
import net from "node:net"
import EventEmitter from "node:events"

import { pEvent } from "p-event"

export class Client extends EventEmitter {
  // constructor() {}
  //

  async connect() {
    const conn = net.createConnection(2947, "localhost")
    conn.on("connect", () => {
      const duplex = Duplex.toWeb(conn)
      this.readable = duplex.readable.pipeThrough(
        new TextDecoderStream("ascii"),
      )
      this.#read()
      this.writable = duplex.writable
    })
    conn.on("error", (err) => {
      this.emit(err)
    })
    conn.on("close", () => {})
    this.connection = conn

    return pEvent(conn, "connect")
  }

  // FIXME we need to process truncated chunks
  // > The length limit for responses and reports is currently 10240 characters, including the trailing CR-NL. Longer responses will be truncated, so client code must be prepared for the possibility of invalid JSON fragments.
  // https://gpsd.gitlab.io/gpsd/gpsd_json.html#_overview
  async #read() {
    for await (const chunk of this.readable) {
      // > Each object is terminated by a carriage return and a new line (CR-NL).
      // https://gpsd.gitlab.io/gpsd/gpsd_json.html#_core_protocol_commands
      // chunk.slice(-1) === '\n' // true

      const lines = chunk.split("\n")

      for (const line of lines) {
        if (!line) continue
        try {
          const obj = JSON.parse(line)
          this.process_response(obj)
        } catch (err) {
          this.emit("error", err)
        }
      }
    }
  }

  process_response(obj) {
    this.emit("response", obj)
    this.emit(obj.class, obj)
    this[obj.class] = obj
  }

  async disconnect() {
    await this.unwatch()
    this.connection.end()
    return pEvent(this.connection, "close")
  }

  // https://gpsd.gitlab.io/gpsd/gpsd_json.html#_core_protocol_commands
  async sendCommand(command, attributes = {}) {
    const object = { class: command, ...attributes }
    const str = `?${command}=${JSON.stringify(object)}`
    return this.write(str)
  }

  async write(str) {
    const writer = this.writable.getWriter()
    await writer.write(str)
    writer.releaseLock()
  }

  async watch(attributes) {
    await this.sendCommand("WATCH", attributes)
  }

  async unwatch() {
    await this.sendCommand("WATCH", { enable: false })
  }
}

const gpsd = new Client()
await gpsd.connect()
await gpsd.watch({ json: true })

gpsd.on("response", (response) => {
  console.log(response)
})

gpsd.on("error", (err) => {
  console.log(err)
})
