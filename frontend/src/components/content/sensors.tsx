import Padding from "@/components/containers/padding"
import { Detail, H1, H3 } from "@/components/typography/heading"
import { Card } from "@/components/ui/card"
import SensorToggle from "@/components/ui/toggle/toggle"
import data from "@/root/data.json"
import { createSignal } from "solid-js"

export default () => {
    const [getLight, setLight] = createSignal(data.sensors.lights)
    const [getPump, setPump] = createSignal(data.sensors.pump)
    const [getTemp, setTemp] = createSignal(data.sensors.temp)
    const [getHumidity, setHumidity] = createSignal(data.sensors.humidity)
    const [getWaterLvl, setWaterLvl] = createSignal(data.sensors.water)

    const [getLightState, setLightState] = createSignal(data.sensors.lights.on)
    const [getPumpState, setPumpState] = createSignal(data.sensors.pump.on)

    const handleLightToggle = () => {
        setLightState(!getLightState())
    }

    const handlePumpToggle = () => {
        setPumpState(!getPumpState())
    }

    "Returns value or the string 'failed'"
    const getValue = (sensor, prop) => {
        if (isFailed(sensor)) {
            return "failed"
        }
        return sensor[prop]
    }

    const isFailed = (sensor) => {
        return sensor.status === "failed"
    }


    return (
        <Padding>
            <H1>Sensors</H1>
            <Detail class="mb-4">Manually run. Auto-stop after 5 minutes.</Detail>
            <Card>
                {/* Lights */}
                <div class="mb-4">
                    <div class="flex justify-between">
                        <H3 class="capitalize">Lights</H3>
                        <SensorToggle checked={getLightState()} onChange={handleLightToggle} />
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Brightness</Detail>
                        <Detail isFailed={isFailed(getLight())}>{getValue(getLight(), "brightness")}</Detail>
                    </div>
                </div>

                {/* Pump */}
                <div class="mb-4">
                    <div class="flex justify-between">
                        <H3 class="capitalize">Pump</H3>
                        <SensorToggle checked={getPumpState()} onChange={handlePumpToggle} />
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Speed</Detail>
                        <Detail isFailed={isFailed(getPump())}>{getValue(getPump(), "speed")}</Detail>
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Current</Detail>
                        <Detail isFailed={isFailed(getPump())}>{getValue(getPump(), "current")}</Detail>
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Voltage</Detail>
                        <Detail isFailed={isFailed(getPump())}>{getValue(getPump(), "voltage")}</Detail>
                    </div>
                </div>

                {/* Temp */}
                <div class="mb-4">
                    <div class="flex justify-between">
                        <H3 class="capitalize">Temperature</H3>
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Air</Detail>
                        <Detail isFailed={isFailed(getTemp())}>{getValue(getTemp(), "air")}</Detail>
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">PCB</Detail>
                        <Detail isFailed={isFailed(getTemp())}>{getValue(getTemp(), "pcb")}</Detail>
                    </div>
                </div>

                {/* Humidity */}
                <div class="mb-4">
                    <div class="flex justify-between">
                        <H3 class="capitalize">Humidity</H3>
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Air</Detail>
                        <Detail isFailed={isFailed(getHumidity())}>{getValue(getHumidity(), "air")}</Detail>
                    </div>
                </div>

                {/* Water */}
                <div class="mb-4">
                    <div class="flex justify-between">
                        <H3 class="capitalize">Water</H3>
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Level</Detail>
                        <Detail isFailed={isFailed(getWaterLvl())}>{getValue(getWaterLvl(), "level")}</Detail>
                    </div>
                </div>

            </Card>
        </Padding>
    )
}