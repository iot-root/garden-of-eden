export const TurnOnLight = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/light/on`,
      {
        method: 'POST',
      }
    )

    if (!response.ok) {
      return 'Sensor not detected'
    }

    return response.json()
  } catch (e) {
    console.error('Error turning on lights: ', e)
    throw e
  }
}

export const TurnOffLight = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/light/off`,
      {
        method: 'POST',
      }
    )

    if (!response.ok) {
      return 'Sensor not detected'
    }

    return response.json()
  } catch (e) {
    console.error('Error turning off lights: ', e)
    throw e
  }
}

export const GetBrightness = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/light/brightness`
    )

    const data = await response.json()

    if (!response.ok) {
      return data
    }

    return String(data.value)
  } catch (e) {
    console.error('Error fetching brightness: ', e)
    throw e
  }
}

export const SetBrightness = async (value: string) => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/light/brightness`
    )

    if (!response.ok) {
      return 'Sensor not detected'
    }

    return response.json()
  } catch (e) {
    console.error('Error setting brightness distance: ', e)
    throw e
  }
}
