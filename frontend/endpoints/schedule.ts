export const SetSchedule = async () => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/schedule/set`, {
        method: 'POST'
    })
}
