export const GetDistance = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/distance`
    )

    const data = await response.json()

    if (!response.ok) {
      return data
    }

    return data
  } catch (e) {
    console.error('Error fetching distance: ', e)
    throw e
  }
}

