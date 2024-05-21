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
import { Match, Suspense, Switch, createEffect, createResource, createSignal } from "solid-js"
export default () => {
    const [distanceData] = createResource(GetDistance);
    const [brightnessData, { refetch: refetchBrightness }] = createResource(GetBrightness);
    const [pumpSpeedData, { refetch: refetchPumpSpeed }] = createResource(GetPumpSpeed);
    const [pumpStatsData] = createResource(GetPumpStats);
    const [airTempData] = createResource(GetTemp);
    const [pcbTempData] = createResource(GetPCBTemp);
    const [humidityData] = createResource(GetHumidity);

    const [getLightState, setLightState] = createSignal()
    const [getPumpState, setPumpState] = createSignal()

    const handleLightToggle = async () => {
        if (!getLightState()) {
            try {
                await TurnOnLight()
                setLightState(!getLightState())
                refetchBrightness()
            } catch (e) {
                console.log(e)
            }
        } else {
            try {
                await TurnOffLight()
                setLightState(!getLightState())
                refetchBrightness()
            } catch (e) {
                console.log(e)
            }
        }
    }

    const handlePumpToggle = async () => {
        if (!getPumpState()) {
            try {
                await TurnOnPump()
                setPumpState(!getPumpState())
                refetchPumpSpeed()
            } catch (e) {
                console.log(e)
            }
        } else {
            try {
                await TurnOffPump()
                setPumpState(!getPumpState())
                refetchPumpSpeed()
            } catch (e) {
                console.log(e)
            }
        }
    }

    createEffect(async () => {
        // initialize lights state
        const brightness = await brightnessData()
        let isLightOn = brightness?.value > 0 ? true : false
        setLightState(isLightOn)

        // initialize pump state
        const speed = await pumpSpeedData()
        let isPumpOn = speed?.value > 0 ? true : false
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
                        <Suspense fallback={<Detail>Loading...</Detail>}>
                            <Switch>
                                <Match when={pumpStatsData()?.error}>
                                    <Detail error>{`${String(pumpStatsData()?.error).slice(0, 30)}...`}</Detail>
                                </Match>

                                <Match when={pumpStatsData()}>
                                    <Detail>{String(pumpStatsData()['Bus Current'])}</Detail>
                                </Match>
                            </Switch>
                        </Suspense>
                    </div>

                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Voltage</Detail>
                        <Suspense fallback={<Detail>Loading...</Detail>}>
                            <Switch>
                                <Match when={pumpStatsData()?.error}>
                                    <Detail error>{`${String(pumpStatsData()?.error).slice(0, 30)}...`}</Detail>
                                </Match>

                                <Match when={pumpStatsData()}>
                                    <Detail>{String(pumpStatsData()['Bus Voltage'])}</Detail>
                                </Match>
                            </Switch>
                        </Suspense>
                    </div>


                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Power</Detail>
                        <Suspense fallback={<Detail>Loading...</Detail>}>
                            <Switch>
                                <Match when={pumpStatsData()?.error}>
                                    <Detail error>{`${String(pumpStatsData()?.error).slice(0, 30)}...`}</Detail>
                                </Match>

                                <Match when={pumpStatsData()}>
                                    <Detail>{String(pumpStatsData()['Power'])}</Detail>
                                </Match>
                            </Switch>
                        </Suspense>
                    </div>


                    <div class="w-full flex justify-between mb-1">
                        <Detail class="capitalize">Shunt Voltage</Detail>
                        <Suspense fallback={<Detail>Loading...</Detail>}>
                            <Switch>
                                <Match when={pumpStatsData()?.error}>
                                    <Detail error>{`${String(pumpStatsData()?.error).slice(0, 30)}...`}</Detail>
                                </Match>

                                <Match when={pumpStatsData()}>
                                    <Detail>{String(pumpStatsData()['Shunt Voltage'])}</Detail>
                                </Match>
                            </Switch>
                        </Suspense>
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
                    <Detail error>{`${String(props.data()?.error).slice(0, 30)}...`}</Detail>
                </Match>

                <Match when={props.data()}>
                    <Detail>{String(props.data().value)}</Detail>
                </Match>
            </Switch>
        </Suspense>
    )
}