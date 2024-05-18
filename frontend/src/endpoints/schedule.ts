export const addSchedule = async (sensor: string, body:  {
    minutes: number,
    hour: number,
    day: number,
    state: string,
    brightness: number,
    speed: number
}) => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/${sensor}/schedule/add`, {
        method: 'POST',
        body: JSON.stringify(body),
        headers: {"Content-Type": "application/json"},
    })
}

export const updateSchedule = async (sensor: string, body: {
    minutes: number,
    hour: number,
    day: number,
    state: string,
    brightness: number,
    speed: number
}) => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/${sensor}/schedule/update`, {
        method: 'POST',
        body: JSON.stringify(body),
        headers: {"Content-Type": "application/json"},
    })
}

export const getAllSchedules = async () => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/schedule/get-all`, {
        method: 'GET',
    })
}

export const deleteScheduleById = async (body: { id: string }) => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/schedule/delete`, {
        method: 'POST',
        body: JSON.stringify(body),
    })
}

export const deleteAllSchedules = async () => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/schedule/delete-all`, {
        method: 'POST',
    })
}


