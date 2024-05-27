export const TurnOnPump = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pump/on`,
      {
        method: 'POST',
      }
    )

    if (!response.ok) {
      return 'Sensor not detected'
    }

    return response.json()
  } catch (e) {
    console.error('Error turning on pump: ', e)
    throw e
  }
}

export const TurnOffPump = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pump/off`,
      {
        method: 'POST',
      }
    )

    if (!response.ok) {
      return 'Sensor not detected'
    }

    return response.json()
  } catch (e) {
    console.error('Error turning off pump: ', e)
    throw e
  }
}

export const GetPumpSpeed = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pump/speed`
    )

    const data = await response.json()

    if (!response.ok) {
      return data
    }

    return data
  } catch (e) {
    console.error('Error fetching pump speed: ', e)
    throw e
  }
}

export const SetPumpSpeed = async (value: number) => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pump/speed`,
      {
        method: 'POST',
        body: JSON.stringify({
          value,
        }),
      }
    )

    if (!response.ok) {
      return 'Sensor not detected'
    }

    return response.json()
  } catch (e) {
    console.error('Error setting pump speed: ', e)
    throw e
  }
}

export const GetPumpStats = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pump/stats`
    )

    const data = await response.json()

    if (!response.ok) {
      return data.data
    }

    return data.data
  } catch (e) {
    console.error('Error fetching pump stats: ', e)
    throw e
  }
}

export const GetSpeedLogs = async (value: string) => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pump/speed/logs`,
      )

   const data = await response.json()

    if (!response.ok) {
      return data
    }
    
    return data
  } catch (e) {
    console.error('Error setting brightness distance: ', e)
    throw e
  }
}

export const GetStatsLogs = async (value: string) => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pump/stats/logs`,
      )

   const data = await response.json()

    if (!response.ok) {
      return data
    }
    
    return data
  } catch (e) {
    console.error('Error setting brightness distance: ', e)
    throw e
  }
}

