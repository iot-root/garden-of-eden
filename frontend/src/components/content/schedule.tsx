import Padding from "@/components/containers/padding"
import { Add } from "@/components/ui/add"
import {
    Dialog,
    DialogContent,
    DialogTrigger
} from "@/components/ui/dialog"
import { getAllSchedules } from "@/endpoints/schedule"
import { Settings } from "@/icons/icons"
import { parseCronJob } from "@/root/src/libs/parsers"
import { Detail, H1, P } from "@/typography/heading"
import { Card } from "@/ui/card"
import { Match, Suspense, Switch, createResource, createSignal } from "solid-js"
import { CreateSchedule } from "../forms/create-schedule"
import { UpdateSchedule } from "../forms/update-schedule"


export const Schedule = () => {
    const [schedules, { refetch: refetchSchedules }] = createResource(getAllSchedules)
    const [openUpdateMenu, setUpdateMenu] = createSignal(false);
    const [openCreateMenu, setCreateMenu] = createSignal(false);

    console.log('Schedules data:', schedules());


    return (
        <Padding>
            <div class="flex flex-row justify-between items-center mb-4">
                <H1 class="w-min">Schedule</H1>
                <Dialog open={openCreateMenu()} onOpenChange={setCreateMenu}>
                    <DialogTrigger>
                        <Add label="Create" />
                    </DialogTrigger>

                    <DialogContent>
                        <CreateSchedule onClose={setCreateMenu} refetch={refetchSchedules}></CreateSchedule>
                    </DialogContent>
                </Dialog>
            </div>

            <Card>
                <Suspense fallback={<Detail>Loading...</Detail>}>
                    <Switch>
                        <Match when={schedules()?.error}>
                            <Detail error>{`${String(schedules()?.error).slice(0, 30)}...`}</Detail>
                        </Match>

                        <Match when={schedules()}>
                            {
                                Object.entries(schedules().jobs).length == 0 ? <Detail>No schedules.</Detail> : ""
                            }

                            {Object.entries(schedules().jobs).map((e) => {
                                return (
                                    <div class="flex flex-col items-start mb-4">
                                        {/* sensor */}
                                        <p class="capitalize font-medium">{e[0]}</p>

                                        <div class="flex flex-col justify-between w-full">

                                            {e[1].map((s) => {
                                                const j = parseCronJob(s)
                                                return (
                                                    <div class="w-full flex flex-row justify-between items-center">
                                                        <P class="text-zinc-400 text-sm">{j.day}, {j.time}, {j.state}, {j.details}</P>
                                                        <Dialog open={openUpdateMenu()} onOpenChange={setUpdateMenu} >
                                                            <DialogTrigger>
                                                                <Settings height={30} width={30} />
                                                            </DialogTrigger>

                                                            <DialogContent>
                                                                <UpdateSchedule job={j} onClose={setUpdateMenu} refetch={refetchSchedules}></UpdateSchedule>
                                                            </DialogContent>
                                                        </Dialog>

                                                    </div>
                                                )
                                            })}
                                        </div>
                                    </div>
                                )
                            })}
                        </Match>
                    </Switch>
                </Suspense>
            </Card>
        </Padding>
    )
}