export const GetDistance = async () => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/distance`)
}
