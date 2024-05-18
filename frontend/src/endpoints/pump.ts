export const TurnOnPump = async () => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pump/on`, {
        method: 'POST'
    })
}

export const TurnOffPump = async () => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pump/off`, {
        method: 'POST'
    })
}

export const GetPumpSpeed = async () => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pump/speed`)
}

export const SetPumpSpeed = async (value: number) => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pump/speed`, {
        method: 'POST',
        body: JSON.stringify({
            value
        })
    })
}

export const GetPumpStats = async () => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/pump/stats`)
}