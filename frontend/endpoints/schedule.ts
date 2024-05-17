export const addSchedule = async (sensor, body) => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/${sensor}/schedule/add`, {
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

export const deleteAllSchedules = async () => {
    await fetch(`http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/schedule/delete-all`, {
        method: 'POST',
    })
}


