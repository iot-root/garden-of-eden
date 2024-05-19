export const GetTemp = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/temperature`
    )

    const data = await response.json()

    if (!response.ok) {
      return data
    }

    return data.temperature
  } catch (e) {
    console.error('Error fetching temperature: ', e)
    throw e
  }
}
