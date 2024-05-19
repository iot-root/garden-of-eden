import Padding from "@/components/containers/padding"
import { Detail, H1, H3 } from "@/components/typography/heading"
import { Card } from "@/components/ui/card"
import SensorToggle from "@/components/ui/toggle/toggle"
import { GetDistance } from "@/endpoints/distance"
import { GetHumidity } from "@/endpoints/humidity"
import { GetBrightness, TurnOffLight, TurnOnLight } from "@/endpoints/light"
import { GetPCBTemp } from "@/endpoints/pcb-temp"
import { GetPumpSpeed, GetPumpStats, TurnOffPump, TurnOnPump } from "@/endpoints/pump"
import { GetTemp } from "@/endpoints/temperature"
import data from "@/root/data.json"
import { Match, Suspense, Switch, createEffect, createResource, createSignal } from "solid-js"
export default () => {
    const [distanceData] = createResource(GetDistance);
    const [brightnessData, { refetch: refetchBrightness }] = createResource(GetBrightness);
    const [pumpSpeedData, { refetch: refetchPumpSpeed }] = createResource(GetPumpSpeed);
    const [pumpStatsData] = createResource(GetPumpStats);
    const [airTempData] = createResource(GetTemp);
    const [pcbTempData] = createResource(GetPCBTemp);
    const [humidityData] = createResource(GetHumidity);


    const [getPump, setPump] = createSignal(data.sensors.pump)
    const [getTemp, setTemp] = createSignal(data.sensors.temp)
    const [getHumidity, setHumidity] = createSignal(data.sensors.humidity)
    const [getWaterLvl, setWaterLvl] = createSignal(data.sensors.water)

    const [getLightState, setLightState] = createSignal()
    const [getPumpState, setPumpState] = createSignal(data.sensors.pump.on)

    const handleLightToggle = async () => {
        setLightState(!getLightState())

        if (getLightState()) {
            try {
                await TurnOnLight()
                refetchBrightness()
            } catch (e) {
                console.log(e)
            }
        } else {
            try {
                await TurnOffLight()
                refetchBrightness()
            } catch (e) {
                console.log(e)
            }
        }
    }

    const handlePumpToggle = async () => {
        setPumpState(!getPumpState())

        if (getPumpState()) {
            try {
                await TurnOnPump()
                refetchPumpSpeed()
            } catch (e) {
                console.log(e)
            }
        } else {
            try {
                await TurnOffPump()
                refetchPumpSpeed()
            } catch (e) {
                console.log(e)
            }
        }
    }

    const getValue = (sensor, prop) => {
        if (isFailed(sensor)) {
            return "failed"
        }
        return sensor[prop]
    }

    const isFailed = (sensor) => {
        return sensor.status === "failed"
    }

    createEffect(async () => {
        // initialize lights state
        const brightness = await GetBrightness()
        let isLightOn = brightness > 0 ? true : false
        setLightState(isLightOn)

        // initialize pump state
        const speed = await GetPumpSpeed()
        let isPumpOn = speed > 0 ? true : false
        setPumpState(isPumpOn)
    }, [])


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
                        <AsyncDataPoint data={brightnessData} />
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
                        <AsyncDataPoint data={pumpSpeedData} />
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Current</Detail>
                        <AsyncDataPoint data={pumpStatsData.current} />
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Voltage</Detail>
                        <AsyncDataPoint data={pumpStatsData.voltage} />
                    </div>
                </div>

                {/* Temp */}
                <div class="mb-4">
                    <div class="flex justify-between">
                        <H3 class="capitalize">Temperature</H3>
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Air</Detail>
                        <AsyncDataPoint data={airTempData} />
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">PCB</Detail>
                        <AsyncDataPoint data={pcbTempData} />
                    </div>
                </div>

                {/* Humidity */}
                <div class="mb-4">
                    <div class="flex justify-between">
                        <H3 class="capitalize">Humidity</H3>
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Air</Detail>
                        <AsyncDataPoint data={humidityData} />
                    </div>
                </div>

                {/* Water */}
                <div class="mb-4">
                    <div class="flex justify-between">
                        <H3 class="capitalize">Water</H3>
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Level</Detail>
                        <AsyncDataPoint data={distanceData} />
                    </div>
                </div>

            </Card>
        </Padding>
    )
}

const AsyncDataPoint = (props) => {
    return (
        <Suspense fallback={<Detail>Loading...</Detail>}>
            <Switch>
                <Match when={props.data()?.error}>
                    <Detail>Sensor not detected</Detail>
                </Match>

                <Match when={props.data()}>
                    <Detail>{props.data()}</Detail>
                </Match>
            </Switch>
        </Suspense>
    )
}