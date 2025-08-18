function useTopic(topic) {
  const [state, setState] = useState()

  const update = useCallback(
    async function publish(data) {
      return client.publishAsync(topic, data)
    },
    [topic],
  )

  const fetch = useCallback(
    async function publish(data) {
      return client.publishAsync(topic, data)
    },
    [topic],
  )

  useEffect(() => {
    let ignore = false

    function listener(t, message) {
      if (ignore === true) return
      if (t !== topic) return
      setState(message)
    }
    client.on("message", listener)

    subscribe(topic).catch((error) => {
      console.error(error)
    })

    return () => {
      ignore = true
      client.removeListener("message", listener)
    }
  }, [])

  return [state, update, updatePending]
}

function usePromise(promise) {
  const [pending, setPending] = useState(true)
  const [result, setResult] = useState()
  const [error, setError] = useState()

  useEffect(() => {
    let ignore = false
    promise
      .then((result) => {
        console.log(result)
        if (!ignore) setResult(result)
      })
      .catch((error) => {
        if (!ignore) setError(error)
      })
      .finally(() => {
        if (!ignore) setPending(false)
      })
    return () => {
      ignore = true
    }
  }, [])

  return [pending, error, result]
}

// function useRemoteState(name, initialState) {
//     const [result, setResult] = useState(initialState)
//     const [error, setError] = useState(null)
//     const [pending, setPending] = useState(true)

//     const update = useCallback(function update(data) {
//         request(`${name}/set`, data)
//             .then((result) => {
//                 if (!ignore) {
//                     setResult(result)
//                 }
//             })
//             .catch((error) => {
//                 if (!ignore) {
//                     setError(error)
//                 }
//             })
//             .finally(() => {
//                 setPending(false)
//             })
//     }, [])

//     useEffect(() => {
//         let ignore = false
//         request(`${name}/get`)
//             .then((result) => {
//                 if (!ignore) {
//                     setResult(result)
//                 }
//             })
//             .catch((error) => {
//                 if (!ignore) {
//                     setError(error)
//                 }
//             })
//             .finally(() => {
//                 setPending(false)
//             })
//         return () => {
//             ignore = true
//         }
//     }, [])

//     return { state: result, error, pending, update }
// }
