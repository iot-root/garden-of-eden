import { CaptureSensors, GetLogs } from "@/endpoints/logs"
import { parseLogs } from "@/libs/parsers"
import { H1 } from "@/typography/heading"
import { createEffect, createResource, createSignal } from "solid-js"
import Padding from "../containers/padding"
import { LogView } from "../dataviews/log-view"
import { Add } from "../ui/add"

export const Logs = () => {
    const [pumpStatsLogs] = createResource(async () => await GetLogs("pump/stats"))

    let [pumpStats, setPumpStats] = createSignal()

    createEffect(() => {
        if (pumpStatsLogs()) {
            setPumpStats(parseLogs(pumpStatsLogs()))
        }
    }, [pumpStatsLogs])

    const handleOnClick = async () => {
        await CaptureSensors()
    }

    return (
        <Padding>
            <div class="flex flex-row justify-between items-center mb-4">
                <H1 >Log</H1>
                <button onClick={handleOnClick}>
                    <Add label="Add" />
                </button>
            </div>

            <div class="md:grid md:grid-cols-2 gap-4">
                <LogView class="" sensor="distance" field="value" title="Water Level cm" />
                <LogView class="" sensor="temperature" field="value" title={"Temperature \u00B0C"} />
                <LogView class="" sensor="humidity" field="value" title={"Humidity %"} />
                <LogView class="" sensor="light" field="value" title={"Brightness %"} />
                <LogView class="" sensor="pcb-temp" field="value" title={"PCB Temp. \u00B0C"} />
                <LogView class="" sensor="pump/speed" field="value" title={"Pump Speed %"} />
                <LogView class="" sensor="pump/stats" field="power" title={"Power W"} />
                <LogView class="" sensor="pump/stats" field="bus_current" title={"Bus Current A"} />
                <LogView class="" sensor="pump/stats" field="bus_voltage" title={"Bus Voltage V"} />
                <LogView class="" sensor="pump/stats" field="shunt_voltage" title={"Shunt Voltage A"} />
            </div>
        </Padding >
    )
}