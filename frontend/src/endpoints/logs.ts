export const GetLogs = async (sensor: string) => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/${sensor}/logs`
    )

    if (!response.ok) {
      const errorData = await response.text()
      console.error('Error fetching logs:', errorData)
      return { error: errorData }
    }

    const blob = await response.blob()
    const text = await blob.text()
    return text
  } catch (e) {
    console.error('Error setting brightness distance: ', e)
    return e
  }
}

export const CaptureSensors = async () => {
  try {
    let response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/log`,
      {
        method: 'POST',
      }
    )

    response = await response.json()

    if (!response.ok) {
      return { error: 'Error fetching logs' }
    }

    return response
  } catch (e) {
    console.error('Error setting brightness distance: ', e)
    return e
  }
}
