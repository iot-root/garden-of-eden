export const TurnOnLight = async () => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/light/on`, {
        method: 'POST'
    })
}

export const TurnOffLight = async () => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/light/off`, {
        method: 'POST'
    })
}

export const GetBrightness = async () => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/light/brightness`)
}

export const SetBrightness = async (value: string) => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/light/brightness`, {
        method: 'POST',
        body: JSON.stringify({
            value
        })
    })
}