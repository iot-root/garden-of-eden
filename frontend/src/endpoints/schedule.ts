export const addSchedule = async (
  sensor: string,
  body: {
    minutes: number
    hour: number
    day: number
    state?: string
    brightness?: number
    speed?: number
  }
) => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/${sensor}/schedule/add`,
      {
        method: 'POST',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' },
      }
    );

    if (!response.ok) {
      return 'Sensor not detected';
    }

    return response.json();
  } catch (e) {
    console.error('Error adding schedule: ', e);
    throw e;
  }
};

export const updateSchedule = async (
  sensor: string,
  body: {
    id: string
    minutes: number
    hour: number
    day: number
    state: string
    brightness?: number
    speed?: number
  }
) => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/${sensor}/schedule/update`,
      {
        method: 'POST',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' },
      }
    );

    if (!response.ok) {
      return 'Sensor not detected';
    }

    return response.json();
  } catch (e) {
    console.error('Error updating schedule: ', e);
    throw e;
  }
};

export const getAllSchedules = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/schedule/get-all`,
      {
        method: 'GET',
      }
    );

    if (!response.ok) {
      return 'Sensor not detected';
    }

    return response.json();
  } catch (e) {
    console.error('Error getting all schedules: ', e);
    throw e;
  }
};

export const deleteScheduleById = async (body: { id: string }) => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/schedule/delete`,
      {
        method: 'POST',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' },
      }
    );

    if (!response.ok) {
      return 'Sensor not detected';
    }

    return response.json();
  } catch (e) {
    console.error('Error deleting schedule: ', e);
    throw e;
  }
};

export const deleteAllSchedules = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/schedule/delete-all`,
      {
        method: 'POST',
      }
    );

    if (!response.ok) {
      return 'Sensor not detected';
    }

    return response.json();
  } catch (e) {
    console.error('Error deleting all schedules: ', e);
    throw e;
  }
};
