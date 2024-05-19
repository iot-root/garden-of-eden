export const GetHumidity = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/humidity`
    )

    const data = await response.json()

    if (!response.ok) {
      return data
    }

    return data.humidity
  } catch (e) {
    console.error('Error fetching humidity: ', e)
    throw e
  }
}
