import "@picocss/pico/css/pico.blue.css"

import { useActionState, useEffect, useState } from "react"

async function readEEPROM() {
    const res = await fetch("http://pkscope-wax-ornament-42816:3001/api/eeprom")
    if (!res.ok) {
        throw new Error("Could not fetch")
    }
    return res.json()
}

async function writeEEPROM(EEPROM) {
    const res = await fetch({
        url: "http://pkscope-wax-ornament-42816:3001/api/eeprom",
        body: JSON.stringify(EEPROM),
        headers: {
            "Content-Type": "application/json",
        },
    })
    if (!res.ok) {
        throw new Error("Could not fetch")
    }
    return res.json()
}

export function App() {
    const [EEPROM, setEEPROM] = useState({
        product_uuid: "",
        product_id: "",
        product_ver: "",
        vendor: "",
        product: "",
        current_supply: "",
        dt_blob: "",
        custom_data: {
            unit: "",
        },
    })

    useEffect(() => {
        let ignore = false
        readEEPROM().then((result) => {
            if (!ignore) {
                setEEPROM(result)
            }
        })
        return () => {
            ignore = true
        }
    }, [])

    const disabled = false

    const [error, submitAction, isPending] = useActionState(
        async (previousState, formData) => {
            const data = Object.fromEntries(formData.entries())

            data.custom_data = {
                unit: data.unit,
            }
            delete data.unit

            await writeEEPROM(data)

            // const error = await updateName(formData.get("name"))
            // if (error) {
            // return error
            // }
            // redirect("/path")
            return null
        },
        null,
    )

    return (
        <>
            <header>
                <h1>PlanktoScope</h1>
            </header>
            <main>
                <form action={submitAction}>
                    <fieldset>
                        <div className="grid">
                            <div>
                                <label>
                                    product_uuid
                                    <input
                                        name="product_uuid"
                                        disabled={disabled}
                                        defaultValue={EEPROM?.product_uuid}
                                    />
                                </label>
                                <label>
                                    product_id
                                    <input
                                        name="product_id"
                                        disabled={disabled}
                                        defaultValue={EEPROM?.product_id}
                                    />
                                </label>
                                <label>
                                    product_ver
                                    <input
                                        name="product_ver"
                                        disabled={disabled}
                                        defaultValue={EEPROM?.product_ver}
                                    />
                                </label>
                                <label>
                                    vendor
                                    <input
                                        name="vendor"
                                        disabled={disabled}
                                        defaultValue={EEPROM.vendor}
                                    />
                                </label>
                            </div>
                            <div>
                                <label>
                                    product
                                    <input
                                        name="product"
                                        readOnly={disabled}
                                        defaultValue={EEPROM.product}
                                    />
                                </label>
                                <label>
                                    current_supply
                                    <input
                                        name="current_supply"
                                        type="number"
                                        disabled={disabled}
                                        defaultValue={EEPROM.current_supply}
                                    />
                                </label>
                                <label>
                                    dt_blob
                                    <input
                                        name="dt_blob"
                                        disabled={disabled}
                                        defaultValue={EEPROM.dt_blob}
                                    />
                                </label>
                                <label>
                                    unit
                                    <input
                                        name="unit"
                                        disabled={disabled}
                                        defaultValue={EEPROM.custom_data?.unit}
                                    />
                                </label>
                            </div>
                        </div>
                    </fieldset>

                    <button
                        type="submit"
                        disabled={isPending}
                        aria-busy={isPending}
                    >
                        Save
                    </button>
                </form>
            </main>
            <footer>
                Made with ❤️ by <a href="https://fairscope.com/">FairScope</a>{" "}
                in Bretagne
            </footer>
        </>
        // <main className="container">
        //   <h1>Parcel React App</h1>
        //   <p>
        //     Edit <code>src/App.tsx</code> to get started!
        //   </p>
        // </main>
    )
}
