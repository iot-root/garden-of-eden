export const parseCronJob = (cronJob) => {
    const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    function getCronTime(schedule) {
        const parts = schedule.split(' ');
        const minute = parseInt(parts[0], 10);
        const hour = parseInt(parts[1], 10);
        const dayOfWeek = parseInt(parts[4], 10);

        const formattedHour = hour;
        // const formattedHour = hour % 12 === 0 ? 12 : hour % 12;
        const formattedMinute = minute < 10 ? '0' + minute : minute;
        return `${daysOfWeek[dayOfWeek]}, ${formattedHour}:${formattedMinute}`;
    }

    function parseCommand(command) {
        const cmdDetails = {
            on: command.includes('--on'),
            off: command.includes('--off'),
            brightness: command.match(/--brightness (\d+)/)?.[1],
            speed: command.match(/--speed (\d+)/)?.[1]
        };

        return {
            state: cmdDetails.on ? 'On' : 'Off',
            brightness: cmdDetails.brightness ? `Brightness: ${cmdDetails.brightness}` : '',
            speed: cmdDetails.speed ? `Speed: ${cmdDetails.speed}` : ''
        };
    }

    const readableTime = getCronTime(cronJob.schedule);
    const commandDetails = parseCommand(cronJob.command);

    return {
        id: cronJob.id,
        day: readableTime.split(',')[0],
        time: readableTime.split(', ')[1],
        state: commandDetails.state,
        details: commandDetails.brightness || commandDetails.speed
    };
};

export const parseLogs = (logs) => {
    // transform text into json
    const data = {};

    const jsonLines = [];
    const lines = logs.split('\n');

    for (const line of lines) {
        if (line.trim()) {
            try {
                const json = JSON.parse(line);
                jsonLines.push(json);
            } catch (e) {
                console.error('Error parsing JSON:', e, line);
            }
        }
    }

    // group json data by  field
    jsonLines.forEach((lines) => {
        Object.entries(lines).forEach((entry) => {
            const field = entry[0];
            const value = entry[1];
            if (data[`${field}`] !== undefined) {
                data[`${field}`].push(value);
            } else {
                data[`${field}`] = [];
                data[field].push(value);
            }
        });
    });

    return data;
};