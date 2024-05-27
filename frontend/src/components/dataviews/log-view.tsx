
import { LineGraph } from "@/components/dataviews/line-graph"
import { GetLogs } from "@/endpoints/logs"
import { parseLogs } from "@/libs/parsers"
import { Match, Switch, createEffect, createResource, createSignal } from "solid-js"

export const LogView = (props) => {
    const [logs] = createResource(async () => await GetLogs(props.sensor))

    let [parsedLogs, setParsedLogs] = createSignal()

    createEffect(() => {
        if (logs()) {
            setParsedLogs(parseLogs(logs()))
        }
    }, [logs])

    return (
        <div class={props.class}>
            <Switch>
                <Match when={parsedLogs()}>
                    <LineGraph data={parsedLogs()[props.field]} labels={parsedLogs().timestamp} title={props.title} />
                </Match>
            </Switch>
        </div>
    )
}