// TODO: if response err

export const GetPCBTemp = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pcb-temp`
    )

    const data = await response.json()

    if (!response.ok) {
      return data
    }

    return data
  } catch (e) {
    console.error('Error fetching PCB Temp: ', e)
    return e
  }
}
