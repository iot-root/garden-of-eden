import { GetLogs } from "@/endpoints/logs"
import { H1 } from "@/typography/heading"
import { Colors, Legend, Title, Tooltip } from 'chart.js'
import Chart from 'chart.js/auto'
import { Line } from 'solid-chartjs'
import { createSignal, onMount, createResource, createEffect } from "solid-js"
import Padding from "../containers/padding"
import { Add } from "../ui/add"
import { Dot } from "../ui/dot"
import {Card} from "@/ui/card"
import {LogsGraph} from "@/components/dataviews/logs-graph"

export const Log = () => {
    const [brightnessLogs] = createResource(async () => await GetLogs("humidity"))
    // const [temperatureLogs] = createSignal(GetLogs("temperature"))
    // const [humidityLogs] = createSignal(GetLogs("humidity"))
    // const [pcbTempLogs] = createSignal(GetLogs("pcb-temp"))
    // const [pumpSpeedLogs] = createSignal(GetLogs("pump/speed"))
    // const [pumpStatsLogs] = createSignal(GetLogs("pump/stats"))
    // const [distanceLogs] = createSignal(GetLogs("distance"))
     
    return (
        <Padding>
            <div class="flex flex-row justify-between items-center mb-4">
                <H1 >Log</H1>
                <Add label="Create" />
            </div>

            <LogsGraph logs={brightnessLogs}/>

        </Padding >
    )
}